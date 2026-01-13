from sqlalchemy import or_, select
from models.submission_models import Submission, MovieTitleLink
from models.movie_models import Movie
from core.db_core import get_db_session
from core.entity_recognition import get_movies

session = get_db_session() 

BATCH_SIZE = 100
processed = 0



submissions = session.query(Submission).filter(
    or_(
        Submission.title.ilike("%movies like%"),
        Submission.title.ilike("%ssimilar to%")
    )
).all() 

for submission in submissions:
    if not submission.title:
        continue

    movies = get_movies(submission.title, 0.4)

    for movie_name in movies:
        movie = session.execute(
            select(Movie).where(Movie.movie_name == movie_name)
        ).scalar_one_or_none()

        if not movie:
            movie = Movie(movie_name = movie_name)
            session.add(movie)
            session.flush()

        link = MovieTitleLink(
            submission_id = submission.submission_id,
            movie_id = movie.id
        )

        session.merge(link)

    processed += 1

    if processed % BATCH_SIZE == 0:
        session.commit()
        print(f"{processed} titles processed and stored", end = "\r\r\r")

session.close()
print("Title movie extraction completed!")
print(f"{processed} titles proceseed!")



        