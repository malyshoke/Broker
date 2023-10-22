import threading
from dataclasses import dataclass
import socket, struct, time
from msg import *


def ProcessMessages():
	while True:
		m = Message.SendMessage(MR_BROKER, MT_GETDATA)
		if m.Header.Type == MT_DATA:
			print(m.Data)
		else:
			time.sleep(1)


def Client():
	Message.SendMessage(MR_BROKER, MT_INIT)
	t = threading.Thread(target=ProcessMessages)
	t.start()
	while True:
		Message.SendMessage(MR_ALL, MT_DATA, input())

Client()
