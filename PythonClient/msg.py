import threading
from dataclasses import dataclass
import socket, struct, time

MT_INIT		= 0
MT_EXIT		= 1
MT_GETDATA	= 2
MT_DATA		= 3
MT_NODATA	= 4
MT_CONFIRM	= 5

MR_BROKER	= 10
MR_ALL		= 50
MR_USER		= 100


@dataclass
class MsgHeader:
	To: int = 0
	From: int = 0
	Type: int = 0
	Size: int = 0

	def Send(self, s): #второй передаваемый параметр - это сокет
		s.send(struct.pack(f'iiii', self.To, self.From, self.Type, self.Size)) #все параметры кроме первого упаковываются, берутся 4 целых числа и упаковываются

	def Receive(self, s):
		try:
			(self.To, self.From, self.Type, self.Size) = struct.unpack('iiii', s.recv(16)) #16 байтов из сокета интерпретируем как 4 целых числа, получаем кортеж
		except:
			self.Size = 0
			self.Type = MT_NODATA

class Message:
	ClientID = 0

	def __init__(self, To = 0, From = 0, Type = MT_DATA, Data=""):
		self.Header = MsgHeader(To, From, Type, len(Data))
		self.Data = Data

	def Send(self, s):
		self.Header.Send(s)
		if self.Header.Size > 0:
			s.send(struct.pack(f'{self.Header.Size}s', self.Data.encode('cp866'))) #формируем строчку опеределенной длины и посылаем ее

	def Receive(self, s):
		self.Header.Receive(s)
		if self.Header.Size > 0:
			self.Data = struct.unpack(f'{self.Header.Size}s', s.recv(self.Header.Size))[0].decode('cp866') #читаем из сокета кол-во байт, указанных в header, распаковываем и конвертируем нулевой элемент во внутреннюю строку

	def SendMessage(To, Type = MT_DATA, Data=""):
		HOST = 'localhost'
		PORT = 12435
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, PORT))
			m = Message(To, Message.ClientID, Type, Data)
			if m.Header.From == m.Header.To:
				print("You have entered your id")
			else:
				m.Send(s)
				m.Receive(s)
				if m.Header.Type == MT_INIT:
					Message.ClientID = m.Header.To
					print("clientID is " + str(m.Header.To))
				return m

