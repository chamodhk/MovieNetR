from sqlalchemy import text,select
import networkx as nx 
from itertools import combinations
import matplotlib.pyplot as plt
from models.movie_models import Movie
from models.submission_models import MovieTitleLink
from models.comment_models import CommentMovieLink
from core.db_core import get_db_session

G = nx.Graph()

session = get_db_session()


sql = text(
"""
    SELECT DISTINCT(cml.comment_id),  s.submission_id
    FROM comment_movie_link cml
    JOIN comments c
    ON c.comment_id = cml.comment_id
    JOIN submissions s
    on c.parent_id = s.name
    WHERE c.parent_id IN (SELECT DISTINCT(s.name)
    FROM movie_title_links mtl
    JOIN submissions s 
    ON s.submission_id = mtl.submission_id
    WHERE s.name != "") AND c.score > 2
    ORDER BY submission_id
"""
)



results = session.execute(sql)
rows = results.fetchall()

submission_comment_dict = {}

for row in rows:
    try:
        submission_comment_dict[row[1]].append(row[0])
    except KeyError:
        submission_comment_dict[row[1]] = [row[0]]


movie_dict = {}
count = 0
for key, values in submission_comment_dict.items():

    #get the anchor movies
    stmt = (
        select(Movie.movie_name)
        .join(MovieTitleLink, Movie.id == MovieTitleLink.movie_id) 
        .where(MovieTitleLink.submission_id == key)
    )

    results = session.execute(stmt)
    anchor_movie_names = [row.movie_name for row in results]
    suggested_movies = []

    #get the suggested movies 
    for comment_id in values:
        stmt = (
            select(Movie.movie_name)
            .join(CommentMovieLink, Movie.id == CommentMovieLink.movie_id)
            .where(CommentMovieLink.comment_id == comment_id)
        )
        results = session.execute(stmt)
        for result in results:
            suggested_movies.append(result.movie_name)


    all_movies = set(anchor_movie_names + suggested_movies)

    for m1, m2 in combinations(all_movies, 2):
        if G.has_edge(m1, m2):
            G[m1][m2]["weight"] += 1
        else:
            G.add_edge(m1, m2, weight=1)

  
    
    count += 1
    print(count, end="\r\r")
    
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())
print("\n")

plt.figure(figsize=(20, 20))


print("saving the network to a gexf file....")
nx.write_gexf(G, "./network/movie_net.gexf")

print("saving completed!")



