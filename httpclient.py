#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Sanjeev Kotha
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

# Resources and References
# https://docs.python.org/3/library/urllib.parse.html
# https://reqbin.com/req/nfilsyk5/get-request-example
# https://reqbin.com/Article/HttpPost
# https://www.clickssl.net/blog/port-80-http-vs-port-443-https

import sys
import socket
import urllib.parse as up

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
        return int(data.split('\r\n')[0].split()[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
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

    def GET(self, url, args=None):
        code = 500
        body = ""
        o = up.urlparse(url)
        port = o.port

        if port == None and o.scheme == 'https':
            port = 443
        elif port == None and o.scheme == 'http':
            port = 80

        host = o.hostname
        self.connect(host,port)
        path = o.path if o.path != '' else '/'

        request = 'GET {} HTTP/1.1\r\n'.format(path)
        request += 'Host: {}\r\n'.format(host)
        request += 'Accept: */*\r\n'
        request += 'Connection: close\r\n\r\n'

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(str(code)+'\n'+headers+'\n'+body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = "" 
        o = up.urlparse(url)
        port = o.port

        if port == None and o.scheme == 'https':
            port = 443
        elif port == None and o.scheme == 'http':
            port = 80

        args = up.urlencode(args) if args != None else up.urlencode("")

        host = o.hostname
        self.connect(host,port)

        path = o.path if o.path != '' else '/'

        request = 'POST {} HTTP/1.1\r\n'.format(path)
        request += 'Host: {}\r\n'.format(host)
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        request += 'Content-Length: {}\r\n'.format(len(args))
        request += 'Connection: close\r\n\r\n'
        request += args

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        print(str(code)+'\n'+headers+'\n'+body)
        return HTTPResponse(code, body)

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
