import sqlite3
import json
from collections import Counter


def db_connect(db_name, query) -> list:    
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()

    return data


def get_movie_by_title(movie_title) -> list:   
    query = ("SELECT show_id FROM netflix "
             f"WHERE title LIKE '%{movie_title}%'"
             "AND type = 'Movie'"
             "ORDER BY release_year DESC "
             "LIMIT 1")
    data = db_connect('netflix.db', query)

    return data[0]


def get_data_by_id(movie_id) -> str:   
    query = ("SELECT title, country, release_year, listed_in, description FROM netflix "
             f"WHERE show_id = '{movie_id}'")

    data = db_connect('netflix.db', query)

    match_movie = {
        "title": data[0][0],
        "country": data[0][1],
        "release_year": data[0][2],
        "genre": data[0][3],
        "description": data[0][4].replace('\n', ''),
    }

    return json.dumps(match_movie)


def get_movies_between_years(start_year, finish_year) -> str:
    query = ("SELECT title, release_year FROM netflix "
             f"WHERE release_year BETWEEN '{start_year}' AND {finish_year} "
             "AND type = 'Movie'"
             "ORDER BY release_year DESC "
             "LIMIT 100")
    data = db_connect('netflix.db', query)

    movies_match = []

    for movie in data:
        movie_data = {
            "title": movie[0],
            "release_year": movie[1],
        }
        movies_match.append(movie_data)

    return json.dumps(movies_match)


def add_with_rating(data) -> str:
    movies_match = []

    for movie in data:
        movie_data = {
            "title": movie[0],
            "rating": movie[1],
            "description": movie[2].replace('\n', ''),
        }
        movies_match.append(movie_data)

    return json.dumps(movies_match)


def get_movie_by_rating(rating) -> str:
    if rating == "children":
        query = ("SELECT title, rating, description FROM netflix "
                 "WHERE rating = 'G' "
                 "AND type = 'Movie'"
                 "ORDER BY release_year DESC")
        data = db_connect('netflix.db', query)

        return json.dumps(add_with_rating(data))
    if rating == "family":
        query = ("SELECT title, rating, description FROM netflix "
                 "WHERE rating = 'G'"
                 "OR rating = 'PG'"
                 "OR rating = 'PG-13'"
                 "AND type = 'Movie'"
                 "ORDER BY release_year DESC")
        data = db_connect('netflix.db', query)

        return json.dumps(add_with_rating(data))
    if rating == 'adult':
        query = ("SELECT title, rating, description FROM netflix "
                 "WHERE rating = 'R' OR rating = 'NC-17'"
                 "AND type = 'Movie'"
                 "ORDER BY release_year DESC ")
        data = db_connect('netflix.db', query)

        return json.dumps(add_with_rating(data))


def get_movies_by_genre(genre) -> str:
    query = ("SELECT title, description FROM netflix "
             f"WHERE listed_in LIKE '%{genre}%' "
             "AND type = 'Movie'"
             "ORDER BY release_year DESC "
             "LIMIT 10")
    data = db_connect('netflix.db', query)

    movies_match = []

    for movie in data:
        movie_data = {
            "title": movie[0],
            "description": movie[1].replace('\n', ''),
        }
        movies_match.append(movie_data)

    return json.dumps(movies_match)


def get_cast_count(first_actor, second_actor) -> list:
    query = ("SELECT netflix.cast FROM netflix "
             f"WHERE netflix.cast LIKE '%{first_actor}%'"
             f"AND netflix.cast LIKE '%{second_actor}%'")

    data = db_connect('netflix.db', query)
    result_list = []
    for cast in data:
        cast = cast[0].split(", ")
        result_list += cast
    counter = Counter(result_list)
    actors_list = []
    for key, value in counter.items():
        if value > 2 and key.strip() not in [first_actor, second_actor]:
            actors_list.append(key)

    return actors_list


def get_uniq_movie(category, release_year, genre) -> str:
    query = ("SELECT title, description FROM netflix "
             f"WHERE release_year = '{release_year}'"
             f"AND type = '{category}'"
             f"AND listed_in = '{genre}'"
             "ORDER BY release_year DESC")

    data = db_connect('netflix.db', query)

    movies_match = []

    for movie in data:
        movie_data = {
            "title": movie[0],
            "description": movie[1].replace('\n', ''),
        }
        movies_match.append(movie_data)

    return json.dumps(movies_match)
