import cgi
import threading
from dataclasses import dataclass
import socket, struct, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from msg import *
import requests

clientId = 0
clientmsg = ''

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def get_integer_input(prompt):
    while True:
        user_input = input(prompt)
        if is_integer(user_input):
            return int(user_input)
        else:
            print("Enter number")

def ProcessMessages():
    global clientId
    while True:
        a = SendRequest({'to':MR_BROKER, 'from':clientId, 'type': MT_GETDATA, 'data':''})
        if int(a['type']) == MT_DATA:
            print("New message: " + a['data'] + "\nFrom: " + a['from'])
        else:
            time.sleep(1)


def SendRequest(params):
    URL = "http://localhost:8989"
    r = requests.get(url=URL, json=params)
    return r.json()

def GetHistory():
    global clientId
    a = SendRequest({'to': MR_BROKER, 'from': clientId, 'type': MT_GETLAST, 'data': ""})

def SendInit():
    global clientId
    id = SendRequest({'to':MR_BROKER, 'from':'', 'type': MT_INIT, 'data':''})
    clientId = int(id['to'])
    print("Client ID is " + str(clientId))

def Send(id, message):
    global clientId
    a = SendRequest({'to':id, 'from':clientId, 'type': MT_DATA, 'data':message})

def SendAll(message):
    global clientId
    a = SendRequest({'to': MR_ALL, 'from': clientId, 'type': MT_DATA, 'data': message})

def SendExit():
    global clientId
    a = SendRequest({'to': MR_BROKER, 'from': clientId, 'type': MT_EXIT, 'data': ''})

def Client():
        global clientId
        print("Python client has started")
        SendInit()
        GetHistory()
        w = threading.Thread(target=ProcessMessages)
        w.start()
        while True:
            print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit")
            menu = get_integer_input("Enter your choice:\n")
            if menu == 1:
                receiver_id = get_integer_input("Enter receiver's id:\n")
                message = input("Enter your message:\n")
                Send(receiver_id, message)
            elif menu == 2:
                message = input("Enter your message:\n")
                SendAll(message)
            elif menu == 3:
                SendExit()
                quit()
                break

Client()
