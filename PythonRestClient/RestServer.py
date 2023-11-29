from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
from msg import *

users = []
clientId = 30
clientmsg = ''

class requestHandler(BaseHTTPRequestHandler):
    global clientId

    def MakeResponse(self, to, From, type, data):
        return '{"to":"' + str(to) + '","type":"' + str(type) + '","data":"' + data + '","from":"' + str(From) + '"}'

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length)
        data = post_data.decode('utf-8')
        data = json.loads(data)
        if int(data['type']) == MT_INIT:
            m = Message.SendMessage(int(data['to']), int(data['type']), data['data'])
            self.wfile.write(self.MakeResponse(m.Header.To, m.Header.From, m.Header.Type, m.Data).encode())
            print("Rest client " + str(m.Header.To) + " entered")
        else:
            print(int(data['type']))
            m = Message.SendAsClient(int(data['to']), int(data['from']), int(data['type']), data['data'])
            self.wfile.write(self.MakeResponse(m.Header.To, m.Header.From, m.Header.Type, m.Data).encode())


def ProcessServer():
    server_address = ("", 8989)
    print("Rest support server has started")
    HTTPServer(server_address, requestHandler).serve_forever()

def ProcessMessages():
    global clientId
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        clientId = m.Header.To
        if m.Header.Type == MT_DATA:
            print("You got message: " + m.Data + "\nFrom: " + str(m.Header.From))
        else:
            time.sleep(1)

def RestServer():
    global clientId
    w = threading.Thread(target=ProcessServer)
    w.start()
    Message.SendMessage(MR_BROKER, MT_REST)
    t = threading.Thread(target=ProcessMessages)
    t.start()

RestServer()