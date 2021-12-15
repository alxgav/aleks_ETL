from typing import Optional, List, Union
from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str
    name: str = None


class Genre(BaseModel):
    id: str
    name: str = None


class Filmwork(BaseModel):
    id: str


class ElasticRecords(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genre: Optional[List[str]]
    title: str
    description: Union[str, None] = ""
    director: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Person]] = []
    writers: Optional[List[Person]] = []
