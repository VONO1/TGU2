import datetime
import json
import pytz
from wsgiref.simple_server import make_server


def handle_get_request(uri):
    # Получение временной зоны из пути или использование GMT по умолчанию
    timezone_name = uri.lstrip('/') or 'GMT'
    try:
        timezone = pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError:
        return generate_error_response('unknown_time_zone')
    # Форматирование текущего времени для ответа
    current_time = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
    body = f"""
            <html>
            <head></head>
            <body>
            {current_time}
            </body>
            </html>
           """
    headers = [('Content-Type', 'text/html')]
    return body, headers, 0

def handle_post_convert(data, uri):
    # Попытка извлечь и преобразовать временные данные
    try:
        date_str = data['date']
        from_tz_name = data['tz']
        to_tz_name = uri.lstrip('/api/v1/convert/')
    except KeyError:
        return generate_error_response('post_req_input_err')
    try:
        from_tz = pytz.timezone(from_tz_name)
        to_tz = pytz.timezone(to_tz_name)
        datetime_obj = datetime.datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S').replace(tzinfo=from_tz)
        converted_time = datetime_obj.astimezone(to_tz)
    except Exception:
        return generate_error_response('post_req_process_err')
    headers = [('Content-Type', 'application/json')]
    body = converted_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    return body, headers, 0

def handle_post_datediff(data, uri):
    # Попытка извлечь и сравнить временные данные
    try:
        first_date_str = data['first_date']
        first_timezone = data['first_tz']
        second_date_str = data['second_date']
        second_timezone = data['second_tz']
    except KeyError:
        return generate_error_response('post_req_input_err')
    try:
        first_tz = pytz.timezone(first_timezone)
        second_tz = pytz.timezone(second_timezone)
        first_datetime = datetime.datetime.strptime(first_date_str, '%d.%m.%Y %H:%M:%S').astimezone(first_tz)
        second_datetime = datetime.datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d').astimezone(second_tz)
    except Exception:
        return generate_error_response('post_req_process_err')
    time_diff = (first_datetime - second_datetime).total_seconds()
    headers = [('Content-Type', 'application/json')]
    body = str(time_diff)
    return body, headers, 0

def app(environ, start_response):
    # Основная функция обработки входящих запросов
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']

    if method == 'GET':
        response_body, headers, check = handle_get_request(path)
        status = '200 OK' if check == 0 else '500 Internal Server Error'

    elif method == 'POST' and '/api/v1/convert' in path:
        size = int(environ['CONTENT_LENGTH'])
        body = environ['wsgi.input'].read(size).decode('utf-8')
        data = json.loads(body)
        response_body, headers, check = handle_post_convert(data, path)
        status = '200 OK' if check == 0 else '500 Internal Server Error'

    elif method == 'POST' and path == '/api/v1/datediff':
        size = int(environ['CONTENT_LENGTH'])
        body = environ['wsgi.input'].read(size).decode('utf-8')
        data = json.loads(body)
        response_body, headers, check = handle_post_datediff(data, path)
        status = '200 OK' if check == 0 else '500 Internal Server Error'

    else:
        # Обработка неизвестных запросов
        response_body = 'unknown_request'
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html')]

    start_response(status, headers)
    return [response_body.encode('utf-8')]

def generate_error_response(error_code):
    # Генерация HTML-ответа на основе кода ошибки
    headers = [('Content-Type', 'text/html')]
    body = f"""
            <html>
            <head></head>
            <body>
            {error_code}
            </body>
            </html>
           """
    return body, headers, 1

if __name__ == '__main__':
    port = 6666
    with make_server('', port, app) as server:
        print(f"Server running on port {port}")
        server.serve_forever()
