import sqlite3
from typing import Union


class LikeDatabase:
    """ Encapsulate working with database """

    DATABASE_FILE_NAME = 'likebot/like.db'

    def __init__(self) -> None:
        """ Init db and create connection to local sqlite database """
        self.conn = sqlite3.connect(self.DATABASE_FILE_NAME, check_same_thread=False)
        self.create_db()

    def create_db(self) -> None:
        c = self.conn.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS like '
            '(message_id text, user_id integer, reaction text, PRIMARY KEY (message_id, user_id))'
        )
        self.conn.commit()

    def check_exists(self, message_id: str, user_id: int) -> bool:
        c = self.conn.cursor()
        c.execute(
            'SELECT * FROM like WHERE message_id=? AND user_id=?', (message_id, user_id)
        )

        result = c.fetchone()
        if result:
            return True
        return False

    def add(self, message_id: str, user_id: int, reaction: str) -> None:
        c = self.conn.cursor()
        c.execute(
            'INSERT INTO like(message_id, user_id, reaction) values (?, ?, ?)',
            (message_id, user_id, reaction),
        )
        self.conn.commit()

    def update(self, message_id: str, user_id: int, reaction: str) -> None:
        c = self.conn.cursor()
        c.execute(
            'UPDATE like SET reaction=? WHERE message_id=? AND user_id=?',
            (reaction, message_id, user_id),
        )
        self.conn.commit()

    def get_count(self, message_id: str, reaction: str) -> Union[str, int]:
        c = self.conn.cursor()
        c.execute(
            'SELECT COUNT(*) FROM like WHERE message_id=? AND reaction=?',
            (message_id, reaction),
        )
        count = c.fetchone()[0]
        if not count:
            return ''
        return count

    def add_reaction(self, message_id: str, user_id: int, reaction: str) -> None:
        if self.check_exists(message_id, user_id):
            self.update(message_id, user_id, reaction)
        else:
            self.add(message_id, user_id, reaction)


like_db = LikeDatabase()
