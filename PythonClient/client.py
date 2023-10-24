import threading
from dataclasses import dataclass
import socket, struct, time
from msg import *

def ProcessMessages():
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if m.Header.Type == MT_DATA:
            print(f"You got a message: {m.Data}")
            print(f"From: {m.Header.From}")
        else:
            time.sleep(1)

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

def Client():
    print("Client has started\n")
    Message.SendMessage(MR_BROKER, MT_INIT)
    t = threading.Thread(target=ProcessMessages)
    t.start() #поток работает на прием
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

Client()
