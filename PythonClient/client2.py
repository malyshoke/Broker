import threading
import socket
import struct
import time
from msg import *
import cgi
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

class PythonClient:
    def __init__(self):
        self.clientId = 0

    def is_integer(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def get_integer_input(self, prompt):
        while True:
            user_input = input(prompt)
            if self.is_integer(user_input):
                return int(user_input)
            else:
                print("Enter number")

class SocketClient(PythonClient):
    def __init__(self):
        super().__init__()
        self.clientId = 0

    def process_messages_by_sockets(self):
        while True:
            m = Message.SendMessage(MR_BROKER, MT_GETDATA)
            if m.Header.Type == MT_DATA:
                print(f"You got a message: {m.Data}")
                print(f"From: {m.Header.From}")
            else:
                time.sleep(1)

    def socket_client(self):
        print("Client has started\n")
        Message.SendMessage(MR_BROKER, MT_INIT)
        t = threading.Thread(target=self.process_messages_by_sockets)
        t.start()
        while True:
            print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit")
            menu = self.get_integer_input("Enter your choice:\n")
            if menu == 1:
                receiver_id = self.get_integer_input("Enter receiver's id:\n")
                message = input("Enter your message:\n")
                Message.SendMessage(receiver_id, MT_DATA, message)
            elif menu == 2:
                message = input("Enter your message:\n")
                Message.SendMessage(MR_ALL, MT_DATA, message)
            elif menu == 3:
                Message.SendMessage(MR_BROKER, MT_EXIT)
                quit()
                break

class APIClient(PythonClient):
    def __init__(self):
        super().__init__()

    def send_request(self, params):
        URL = "http://localhost:8989"
        r = requests.get(url=URL, json=params)
        return r.json()

    def get_history(self):
        a = self.send_request({'to': MR_BROKER, 'from': self.clientId, 'type': MT_GETLAST, 'data': ""})

    def send_init(self):
        id = self.send_request({'to': MR_BROKER, 'from': '', 'type': MT_INIT, 'data': ''})
        self.clientId = int(id['to'])
        print("Client ID is " + str(self.clientId))

    def send(self, receiver_id, message):
        a = self.send_request({'to': receiver_id, 'from': self.clientId, 'type': MT_DATA, 'data': message})

    def send_all(self, message):
        a = self.send_request({'to': MR_ALL, 'from': self.clientId, 'type': MT_DATA, 'data': message})

    def send_exit(self):
        a = self.send_request({'to': MR_BROKER, 'from': self.clientId, 'type': MT_EXIT, 'data': ''})

    def process_messages_by_api(self):
        while True:
            a = self.send_request({'to': MR_BROKER, 'from': self.clientId, 'type': MT_GETDATA, 'data': ''})
            print("LogSendReq: ", a['from'])
            if int(a['type']) == MT_DATA:
                print("New message: " + a['data'] + "\nFrom: " + a['from'])
            else:
                time.sleep(1)

    def api_client(self):
        print("Python client has started")
        self.send_init()
        self.get_history()
        w = threading.Thread(target=self.process_messages_by_api)
        w.start()
        while True:
            print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit")
            menu = self.get_integer_input("Enter your choice:\n")
            if menu == 1:
                receiver_id = self.get_integer_input("Enter receiver's id:\n")
                message = input("Enter your message:\n")
                self.send(receiver_id, message)
            elif menu == 2:
                message = input("Enter your message:\n")
                self.send_all(message)
            elif menu == 3:
                self.send_exit()
                quit()
                break

def menu():
    while True:
        print("Choose interaction method:")
        print("1. API")
        print("2. Sockets")
        m = PythonClient().get_integer_input("Enter your choice:\n")
        if m == 1:
            APIClient().api_client()
        elif m == 2:
            SocketClient().socket_client()

menu()
