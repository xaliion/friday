import sqlite3


def connect():
    connection = sqlite3.connect('friday.db')
    cursor = connection.cursor()
    return (connection, cursor)


def write(user_data, id_data):
    connection, cursor = connect()
    sql_request = 'INSERT INTO purchase (purchase_list, id) VALUES (?, ?);'
    cursor.execute(sql_request, (user_data, id_data))
    connection.commit()


def read(id_data):
    connection, cursor = connect()
    sql_request = 'SELECT purchase_list FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (id_data, ))
    return cursor.fetchall()[0][0]


def update(user_data, id_data):
    connection, cursor = connect()
    sql_request = 'UPDATE purchase SET purchase_list=? WHERE id=?;'
    cursor.execute(sql_request, (user_data, id_data))
    connection.commit()


def delete(id_data):
    connection, cursor = connect()
    sql_request = 'DELETE FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (id_data,))
    connection.commit()
