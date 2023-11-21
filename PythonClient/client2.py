import threading
import socket, struct, time
from msg import *
import cgi
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

clientId = 0
clientmsg = ''

def SendRequest(params):
    URL = "http://localhost:8989"
    r = requests.get(url=URL, json=params)
    return r.json()

def ProcessMessagesByAPI():
    global clientId
    while True:
        a = SendRequest({'to':MR_BROKER, 'from':clientId, 'type': MT_GETDATA, 'data':''})
        if int(a['type']) == MT_DATA:
            print("New message: " + a['data'] + "\nFrom: " + a['from'])
        else:
            time.sleep(1)

def ProcessMessagesbySockets():
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if m.Header.Type == MT_DATA:
            print(f"You got a message: {m.Data}")
            print(f"From: {m.Header.From}")
        else:
            time.sleep(1)

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

def SocketClient():
    print("Client has started\n")
    Message.SendMessage(MR_BROKER, MT_INIT)
    t = threading.Thread(target=ProcessMessagesbySockets)
    t.start() 
    while True:
        print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit")
        menu = get_integer_input("Enter your choice:\n")
        if menu == 1:
            receiver_id = get_integer_input("Enter receiver's id:\n")
            message = input("Enter your message:\n")
            Message.SendMessage(receiver_id, MT_DATA, message)
        elif menu == 2:
            message = input("Enter your message:\n")
            Message.SendMessage(MR_ALL, MT_DATA, message)
        elif menu == 3:
            Message.SendMessage(MR_BROKER, MT_EXIT)
            quit()
            break

def APIClient():
        global clientId
        print("Python client has started")
        SendInit()
        GetHistory()
        w = threading.Thread(target=ProcessMessagesByAPI)
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

def menu():
    while True:
        print("Choose interaction method:")
        print("1. API")
        print("2. Sockets")
        m = get_integer_input("Enter your choice:\n")
        if m == 1:
            APIClient()
        elif m == 2:
            SocketClient()

menu()