// SocketClient.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "pch.h"
#include "framework.h"
#include "../SocketServer/Message.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


void ProcessMessages()
{
	while (true)
	{
		Message m = Message::send(MR_BROKER, MT_GETDATA);
		switch (m.header.type)
		{
		case MT_DATA:
			cout << "You got a message: " << m.data << endl << "From: " << to_string(m.header.from) << endl;
		default:
			Sleep(100);
			break;
		}
	}
}

void Client()
{
	AfxSocketInit();
	cout << "Client has started\n";
	thread t(ProcessMessages);
	t.detach();

	Message m = Message::send(MR_BROKER, MT_INIT);
	while (true) {
		cout << "Menu:\n1. Choose receiver\n2. Broadcast message\n3. Exit\n";
		int number;
		cin >> number;
		switch (number)
		{
		case 1: {
			cout << "Enter receiver's id\n";
			int to;
			cin >> to;
			Message m;
			if (to == m.clientID) {
				cout << "You have entered your id\n";
				break;
			}
			else {
				cout << "Enter your message\n";
				string str;
				cin >> str;
				Message::send(to, MT_DATA, str);
				cout << "Message sent successfully\n";
				break;
			}
		}
		case 2: {
			cout << "Enter your message\n";
			string str;
			cin >> str;
			Message::send(MR_ALL, MT_DATA, str);
			cout << "Message sent successfully \n";
			break;
		}
		case 3: {
			Message m = Message::send(MR_BROKER, MT_EXIT);
			exit(0);
			break;
		}
		}
	}
}

CWinApp theApp;

int main()
{
	int nRetCode = 0;

	HMODULE hModule = ::GetModuleHandle(nullptr);

	if (hModule != nullptr)
	{
		// initialize MFC and print and error on failure
		if (!AfxWinInit(hModule, nullptr, ::GetCommandLine(), 0))
		{
			// TODO: code your application's behavior here.
			wprintf(L"Fatal Error: MFC initialization failed\n");
			nRetCode = 1;
		}
		else
		{
			Client();
		}
	}
	else
	{
		// TODO: change error code to suit your needs
		wprintf(L"Fatal Error: GetModuleHandle failed\n");
		nRetCode = 1;
	}

	return nRetCode;
}
