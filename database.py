from typing import List, Any, Tuple
import cx_Oracle


def sql_exec(con: cx_Oracle.Connection, sql_text: str, **kwargs) -> list[tuple[Any, Any]]:
    try:
        print(f"executing query: {sql_text: <20}")
        cur = con.execute(sql_text)
        descriptions = list()
        for column in cur.description:
            descriptions.append(column[0])
        rows = cur.fetchall()
        data: list[tuple[Any, Any]] = list(zip(descriptions, rows))
        return data
    except cx_Oracle.DatabaseError as err:
        error_obj, = err.args
        print(f"database error {error_obj.message}")
    finally:
        cur.close()
        print("cursor closed!")


class Database:
    def __init__(self, username: str, password: str, alias: str):
        self.username = username
        self.password = password
        self.dbname = alias

    def connect(self, alias: str) -> cx_Oracle.Connection:
        if alias:
            return cx_Oracle.connect(self.username, self.password, alias, encoding="UTF-8")
