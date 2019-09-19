import json
import apiai
import configparser


def make_response(response_from_ai, action, parameters):
    def cons_response(data_obtain):
        if data_obtain == 'response_ai':
            return response_from_ai
        elif data_obtain == 'action':
            return action
        elif data_obtain == 'parameters':
            return parameters
        else:
            return None
    return cons_response


def response_ai(response):
    return response('response_ai')


def action(response):
    return response('action')


def parameters(response):
    return response('parameters')


def collect_request(message):
    config_file = configparser.ConfigParser()
    config_file.read('/Users/Konstantin/Desktop/friday/dialogflow/config.ini')

    request = apiai.ApiAI(f'{config_file.get("Connection", "token")}').text_request()
    request.session_id = f'{config_file.get("Connection", "session_id")}'
    request.lang = f'{config_file.get("Language", "lang")}'
    request.query = message

    return request


def request_to_dialogflow(request):
    full_json_response = json.loads(request.getresponse().read().decode('utf-8'))
    response_ai = full_json_response['result']['fulfillment']['speech']
    action = full_json_response['result']['action']
    parameters = full_json_response['result']['parameters']

    return make_response(response_ai, action, parameters)
