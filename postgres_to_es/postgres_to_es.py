import logging
import os
from datetime import datetime
from typing import List

import psycopg2
from elasticsearch import Elasticsearch, helpers
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from pydantic import ValidationError

from config.config import Config
from config.database import Person, Filmwork, ElasticRecords, Genre
from read_data import LoadDatabase
from config.state import State, JsonFileStorage

path = os.path.dirname(os.path.realpath(__file__))
config = Config.parse_file(f'{path}/config/config.json')
logging.getLogger().setLevel(logging.INFO)
es = Elasticsearch(config.film_work_setting.es.host)


def bulk_data(data):
    for films in data:
        print(films)
        actors = get_Person(films.actors)
        writers = get_Person(films.writers)
        director = ''
        if films.director:
            director = ' '.join(films.director)
        actors_names = ''
        if films.actors_names:
            actors_names = ' '.join(films.actors_names)
        writers_names = ''
        if films.writers_names:
            writers_names = ' '.join(films.writers_names)
        yield {
            "_index": config.film_work_setting.es.index,
            "id": films.id,
            "imdb_rating": films.imdb_rating,
            "genre": ' '.join(films.genre),
            "title": films.title,
            "description": films.description,
            "director": director,
            "actors_names": actors_names,
            "writers_names": writers_names,
            "actors": actors,
            "writers": writers
        }


def sql_result(load_data, data_model, single=False) -> List:
    data_result = []
    for item in load_data:
        try:
            if not single:
                data_result.append(data_model(**item))
            else:
                data_result.append(data_model(**item).id)
        except ValidationError as e:
            logging.info(dict(code=-1, msg=str(e)))
    return data_result


def get_postgres_data(pg_connection: _connection, updated_data) -> List:
    load_data = LoadDatabase(pg_connection)
    person_ids, genre_ids, film_work_ids, genre_film_work_ids, person_film_work_ids, film_result = [], [], [], [], [], []

    person_ids = sql_result(load_data.get_data(config.film_work_setting.sql_query_person, 10, updated_data),
                            Person, single=True)
    genre_ids = sql_result(load_data.get_data(config.film_work_setting.sql_query_genre, 10, updated_data),
                           Genre, single=True)
    film_work_ids = sql_result(load_data.get_data(config.film_work_setting.sql_query_fw, 10, updated_data),
                               Filmwork, single=True)
    if person_ids:
        person_film_work_ids = sql_result(
            load_data.get_data(config.film_work_setting.sql_query_person_film_work, 10, tuple(person_ids)),
            Filmwork, single=True)
    if genre_ids:
        genre_film_work_ids = sql_result(
            load_data.get_data(config.film_work_setting.sql_query_genre_film_work, 10, tuple(person_ids)),
            Filmwork, single=True)
    film_work_ids = [*film_work_ids, *person_film_work_ids, *genre_film_work_ids]
    if film_work_ids:
        film_result = sql_result(load_data.get_data(config.film_work_setting.sql_result, 10, tuple(film_work_ids)),
                                 ElasticRecords)
    return film_result


def get_Person(data: List) -> List:
    new_data = []
    if data:
        for person in data:
            if person not in new_data:
                new_data.append({'id': person.id, 'name': person.name})
        return new_data
    return []


if __name__ == '__main__':
    now = datetime.now()
    state = State(JsonFileStorage(f'{path}/config/config.json'))
    update_at = state.get_state('state')
    with psycopg2.connect(**config.film_work_setting.dsn.dict(), cursor_factory=DictCursor) as pg_conn:
        try:
            if update_at <= now.strftime('%Y-%m-%d %H:%M:%S'):
                result = bulk_data(get_postgres_data(pg_conn, update_at))
                state.set_state('state', now.strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as ex:
            state.set_state('state', now.strftime('%Y-%m-%d %H:%M:%S'))
        if result:
            helpers.bulk(es, result)
