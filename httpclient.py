#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def get_parsed_url_info(self, url):
        parsed_url = urllib.parse.urlparse(url)

        path = parsed_url.path
        port = parsed_url.port
        query = parsed_url.query

        if not port:
            port = self.get_port(parsed_url.scheme)

        if not path:
            path = "/"

        if query:
            path += "?{}".format(query)

        return path, port, parsed_url.hostname

    def get_port(self, url_scheme):
        if url_scheme == "http":
            return 80
        elif url_scheme == "https":
            return 443

    def get_data(self, hostname, port, request):
        self.connect(hostname, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()

        return data

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def send_request(self, data):
        if not data:
            return HTTPResponse(404, "")

        code = self.get_code(data)
        body = self.get_body(data)

        print("data", data)
        print("status code, body", code, body)

        return HTTPResponse(code, body)

    def GET(self, url, args=None):
        path, port, hostname = self.get_parsed_url_info(url)

        request = ("GET {} HTTP/1.1\r\nHost: {}\r\nAccept: */*\r\nConnection: Closed\r\n\r\n"
                   .format(path, hostname))
        data = self.get_data(hostname, port, request)

        return self.send_request(data)

    def POST(self, url, args=None):
        path, port, hostname = self.get_parsed_url_info(url)

        if args:
            request_body = urllib.parse.urlencode(args)
            content_length = str(len(request_body))
            content_type = "\r\nContent-Type: application/x-www-form-urlencoded"
        else:
            content_length, content_type, request_body = "0", "", ""

        request = ("POST {} HTTP/1.1\r\nHost: {}\r\nAccept: */*\r\n \
                        Connection: Closed\r\nContent-Length: {}{}\r\n\r\n{}"
                   .format(path, hostname, content_length, content_type, request_body))
        data = self.get_data(hostname, port, request)

        return self.send_request(data)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
