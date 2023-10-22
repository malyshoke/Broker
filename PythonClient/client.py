import threading
from dataclasses import dataclass
import socket, struct, time
from msg import *


def ProcessMessages():
	while True:
		m = Message.SendMessage(MR_BROKER, MT_GETDATA)
		if m.Header.Type == MT_DATA:
            print(f"You got a message: {m.Data}\nFrom: {m.Header.From}")
			print(m.Data)
		else:
			time.sleep(1)


def Client():
    print("Client has started\n")
	Message.SendMessage(MR_BROKER, MT_INIT)
	t = threading.Thread(target=ProcessMessages)
	t.start()
	while True:
        print("Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit")
        number = int(input())
        if menu == 1:
            print("Enter receiver's id")
            id = int(input())
            print("Enter your message")
            message = input()
            Message.SendMessage(id, MT_DATA, message)
        elif menu == 2:
            print("Enter your message")
            message = input()
            Message.SendMessage(MR_ALL, MT_DATA, message)
        elif menu == 3:
            Message.SendMessage(MR_BROKER, MT_EXIT)
            quit()
            break
		Message.SendMessage(MR_ALL, MT_DATA, input())

Client()
