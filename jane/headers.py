import re



def is_request(data):
    return data.split(b" ")[0].upper() in [
        b'GET', 
        b'POST',
        b'DELETE',
        b'PUT',
        b'HEAD'
    ] and b'\r\n\r\n' in data

def is_response(data):
    return not is_request(data)

def get_headers(data):
    if not data:
        return None,None
    if not b'\r\n\r\n' in data:
        return None,None
    headers, *body = data.split(b'\r\n\r\n')
    headers = headers+b"\r\n\r\n"
    body = b'\r\n\r\n'.join(body)
    return headers,body

def get_header_path(data):
    if is_response(data):
        return None
    headers,_ = get_headers(data)
    try:
        return headers.split(b' ')[1].decode()
    except:
        return None

def headers_get_host(headers):
    headers,body = get_headers(headers)
    if not headers:
        return None
    headers = headers.decode()
    expr = r'[Hh]ost\s*:\s*(.*)\s'
    matches = re.findall(expr,headers)
    if not matches:
        return None
    return matches[0]




def is_keep_alive(headers):
    headers,body = get_headers(headers)
    if not headers:
        return False
    expr = r'[Cc]onnection\s*:\s*keep-alive'
    return re.search(expr,headers.decode())


example_get_request_200 = b"GET / HTTP/1.1\r\n" \
    b"Content-Length: 50\r\n" \
    b"Connection: close\r\n" \
    b"Content-Type: application/x-json\r\n" \
    b"Content-Length: 3\r\n" \
    b"Custom-Header1: woei\r\n" \
    b"Custom-Header2: waai\r\n" \
    b"Content-Length: 200\r\n" \
    b"\r\n"

example_get_request_3 = b"GET / HTTP/1.1\r\n" \
    b"Content-Length: 50\r\n" \
    b"Connection: close\r\n" \
    b"Content-Type: application/x-json\r\n" \
    b"Content-Length: 3\r\n" \
    b"\r\n"

example_get_request_50 = b"GET / HTTP/1.1\r\n" \
    b"Content-Length: 50\r\n" \
    b"\r\n"

example_response_200_1337 = b"200 OK\r\n" \
    b"Content-Length: 1337\r\n\r\n"

example_response_http_200_1337 = b"HTTP/1.1 200 OK\r\n" \
    b"Content-Length: 1337\r\n\r\n"



example_response_404_420 = b"404 NOT FOUND\r\n" \
    b"Content-Length: 420\r\n\r\n"

example_response_301_42 = b"301 REDIRECT\r\n" \
    b"Content-Length: 42\r\n\r\n"

example_response_200_0 = b"200 OK\r\n" \
    b"Content-Length: 0\r\n\r\n"








def get_content_length(data):
    headers, body = get_headers(data)
    if not headers:
        return None
    headers = headers.decode()
    if headers.startswith('GET /') and headers.find("Content-Length") == -1 and headers.endswith("\r\n\r\n"):
        return 0
    pattern = r"(.*\d\d\d|GET|POST|PUT|HEAD|DELETE)(?:\s+.*)+Content-Length:\s*(\d+)\s\s"
    matches = re.findall(pattern,headers,re.IGNORECASE)
    if not matches:
        return None
    if matches[0][0] == 'GET' and not matches[0][1]:
        return 0
    return int(matches[0][1]) 


def headers_get_server(headers):
    headers,_ = get_headers(headers)
    if not headers:
        return False
    expr = r'[Ss]erver\s*:\s*(.*)\r\n'
    matches = re.findall(expr,headers.decode())
    try:
        return matches[0] 
    except IndexError:
        return None

def headers_update_server(headers, new_server):
    headers,_ = get_headers(headers)
    if not headers:
        return None
    original_server = headers_get_server(headers)
    if not original_server:
        return headers
    return headers.decode().replace(original_server,new_server).encode()
    #new_header = "Server: " + new_server # + "\\r"
    #expr = r'[Ss]erver\s*:\s*{}'.format(original_server)
    #headers = re.sub(expr,new_header,headers.decode())
    #return headers.encode()
 


def headers_update_host(headers, new_host):
    headers,_ = get_headers(headers)
    if not headers:
        return None
    original_host = headers_get_host(headers)
    return headers.decode().replace(original_host,new_host).encode()
    #expr = r'[Hh]ost\s*:\s*{}'.format(original_host)
    #new_header = "Host: " + new_host # + "\\r"
    #headers = re.sub(expr,new_header,headers.decode())
    #return headers.encode()
    
def update_content_length(headers,new_length):
    original_length = get_content_length(headers)
    headers = headers.replace(str(original_length).encode(),str(new_length).encode())
    return headers

assert(get_content_length(example_get_request_50) == 50)
assert(get_content_length(example_get_request_3) == 3)
assert(get_content_length(example_get_request_200) == 200)
assert(get_content_length(example_response_200_1337) == 1337)
assert(get_content_length(example_response_http_200_1337) == 1337)
assert(get_content_length(example_response_404_420) == 420)
assert(get_content_length(example_response_301_42) == 42)
assert(get_content_length(example_response_200_0) == 0)
assert(get_content_length(b"Content-Length:20\r\n\r\n") is None)
assert(get_content_length(b"Content-Length:20\r\n\r") is None)
assert(get_content_length(b"GET / HTTP/1.1\r\nContent-Id:20\r\n\r\n") == 0)
print(headers_update_server(b"GET / HTTP/1.1\r\nServer: lighttpd/1.4.74\r\nHost: 127.0.0.1:8080\r\n\r\n","Jane HTTPd")) 
print(headers_update_host(b"GET / HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nServer: lighttpd/1.4.74\r\n\r\n","localhost:1337"))
#assert(headers_update_server(b"GET / HTTP/1.1\r\nServer: lighttpd/1.4.74\r\nHost: 127.0.0.1:8080\r\n\r\n","Jane HTTPd") ==b'GET / HTTP/1.1\r\nServer: Jane HTTPd\r\nHost: 127.0.0.1:8080\r\n\r\n')
#assert(headers_update_host(b"GET / HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nServer: lighttpd/1.4.74\r\n\r\n","localhost:1337") == b'GET / HTTP/1.1\r\nHost: localhost:1337\r\nServer: lighttpd/1.4.74\r\n\r\n')
