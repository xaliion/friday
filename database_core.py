import sqlite3


def connect():
    connection = sqlite3.connect('friday.db')
    cursor = connection.cursor()
    return (connection, cursor)


def write(to_table, values):
    sql_request = 'INSERT INTO {} VALUES {};'.format(to_table, str(values))
    connection, cursor = connect()
    cursor.execute(sql_request)
    connection.commit()


def read(columns, from_table, key=None, value=None):
    sql_request = 'SELECT'

    def create_sql_request():
        nonlocal sql_request
        if key is None or value is None:
            sql_request += ' {} FROM {};'.format(columns, from_table)
        else:
            sql_request += ' {} FROM {} WHERE {}="{}";'.format(columns, from_table, key, value)

        connection, cursor = connect()
        cursor.execute(sql_request)
        return cursor.fetchall()

    return create_sql_request()


def delete(from_table, key, value):
    sql_request = 'DELETE FROM {} WHERE {}={};'.format(from_table, key, value)
    connection, cursor = connect()
    cursor.execute(sql_request)
    connection.commit()


def update(to_table, column, data, key, value):
    sql_request = 'UPDATE {} SET {}={} WHERE {}={};'.format(to_table, column, data, key, value)
    connection, cursor = connect()
    cursor.execute(sql_request)
    connection.commit()
