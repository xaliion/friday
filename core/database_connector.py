import sqlite3


def connect():
    connection, cursor = sqlite3.connect('../friday.bd')
    return (connection, cursor)
