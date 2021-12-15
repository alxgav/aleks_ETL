import logging
from typing import List, Any

import psycopg2


def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row


class LoadDatabase:

    def __init__(self, connection):
        try:
            self.connection = connection
        except (Exception, psycopg2.DatabaseError) as error:
            logging.info("Error connection to database : {}".format(error))

    def get_data(self, sql: str, limit: int, var: Any) -> List:
        data = []
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, (var,))
            for row in iter_row(cursor, limit):
                data.append(row)
        except psycopg2.DatabaseError as error:
            logging.info("Error execute sql  : {}".format(error))
        finally:
            cursor.close()
            return data
