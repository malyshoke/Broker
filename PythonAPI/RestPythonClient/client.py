import json
from Session import *
import threading
import time
from message import *

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
    while True:
        m = Session.getData()
        if m.Type == MT_DATA:
            print(f"You got a message: {m.Data}")
            print(f"From: {m.From}")
        elif m.Type == MT_GETLAST:
            if(len(m.Data) > 0 ):
                print(f"{m.Data}")
        else:
            time.sleep(2)
        
def Client():
    s = Session()
    t = threading.Thread(target=ProcessMessages)
    t.start()             
    while True:
        print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Get last message\n4. Exit")
        menu = get_integer_input("Enter your choice:\n")
        if menu == 1:
            receiver_id = get_integer_input("Enter receiver's id:\n")
            message = input("Enter your message:\n")
            s.send(int(receiver_id), MT_DATA, message)

        elif menu == 2:
            message = input("Enter your message:\n")
            s.send(MR_ALL, MT_DATA, message)

        elif menu == 3:
            s.getLast()
            
        elif menu == 4:
            break


Client()