import json
import requests
from core import db


def get_proxy():
    def get_cache_proxy():
        connection, cursor = db.connect()
        sql_request = "SELECT TOP 1 * FROM cache_proxy;"
        cursor.execute(sql_request)
        sql_response = cursor.fetchall()

        proxy = dict.fromkeys(['ip', 'port', 'country'])
        proxy['ip'] = sql_response[0][0]
        proxy['port'] = sql_response[0][1]
        proxy['country'] = sql_response[0][2]

        sql_request = "DELETE FROM cache_proxy WHERE ip=?;"
        cursor.execute(sql_request, (proxy['ip'],))
        connection.commit()
        return proxy

    url = 'http://pubproxy.com/api/proxy?type=https'
    response = requests.get(url)

    # Если бот попал в бан, то переходим на кэшированные прокси
    try:
        json_proxy = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        cache_proxy = get_cache_proxy()
        return cache_proxy

    proxy = dict.fromkeys(['ip', 'port', 'country'])
    proxy['ip'] = json_proxy['data'][0]['ip']
    proxy['port'] = json_proxy['data'][0]['port']
    proxy['country'] = json_proxy['data'][0]['country']
    return proxy


def write_proxy(proxy):
    connection, cursor = db.connect()
    sql_request = "UPDATE proxy SET ip=?, port=?, country=? WHERE id=0;"
    cursor.execute(sql_request, (proxy['ip'], proxy['port'],
                                 proxy['country']))

    sql_request = "INSERT INTO cache_proxy VALUES (?, ?, ?);"
    cursor.execute(sql_request, (proxy['ip'], proxy['port'],
                                 proxy['country']))
    connection.commit()


def read_proxy():
    connection, cursor = db.connect()
    sql_request = 'SELECT ip, port FROM proxy'
    cursor.execute(sql_request)
    sql_response = cursor.fetchall()

    proxy = dict.fromkeys(['ip', 'port'])
    proxy['ip'] = sql_response[0][0]
    proxy['port'] = sql_response[0][1]
    return proxy


def check_size_cached_proxy():
    connection, cursor = db.connect()
    sql_request = "SELECT COUNT(ip) FROM cache_proxy;"
    cursor.execute(sql_request)
    sql_response = cursor.fetchall()

    amount_proxy = sql_response[0][0]

    if (amount_proxy >= 100):
        sql_request = "DELETE FROM cache_proxy;"
        cursor.execute(sql_request)
        connection.commit()


check_size_cached_proxy()
