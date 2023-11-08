import cgi
import threading
from dataclasses import dataclass
import socket, struct, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from msg import *


messages = []
clientId = 0
clientmsg = ''

class requestHandler(BaseHTTPRequestHandler):
    global messages, clientmsg
	
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        output = '<html><body><form method="POST" enctype="multipart/form-data">' \
                 '<h1>ClientID is ' + str(clientId) + '</h1>' \
                 '<h1>' + str(clientmsg) + '</h1>' \
                 '<input name="message" type="text" placeholder="New message">' \
                 '<input name="id" type="text" placeholder="id">' \
                 '<input name="SendToAll" type="checkbox" value = "1"/>' \
                 '<label for ="SendToAll" > Send To All </label><br/>' \
                 '<input type="submit" value="Send">' \
                 '<input type="submit" value="Update" name="action" a href="/">' \
                 '<h1>Message List</h1><ul>'
        print(messages)
        for i in messages:
            output += '<li>' + i + '</li>'
        output += '</ul>'
        self.wfile.write(output.encode())

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        content_len = int(self.headers.get('Content-length'))
        pdict['Content-Length'] = content_len
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            print(fields)
            id = fields.get('id')[0]
            if len(id) == 0:
                id = 0
            else:
                id = int(id)
            text = fields.get('message')[0]
            try:
                fields.get('SendToAll')[0]
            except:
                Message.SendMessage(id, MT_DATA, text)
            else:
                Message.SendMessage(MR_ALL, MT_DATA, text)

        self.send_response(301)
        self.send_header('content-type', 'text/html')
        self.send_header('Location', '/')
        self.end_headers()

def ProcessMessages():
    global messages, clientId
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        clientId = m.Header.To
        if m.Header.Type == MT_DATA:
            messages.append('Message: ' + m.Data + "   From: " + str(m.Header.From))
            print("New message: " + m.Data + "\nFrom: " + str(m.Header.From))
        else:
            time.sleep(1)

def ProcessServer():
    server_address = ("", 8000)
    print("Web interface started")
    HTTPServer(server_address, requestHandler).serve_forever()

def Client():
        global clientId
        print("Python client has started\n")
        w = threading.Thread(target=ProcessServer)
        w.start()
        Message.SendMessage(MR_BROKER, MT_INIT)
        Message.SendMessage(MR_STORAGE, MT_GETLAST)
        t = threading.Thread(target=ProcessMessages)
        t.start()

Client()
