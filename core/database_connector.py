import sqlite3


def connect():
    connection = sqlite3.connect('friday.db')
    cursor = connection.cursor()
    return (connection, cursor)
