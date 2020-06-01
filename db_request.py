import sqlite3


def connect():
    connection = sqlite3.connect('friday.db')
    cursor = connection.cursor()
    return (connection, cursor)


def write_purchase(title, purchases, chat_id):
        connection, cursor = connect()
        sql_request = 'INSERT INTO purchase (purchase_name, purchase_list, id) VALUES (?, ?, ?);'
        cursor.execute(sql_request, (title, purchases, chat_id))
        connection.commit()

def read_purchase(chat_id):
    connection, cursor = connect()
    sql_request = 'SELECT purchase_name, purchase_list FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id, ))
    purchase = cursor.fetchall()
    return [purchase[0][0], purchase[0][1]]

def update_purchase(title, purchases, chat_id):
    connection, cursor = connect()
    sql_request = 'UPDATE purchase SET purchase_name=?, purchase_list=? WHERE id=?;'
    cursor.execute(sql_request, (title, purchases, chat_id))
    connection.commit()

def delete_purchase(chat_id):
    connection, cursor = connect()
    sql_request = 'DELETE FROM purchase WHERE id=?;'
    cursor.execute(sql_request, (chat_id,))
    connection.commit()