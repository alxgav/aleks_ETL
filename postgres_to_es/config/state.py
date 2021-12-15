import abc
from abc import ABC
from typing import Any, Optional
import json
import os.path


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        file_path = self.file_path
        if state is not None:
            json.dump(state, open(file_path, 'w'), indent=4)

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        file_path = self.file_path
        return json.load(open(file_path))


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        if not os.path.exists(file_path):
            file_data = open(file_path, 'w')
            file_data.close()


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        data = self.storage.retrieve_state()
        data[key] = value
        self.storage.save_state(data)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        try:
            return self.storage.retrieve_state()[key]
        except:
            return None
