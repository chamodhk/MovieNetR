"""Extract suggested movie titles from relevant Reddit comments.

This stage expects stages 01-03 to have populated ``submissions``, ``comments``,
``movies``, and ``movie_title_links``. It creates the ``comment_movie_link``
records consumed by stage 06.

The script is safe to restart: comments that already have at least one movie
link are skipped. Use ``--start-after`` to avoid rechecking an already scanned
range that contained comments where no movie was detected.
"""

import argparse

from sqlalchemy import exists, select

from core.db_core import get_db_session
from core.entity_recognition import get_movies
from models.comment_models import Comment, CommentMovieLink
from models.movie_models import Movie
from models.submission_models import MovieTitleLink, Submission


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract movie suggestions from qualifying Reddit comments."
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--min-score",
        type=int,
        default=2,
        help="Only process comments with a score greater than this (default: 2).",
    )
    parser.add_argument("--commit-every", type=int, default=100)
    parser.add_argument("--max-chars", type=int, default=5000)
    parser.add_argument("--start-after", type=int, default=0)
    parser.add_argument(
        "--limit", type=int, help="Process at most this many comments for a test run."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not 0 <= args.threshold <= 1:
        raise ValueError("--threshold must be between 0 and 1")
    if args.commit_every < 1:
        raise ValueError("--commit-every must be at least 1")
    if args.max_chars < 1:
        raise ValueError("--max-chars must be at least 1")

    session = get_db_session()

    # This cache avoids one database query for every entity the model finds.
    # setdefault keeps the oldest ID if an earlier run created duplicate names.
    movie_ids = {}
    for movie_id, movie_name in session.execute(
        select(Movie.id, Movie.movie_name).order_by(Movie.id)
    ):
        movie_ids.setdefault(movie_name, movie_id)

    already_linked = exists().where(
        CommentMovieLink.comment_id == Comment.comment_id
    )

    # Stage 06 consumes direct comments on submissions with anchor movies and
    # requires score > 2. Applying the criteria here avoids running GLiNER over
    # millions of comments that cannot contribute to the final graph.
    stmt = (
        select(Comment)
        .join(Submission, Comment.parent_id == Submission.name)
        .join(
            MovieTitleLink,
            MovieTitleLink.submission_id == Submission.submission_id,
        )
        .where(
            Comment.comment_id > args.start_after,
            Comment.score > args.min_score,
            Comment.body.is_not(None),
            Comment.body.notin_(["", "[deleted]", "[removed]"]),
            ~already_linked,
        )
        .distinct()
        .order_by(Comment.comment_id)
    )

    if args.limit is not None:
        stmt = stmt.limit(args.limit)

    processed = 0
    linked_comments = 0
    links_created = 0
    last_comment_id = args.start_after

    try:
        for comment in session.execute(stmt).scalars().yield_per(100):
            last_comment_id = comment.comment_id
            movie_names = get_movies(
                comment.body[: args.max_chars], threshold=args.threshold
            )

            if movie_names:
                linked_comments += 1

            for movie_name in movie_names:
                movie_id = movie_ids.get(movie_name)

                if movie_id is None:
                    movie = Movie(movie_name=movie_name)
                    session.add(movie)
                    session.flush()
                    movie_id = movie.id
                    movie_ids[movie_name] = movie_id

                session.add(
                    CommentMovieLink(
                        comment_id=comment.comment_id,
                        movie_id=movie_id,
                    )
                )
                links_created += 1

            processed += 1

            if processed % args.commit_every == 0:
                session.commit()
                print(
                    f"Processed {processed} comments; "
                    f"created {links_created} links; "
                    f"last comment ID {last_comment_id}",
                    end="\r",
                    flush=True,
                )

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print()
    print("Suggestion movie extraction completed!")
    print(f"Comments processed : {processed}")
    print(f"Comments with movies: {linked_comments}")
    print(f"Links created       : {links_created}")
    print(f"Last comment ID     : {last_comment_id}")


if __name__ == "__main__":
    main()
