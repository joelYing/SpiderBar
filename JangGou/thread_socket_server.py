#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19-11-11

"""
socket实现的Web服务-多线程
"""
import errno
import socket
import threading
import time

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
body = 'Hello, world! <h1> this is django socket server test </h1> - from {thread_name}'
response_params = [
    'HTTP/1.0 200 OK',
    'Date： Sun， 27 may 2019 01:01:01 GMT',
    'Content-Type： text/html；charset=utf-8',
    'Content-Length： {length}\r\n',
    body,
]
response = '\r\n'.join(response_params)


def handle_connection(conn, addr):
    # print('oh, new conn', conn, addr)
    #
    time.sleep(20)
    request = b""
    while EOL1 not in request and EOL2 not in request:
        request += conn.recv(1024)
    print(request)
    # response转为bytes后传输
    current_thread = threading.currentThread()
    content_length = len(body.format(thread_name=current_thread.name).encode())
    print(current_thread.name)
    conn.send(response.format(thread_name=current_thread.name, length=content_length).encode())
    conn.close()


def main():
    # socket.AF_INET 用于服务器与服务器之间的网络通信
    # socket.SOCK_STREAM 用于基于TCP的流式socket通信
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口可复用，保证每次按Ctrl+C后，快速重启
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('127.0.0.1', 8000))
    # 设置backlog--socket 连接最大排队数量
    serversocket.listen(10)
    print('http://127.0.0.1:8000')
    # 设置socket的非阻塞模式
    serversocket.setblocking(0)

    try:
        i = 0
        while True:
            try:
                conn, address = serversocket.accept()
            except BlockingIOError as e:
                # if e.args[0] != errno.EAGAIN:
                #     raise
                continue
            i += 1
            print(i)
            t = threading.Thread(target=handle_connection, args=(conn, address), name='thread-%s' % i)
            t.start()
    finally:
        serversocket.close()


if __name__ == '__main__':
    main()
