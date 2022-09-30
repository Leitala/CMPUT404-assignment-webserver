#  coding: utf-8
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def unsecure_format(self):
        directory = self.path.split("/")
        if ".." in directory:
            return True
        else:
            return False

    def send_status_code(self, status):
        if status == 405:
            msg = self.protocol+ " 405 Method Not Allowed\r\n"
            self.request.sendall(bytearray(msg,'utf-8'))
            return
        elif status == 404:
            msg = self.protocol + " 404 Not Found\r\n"
            self.request.sendall(bytearray(msg,'utf-8'))
            return
        elif status == 301:
            location ="Location: http://" + str(HOST) + ":" + str(PORT) + self.path + "\n\n"
            msg = self.protocol + " 301 Moved Permanently\r\n" + location
            self.request.sendall(bytearray(msg,'utf-8'))
            return
        elif status == 200:
            content_type = self.url_path.split(".")[-1]
            mime_type = "Content-type: text/"+content_type
            file = open(self.url_path, "r")
            content = file.read()
            msg = self.protocol +" 200 OK\r\n" + mime_type +"\n\n" + content
            self.request.sendall(bytearray(msg,'utf-8'))
            file.close()
            return



    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        if self.data == b"":
            return

        self.request_method, self.path, self.protocol = self.data.split(b"\r\n")[0].decode('utf-8').split(" ")

        if "./www" not in self.path:
            self.url_path = "./www" + self.path
        else:
            self.url_path = self.path

        if self.request_method == "GET":


            if not os.path.exists(self.url_path) or self.unsecure_format():
                self.send_status_code(404)

            elif os.path.isdir(self.url_path) and self.url_path[-1] != "/":
                self.send_status_code(301)
            else:
                if os.path.isdir(self.url_path):
                    self.url_path += "index.html"
                self.send_status_code(200)
        elif self.request_method == "POST" or self.request_method == "PUT" or self.request_method == "DELETE":
            self.send_status_code(405)
        else:
            self.send_status_code(405)





if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
