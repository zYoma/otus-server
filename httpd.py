import socket
from select import select
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
from urllib.parse import unquote
from optparse import OptionParser
import os


TO_MONITOR = []
SEPARATOR = '\r\n'
DOUBLE_SEPARATOR = SEPARATOR * 2
CONTENT_TYPES = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash',
}
DEFAULT_CONTENT_TYPE = 'text/plain'
DEFAULT_FILENAME = 'index.html'
DEFAULT_EXT = 'html'


def parse_request(request):
    parsed = request.split(' ')
    method = parsed[0]
    if len(parsed) < 2:
        return method, ''

    url = unquote(parsed[1])
    return method, url


def generate_headers(method, url, file_path):
    if method not in ['GET', 'HEAD']:
        return f'HTTP/1.1 405 Method not allowed{SEPARATOR}', 405

    if not url:
        return f'HTTP/1.1 400 Bad request{SEPARATOR}', 400

    if not os.path.exists(file_path):
        return f'HTTP/1.1 404 Not found{SEPARATOR}', 404

    return f'HTTP/1.1 200 OK{SEPARATOR}', 200


def generate_header_for_ok(body, ext):
    def get_date_for_header():
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)

    def get_content_type():
        try:
            return CONTENT_TYPES[ext]
        except KeyError:
            return DEFAULT_CONTENT_TYPE

    headers = {
        'Date': get_date_for_header(),
        'Server': 'otus-server',
        'Content-Length': int(len(body)),
        'Content-Type': get_content_type(),
        'Connection': 'keep-alive',
    }
    return f'{SEPARATOR}'.join([f'{key}: {value}' for key, value in headers.items()]) + DOUBLE_SEPARATOR


def get_filename_from_path(path: str):
    if not path:
        return ''
    return os.path.split(path)


def get_clear_filename(filename):
    return filename.split('?')[0]


def get_file_ext(filename):
    name = filename.split('.')
    if len(name) < 2:
        return None
    return name[-1]


def get_file(file_path):
    with open(file_path, 'rb') as template:
        return template.read()


def generate_content(code, file_path, ext):
    if code == 404:
        return '<h1>404</h1><p>Not found</p>'
    if code == 405:
        return '<h1>405</h1><p>Method not allowed</p>'
    if code == 400:
        return '<h1>400</h1><p>Bad request</p>'

    return get_file(file_path)


def generate_response(request, root_dir):
    method, url = parse_request(request)
    file_path, filename = get_filename_from_path(root_dir + url)
    filename = get_clear_filename(filename)
    ext = get_file_ext(filename)
    if ext is None:
        filename = DEFAULT_FILENAME
        ext = DEFAULT_EXT

    file_path = os.path.join(file_path, filename)
    headers, code = generate_headers(method, url, file_path)
    body = generate_content(code, file_path, ext)
    headers += generate_header_for_ok(body, ext)
    if method == 'HEAD':
        body = ''
    if isinstance(body, bytes):
        return headers.encode() + body

    return (headers + body).encode()


def accept_connection(server_socket):
    client_socket, addr = server_socket.accept()
    TO_MONITOR.append(client_socket)


def send_message(client_socket, root_dir):
    request = client_socket.recv(4096)
    if request:
        response = generate_response(request.decode(), root_dir)
        client_socket.sendall(response)

    client_socket.close()
    TO_MONITOR.remove(client_socket)


def event_loop(server_socket, root_dir):
    while True:
        ready_to_read, _, _ = select(TO_MONITOR, [], [])
        for sock in ready_to_read:
            if sock is server_socket:
                accept_connection(sock)
            else:
                send_message(sock, root_dir)


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=80)
    op.add_option("-r", "--root_dir", action="store", default='templates')
    (opts, args) = op.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', opts.port))
    server_socket.listen()

    TO_MONITOR.append(server_socket)
    try:
        event_loop(server_socket, opts.root_dir)
    except KeyboardInterrupt:
        pass
