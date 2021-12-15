from typing import Optional, List
from pydantic import BaseModel


class DSNSettings(BaseModel):
    host: str
    port: int
    dbname: str
    password: str
    user: str


class ESSetting(BaseModel):
    host: str
    index: str


class MoviesSettings(BaseModel):
    dsn: DSNSettings
    es: ESSetting
    sql_query_person: str
    sql_query_genre: str
    sql_query_fw: str
    sql_query_genre_film_work: str
    sql_query_person_film_work: str
    sql_result: str


class Config(BaseModel):
    film_work_setting: MoviesSettings
