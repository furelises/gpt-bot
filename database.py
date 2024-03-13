import sqlite3

import config

user_subjects = {}
user_levels = {}
user_tasks = {}
user_answers = {}

class UserRow:
    def __init__(self):
        self.subject = ""
        self.level = ""
        self.task = ""
        self.answer = ""

class DB:
    def __init__(self):
        self.__create_database__()
        self.__create_table__()

    @staticmethod
    def __create_database__():
        con = sqlite3.connect(config.db_file)
        cur = con.cursor()
        con.close()

    @staticmethod
    def __create_table__():
        con = sqlite3.connect(config.db_file)
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            subject TEXT,
            level TEXT,
            task TEXT,
            answer TEXT
        );""")
        con.commit()
        con.close()

    @staticmethod
    def insert_data(user_id, subject):
        con = sqlite3.connect(config.db_file)
        cur = con.cursor()
        cur.execute("insert into users (user_id, subject) values(?,?)", (user_id, subject))
        con.commit()
        con.close()

    @staticmethod
    def update_data(user_id, column, data):
        con = sqlite3.connect(config.db_file)
        cur = con.cursor()
        cur.execute(f"update users set {column}=? where user_id=?", (data, user_id))
        con.commit()
        con.close()

    @staticmethod
    def select_data(user_id):
        con = sqlite3.connect(config.db_file)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        rows = cur.execute("select * from users where user_id=?", (user_id,))
        user_row = UserRow()
        for row in rows:
            user_row.subject = row['subject']
            user_row.level = row['level']
            user_row.task = row['task']
            user_row.answer = row['answer']
        con.close()
        return user_row

    @staticmethod
    def delete_data(user_id):
        con = sqlite3.connect(config.db_file)
        cur = con.cursor()
        cur.execute("delete from users where user_id=?", (user_id,))
        con.commit()
        con.close()

