import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)
DATABASE = 'netflix.db'


def execute_query(query, args=()):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        result = cur.execute(query, args)
        con.commit()
        return result


def get_movie_by_title(title):
    query = '''
    SELECT title, country, release_year, listed_in AS genre, description
    FROM netflix
    WHERE title LIKE ?
    ORDER BY release_year DESC
    LIMIT 1
    '''
    result = execute_query(query, (f'%{title}%',)).fetchone()
    if not result:
        return jsonify({'message': 'Movie not found'})
    keys = ['title', 'country', 'release_year', 'genre', 'description']
    return jsonify(dict(zip(keys, result)))


def get_movies_by_year_range(start_year, end_year):
    query = '''
    SELECT title, release_year
    FROM netflix
    WHERE release_year BETWEEN ? AND ?
    ORDER BY release_year DESC
    LIMIT 100
    '''
    result = execute_query(query, (start_year, end_year)).fetchall()
    if not result:
        return jsonify({'message': 'Movies not found'})
    return jsonify([dict(zip(['title', 'release_year'], row)) for row in result])


def get_movies_by_rating(rating_list):
    query = '''
    SELECT title, rating, description
    FROM netflix
    WHERE rating IN ({})
    '''.format(','.join(['?' for _ in rating_list]))
    result = execute_query(query, tuple(rating_list)).fetchall()
    if not result:
        return jsonify({'message': 'Movies not found'})
    keys = ['title', 'rating', 'description']
    return jsonify([dict(zip(keys, row)) for row in result])


def get_movies_by_genre(genre):
    query = '''
    SELECT title, description
    FROM netflix
    WHERE listed_in LIKE ?
    ORDER BY release_year DESC
    LIMIT 10
    '''
    result = execute_query(query, (f'%{genre}%',)).fetchall()
    if not result:
        return jsonify({'message': 'Movies not found'})
    keys = ['title', 'description']
    return jsonify([dict(zip(keys, row)) for row in result])


def get_movies_by_type_year_genre(movie_type, year, genre):
    query = '''
    SELECT title, description
    FROM netflix
    WHERE type = ? AND release_year = ? AND listed_in LIKE ?
    '''
    result = execute_query(query, (movie_type, year, f'%{genre}%')).fetchall()
    if not result:
        return jsonify({'message': 'Movies not found'})
    keys = ['title', 'description']
    return jsonify([dict(zip(keys, row)) for row in result])


@app.route('/movie/<title>')
def movie_by_title(title):
    return get_movie_by_title(title)


@app.route('/movie/year/<start_year>/<end_year>')
def movies_by_year_range(start_year, end_year):
    return get_movies_by_year_range(start_year, end_year)


@app.route('/movie/rating/<rating_list>')
def movies_by_rating(rating_list):
    return get_movies_by_rating(rating_list.split(','))


@app.route('/genre/<genre>')
def movies_by_genre(genre):
    return get_movies_by_genre(genre)


@app.route('/movie/type_year_genre/<movie_type>/<year>/<genre>')
def movies_by_type_year_genre(movie_type, year, genre):
    return get_movies_by_type_year_genre(movie_type, year, genre)
    

if __name__ == "__main__":
    app.run()
