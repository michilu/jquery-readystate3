#!/usr/bin/env python
"""Comet server
"""

import cmd
import os
import socket
import thread
import threading

DEBUG = (False, True)[1]

PORT = 8081
HOST = "localhost"
S = None
E = threading.Event()
E.clear()

class HandlerBase(object):
    def __init__(self, options):
        name = self.__class__.__name__
        self.options = options

    def receive(self):
        raise NotImplementedError

    def send(self, data="", host=None, port=None):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class TCPHandler(HandlerBase):
    def __init__(self, *argv, **kwargv):
        super(TCPHandler, self).__init__(*argv, **kwargv)
        global S
        S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class CometServer(TCPHandler):
    def __init__(self, *argv, **kwargv):
        super(CometServer, self).__init__(*argv, **kwargv)
        S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        S.bind(("", self.options.port))
        S.listen(1)

    def receive(self):
        self.host = self.port = self.data = self.conn = self.connect = None
        self.listen = True
        headers = {
            "/": """\
HTTP/1.0 200
Content-type: text/html; charset=UTF-8
Cache-Control: no-cache
""",
            "/comet": """\
HTTP/1.0 200
Content-type: text/plain; charset=UTF-8
Cache-Control: no-cache
""",
        }
        html = """\
<html>
<head>
<script type="text/javascript" charset="utf-8">
 window.onload = function(){
  var now = new Date();
  var url = 'http:\/\/%(HOST)s:%(PORT)s\/comet#' + now.getTime();
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
   if ( this.readyState == 3) {
    var lines = this.responseText.split('\\n');
    eval(lines[lines.length - 2]);
   };
  };
  req.open("GET", url, true);
  req.send(null);
 };
</script>
</head>
<body>
</body>
</html>
""" % globals()
        while self.listen:
            (self.conn, (self.host, self.port)) = S.accept()
            request_path = self.recv()
            self.send("%s\n" % headers.get(request_path, "HTTP/1.0 404\n"))
            if request_path == "/":
                self.send(html)
                self.close()
            elif request_path in headers:
                self.connect = True
                E.wait()
                while self.connect:
                    self.send("%s\n" % self.data)
                    E.clear()
                    E.wait()
            else:
                self.close()

    def recv(self):
        return self.conn.recv(4096).split(" ")[1]

    def send(self, data):
        try:
            self.conn.send(data)
        except socket.error, e:
            pass

    def close(self):
        if self.conn:
            self.conn.close()
        self.connect = False

    def run(self):
        while True:
            self.receive()


class Cmd(cmd.Cmd):
    handler = "CometServer"
    prompt = "%(handler)s > " % vars()
    port = PORT

    def __init__(self):
        cmd.Cmd.__init__(self)
        handler = self.name = self.handler
        self.handler = globals()[handler](options=self)
        self.start_server()

    def start_server(self):
        threading.Thread(target=self.handler.receive).start()

    def do_close(self, *argv):
        """(type close): Closing HTTP connection. \
        """
        self.default()
        self.handler.close()

    def do_shutdown(self, *argv):
        """(type shutdown): shutdown server. \
        """
        self.handler.listen = False
        self.handler.close()
        thread.exit()

    def default(self, data=""):
        self.handler.data = data
        E.set()

    def emptyline(self):
        pass


if __name__ == "__main__":
    Cmd().cmdloop();

