import json
import requests
from .core import db
from .core import proxy


def get_proxy():
    def get_cache_proxy():
        sql_request = "SELECT * FROM cache_proxy LIMIT 1;"
        request = db.make_request(sql_request)
        ip, port = db.execute(request)[0]
        cache_proxy = proxy.make_proxy(ip, port)

        sql_request = "DELETE FROM cache_proxy WHERE ip=?;"
        request = db.make_request(sql_request, data=(ip, ))
        db.execute(request)
        return cache_proxy

    url = 'http://pubproxy.com/api/proxy?type=https'
    # Если бот попал в бан, то переходим на кэшированные прокси
    try:
        response = requests.get(url).json()
    except json.decoder.JSONDecodeError:
        cache_proxy = get_cache_proxy()
        return cache_proxy

    ip = response['data'][0]['ip']
    port = ['data'][0]['port']
    current_proxy = proxy.make_proxy(ip, port)

    return current_proxy


def write_proxy(current_proxy):
    sql_requests = ["UPDATE proxy SET ip=?, port=?, country=? WHERE id=0;",
                    "INSERT INTO cache_proxy VALUES (?, ?, ?);"]
    request_data = (proxy.ip(current_proxy), proxy.port(current_proxy))

    for request_body in sql_requests:
        request_to_db = db.make_request(request_body, data=request_data)
        db.execute(request_to_db)


def read_proxy():
    sql_request = 'SELECT ip, port FROM proxy'
    request = db.make_request(sql_request)
    ip, port = db.execute(request)[0]

    current_proxy = proxy.make_proxy(ip, port)
    return current_proxy


def set_proxy(current_proxy):
    return {'https': f'https://{proxy.ip(current_proxy)}:{proxy.port(current_proxy)}'}


def proxy_info(current_proxy):
    url = f'http://free.ipwhois.io/json/{proxy.ip(current_proxy)}?lang=ru'
    response = requests.get(url).json()

    info = {'ip': response['ip'], 'country': response['country'], 'city': response['city']}
    return info
