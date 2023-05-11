from flask import Flask, request, redirect, session
import sqlite3
import json
from collections import Counter


def main():
    app = Flask(__name__)

    def db_connect(db, query):
        """Connect to db for data selection"""
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    @app.route('/movie/title/')
    def search_title():
        if request.method == 'GET':
            response = {}
            title = request.args.get('title')
            if title:
                query = f"SELECT title, country, release_year, listed_in, description FROM netflix " \
                        f"WHERE title = '{title}' " \
                        f"ORDER BY release_year DESC " \
                        f"LIMIT 1"
                result = db_connect('netflix.db', query)
                if len(result):
                    response = {
                        "title": result[0][0],
                        "country": result[0][1],
                        "release_year": result[0][2],
                        "genre": result[0][3],
                        "description": result[0][4]
                    }
        return json.dumps(response)

    @app.route('/movie/year/')
    def search_year():
        if request.method == 'GET':
            response = []
            start_year = request.args.get('start_year')
            end_year = request.args.get('end_year')
            if start_year and end_year:
                query = f"SELECT title, release_year FROM netflix " \
                        f"WHERE release_year BETWEEN {start_year} AND {end_year} " \
                        f"LIMIT 100"
                result = db_connect('netflix.db', query)
                for line in result:
                    line_dict = {
                        "title": line[0],
                        "release_year": line[1]
                    }
                    response.append(line_dict)
        return json.dumps(response)

    def get_rating(data_rating):
        response = []
        rating = data_rating.join(",")
        query = f"SELECT title, rating, description FROM netflix WHERE rating IN ({rating})"
        result = db_connect('netflix.db', query)
        for line in result:
            line_dict = {
                "title": line[0],
                "rating": line[1],
                "description": line[2]
            }
            response.append(line_dict)
        return response

    @app.route('/search/rating/')
    def search_rating():
        if request.method == 'GET':
            rating = request.args.get('rating')
            response = get_rating([rating])
            return json.dumps(response)

    @app.route('/rating/children/')
    def rating_children():
        response = get_rating(['G'])
        return json.dumps(response)

    @app.route('/rating/family/')
    def rating_family():
        response = get_rating(['PG', 'PG-13'])
        return json.dumps(response)

    @app.route('/rating/adult/')
    def rating_adult():
        response = get_rating(['R', 'NC-17'])
        return json.dumps(response)

    def search_genre(genre):
        query = f"SELECT title, description FROM netflix " \
                f"WHERE genre = {genre} " \
                f"ORDER BY release_year DESC " \
                f"LIMIT 10"
        result = db_connect('netflix.db', query)
        response = []
        for line in result:
            line_dict = {
                "title": line[0],
                "description": line[1]
            }
        return json.dumps(response)

    def search_pair(actor1, actor2):
        query = f"SELECT \"cast\" FROM netflix " \
                f"WHERE \"cast\" LIKE '%{actor1}%' AND \"cast\" LIKE '%{actor2}%'"
        result = db_connect('netflix.db', query)
        result_list = []
        for line in result:
            line_list = line[0].split(',')
            result_list += line_list
        counter = Counter(result_list)
        actors_list = []
        for key, value in counter.items():
            if value > 2 and key.strip() not in [actor1, actor2]:
                actors_list.append(key)
        return actors_list

    def full_search(m_type, release_year, genre):
        query = f"SELECT title, description FROM netflix " \
                f"WHERE listed_in LIKE '%{m_type}%' AND release_year = {release_year} AND listed_in LIKE '%{genre}%'"
        result = db_connect('netflix.db', query)
        response = []
        for line in result:
            line_dict = {
                "title": line[0],
                "description": line[1]
            }
        return json.dumps(response)

    app.run()


if __name__ == '__main__':
    main()
    