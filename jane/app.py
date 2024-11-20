from patch import patch_bytes,_patch_bytes
import config
from headers import get_content_length, get_headers,update_content_length,get_header_path,is_keep_alive,headers_get_host,headers_update_host,headers_update_server
import asyncio
import functools
import sys 
import ssl 
import random

from duration import Duration,durations_dump

semaphore = asyncio.Semaphore(100)

def printb(byte_data):
    sys.stdout.buffer.write(byte_data)
    sys.stdout.flush()

async def async_write(writer, data):
    length = len(data or b'')
    writer.write(data)
    await writer.drain()
    return length

async def stream(reader,writer,reader_upstream,writer_upstream,patch,upstream_host,server_name=None,bufsize=4068,max_header_length=4069):
    with Duration("Keep-Alive Session total") as duration_session:
        previous_path = None
        while True:
            with duration_session("Request total") as duration_request:
                data = b''
                bytes_received = 0
                content_length = None
                body_full = b''
                is_http_request = False
                # Get content length and validate header length
                with duration_request("Reading headers") as duration_reading_headers:
                    while len(data) < max_header_length:
                        data_chunk = await reader.read(1)
                        if not data_chunk:
                            break
                        data+=data_chunk
                        content_length = get_content_length(data)
                        if content_length is not None:
                            break
                        if len(data) >= max_header_length:
                            sys.stdout.buffer.write(data)
                            sys.stdout.flush()
                            raise NotImplementedError("Headers not found within limit.")
                if content_length is None:
                    break
                headers, body = get_headers(data)
                headers_host = headers_get_host(headers)
                if headers_host:
                    print(headers_host * 100)
                if content_length == 0:
                    previous_path = get_header_path(data)
                    duration_request.title = "Request of " + previous_path
                    print("Request (content length: {}): {}".format(content_length,previous_path))
                    print("[{}]".format(headers.decode()))
                else:
                    duration_request.title = "Response of " + previous_path
                    print("Response (headers length: {}): {}".format(len(headers),previous_path))
                # Get headers and collect and validate body
                if content_length:
                    with duration_request("Parsing response body"):
                        while len(body) < content_length:
                            adjusted_bufsize = content_length - len(body) >= bufsize and bufsize or content_length - len(body)
                            body_chunk = await reader.read(adjusted_bufsize)
                            
                            if not body_chunk:
                                print("IK KOM HIERR EN CHUNK IS NULL?: {} ".format(body_chunk is None and "yes" or "no")  * 1000)
                                exit(2)
                                break
                            body += body_chunk
                            if len(body) == content_length:
                                print("PERFECTE BREAK ")
                                break
                            if len(body) > content_length:
                                print("TOO MUCH DATA ")
                                exit(3)
                                break

                    
                    # Write body to upstream
                    if(len(body) != content_length):
                        print("Body length: {} Content-Length: {}".format(len(body),content_length))
                        exit(1)

                    old_length = len(body)
                    patched_body = None
                    with duration_request("Patching body"):
                        patched_body = await patch_bytes(body,patch)
                    new_length = len(patched_body)
                    body = patched_body
                    print(server_name * 50)
                    with duration_request("Patching request headers"):
                        print("Original request headers: [{}]".format(headers.decode()))

                        if not old_length == new_length:
                            headers = update_content_length(headers,new_length)
                            print("Updated request header Content-Length")
                        print("Patched request headers: [{}]".format(headers.decode()))
                        if server_name:
                            headers = headers_update_server(headers,server_name)
                            print("Updated response header Server")
      
                    with duration_request("Writing headers"):
                        #writer_upstream.write(headers+body)
                        await async_write(writer_upstream,headers)
                    with duration_request("Writing body"):
                        await async_write(writer_upstream,body)
                        if not is_keep_alive(headers):
                            print("Closing connection by request")
                            break
                        else:
                            print("Keeping connection alive by request")
                        #await writer_upstream.drain()
                else:
                    #headers = body + await reader.read(4096)
                    with duration_request("Patching response headers"):
                        print("Original response headers: [{}]".format(headers.decode()))
     
                        print("Header1",headers)
                        if upstream_host:
                            headers = headers_update_host(headers, upstream_host)
                            print("Updated response header Host")
                        print("Header2",headers)
                        print("Patched response headers: [{}]".format(headers.decode()))
                    with duration_request("Writing and flushing headers only"):
                        print("[{}]".format(headers.decode()))
                        #writer_upstream.write(headers)
                        await async_write(writer_upstream, headers)
                
                # anonymize


                temp_reader = reader
                temp_writer = writer 
                reader = reader_upstream
                writer = writer_upstream
                reader_upstream = temp_reader
                writer_upstream = temp_writer 
                #await writer.drain()
            # reset initial vars
        #await writer.drain()
        #print("Writer closed")
        #
        with duration_session("Closing upstream"):
            #await writer.drain()
            writer.close()
        #    await writer_upstream.drain()
        #    writer_upstream.close()

        with duration_session("Closing stream"):
            #await writer_upstream.drain()
            writer_upstream.close()


        duration_session.dump()
        #    await writer.drain()
        #    writer.close()
        #await writer.drain()
           #conn.close()





count = 0

async def handler(reader,writer,host,port,patch,upstream_host,server_name):
    global count
    ssl_context = None
    if port == 443:
        ssl_context = ssl.create_default_context()




    async with semaphore:
        count += 1
        
        reader_upstream,writer_upstream = await asyncio.open_connection(host,port,ssl=ssl_context)

        print("ONE REQUEST",count)
        await stream(reader, writer, reader_upstream, writer_upstream,patch,upstream_host,server_name)
        print("END REQUEST",count)
        durations_dump()

async def serve(host,port,forward_host,forward_port,patch=None,upstream_host=None,server_name='Jane HTTPd',**kwargs):
    if not patch:
        patch = []
    patched_handler = functools.partial(handler,host=forward_host, port=forward_port,patch=patch, upstream_host=upstream_host,server_name=server_name)
    server1 = await asyncio.start_server(patched_handler, host,port,backlog=100)
    server2 = await asyncio.start_server(patched_handler, host,port+1)
    servers = [server1,server2]
    for server in servers:
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}') 
    async with server1,server2:
        await asyncio.gather(*[server1.serve_forever(),server2.serve_forever()])


if __name__ == '__main__':
    asyncio.run(serve("127.0.0.1",8420,"127.0.0.1",1234,
        upstream_hosta='localhost:8420',
        server_name='Jane HTTPd',
        patch = [
        ['h6','h1'],
        ['h5','h2'],
        ['h4','h3'],
        ['h3','h4'],
        ['h2','h5'],
        ['h1','h6'],
        ['Tue','Tuesday'],
        ['italic','unique-var-1'],
        ['bold', 'unique-var-2'],
        ['unique-var-1','bold'],
        ['unique-var-2','italic'],
        ['black', 'green'],
        ['#000000', 'green'],
        ['<title>','<title patched="true">[PATCHED] '],
        ['<a ', lambda data: '<a style="color: {};" '.format(
            random.choice(['green','blue','red','green'])
            )],
        #['a>','a>']
        #['a>','/>'],
    ]))


