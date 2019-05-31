"""
This module contains custom classes to wrap around the bare sqlite3 library and
make it customized for the application

Field - mini-class that defines a Field type
Table - defines the query of making a sqlite3 table and can create a table
given a connection to a database.
"""

from pathlib import Path
import sqlite3


class Field(object):
    """
    Defines an sqlite3 field, including it's type, name and other parameters
    """
    def __init__(self, name: str, kind: str, extra: str = None):
        """
        :param name: name of the Field
        :param kind: type of the FIeld
        :param extra: used for extra params, such as UNIQUE etc.
        """
        self.name = name
        self.kind = kind.upper()

        self.extra = extra
        if self.extra:
            self.extra = extra.upper()

    def __repr__(self):
        """
        Represents the object as part of an SQLite query.
        """
        if self.extra:
            return f"{self.name} {self.kind} {self.extra}"
        else:
            return f"{self.name} {self.kind}"


class Table(object):
    """
    Defines an sqlite3 table as an OOP object
    """
    def __init__(self, name: str, fields: list):
        """
        :param name: Name of the table object
        :param fields: list of Field objects used in the table.
        """
        self.name = name
        self.fields = fields

    def __repr__(self):
        """
        Represents the object as part of an SQLite query
        """
        fields_section = '('
        for field in self.fields:
            fields_section += str(field) + ', '
        fields_section = fields_section[:-2] + ')'

        return f"{self.name}{fields_section}"

    def create(self, connection: sqlite3.Connection):
        """
        Creates the table from the query when given a connection and cursor

        :param connection: sqlite3 connection
        """
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.__repr__()}")
        connection.commit()


class BaseDataBase(object):
    def __init__(self, folder: str, fname: str):
        """
        Sets up the BaseDataBase class to create necessary folders and files.

        :param folder: folder where the database should be stored
        :param fname: filename of the database. Must end in .db
        """
        self.folder = Path(folder)
        self.fname = Path(fname)
        self.full_path = Path.cwd().joinpath(self.folder, self.fname)

        self.folder.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(self.full_path)

    def create_table(self, table: Table):
        """
        Creates a table within the database file

        :param table: Table query object
        """
        table.create(connection=self.conn)

    def insert(self, table: Table, data: list):
        """
        Inserts a row of data into the table

        :param table: table into which the data must be inserted
        :param data: the data which must be inserted
        """
        query = f"INSERT INTO {table} VALUES ("
        for item in data:
            query += item + ', '
        query = query[:-2] + ')'

        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()


class UserDataBase(BaseDataBase):
    def __init__(self, folder: str, fname: str):
        """
        Application specific database class

        :param folder: folder where the database should be stored
        :param fname: filename of the database. Must end in .db
        """
        super().__init__(folder=folder, fname=fname)

        standard_fields = [
            Field('uid', 'INTEGER', 'UNIQUE'),
            Field('lang', 'TEXT')
        ]

        main_fields = standard_fields + [
            Field('state', 'INTEGER')
        ]

        # keep track of user info
        self.userlog = Table(name='UserLog', fields=main_fields)
        # keeps track of who can be messaged (non-blocked)
        self.msglog = Table(name='MsgLog', fields=standard_fields)

        # create the necessary tables in the database
        self.userlog.create(connection=self.conn)
        self.msglog.create(connection=self.conn)

    def extract_language(self):
        """
        """
        pass

    def collect_stats(self):
        """
        """
        pass

    def add_user(self):
        """
        """
        pass

    def log_user_action(self):
        """
        """
        pass
