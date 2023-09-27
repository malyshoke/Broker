#include "pch.h"
#include "framework.h"
#include "SocketServer.h"
#include "Message.h"
#include "Session.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

#include "pch.h"
#include "framework.h"
#include "SocketServer.h"
#include "Message.h"
#include "Session.h"
#include <thread>
#include <map>
#include <queue>
#include <iostream>
#include <ctime>
#include <chrono>
#include <mutex>
#include "pch.h"
#include "framework.h"
#include "SocketServer.h"
#include "Message.h"
#include "Session.h"
#include <thread>
#include <map>
#include <queue>
#include <iostream>
#include <ctime>
#include <chrono>
#include <mutex>

class Server {
public:
    Server() : maxID(MR_USER) {}

    void LaunchClient() {
        STARTUPINFO si = { sizeof(si) };
        PROCESS_INFORMATION pi;
        CreateProcess(NULL, (LPSTR)"SocketClient.exe", NULL, NULL, TRUE, CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi);
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
    }

    void CheckClients() {
        int del = 0;
        for (auto& session : sessions)
        {
            std::chrono::duration<double> elapsed_seconds = std::chrono::high_resolution_clock::now() - session.second->lastInteraction;
            if (elapsed_seconds.count() >= 5)
            {
                session.second->lastInteraction = std::chrono::high_resolution_clock::now();
                del = session.first;
            }
        }
        if (del != 0) {
            cout << "Session " + to_string(del) + " deleted\n";
            sessions.erase(del);
        }
    }

    void ProcessClient(SOCKET hSock) {
        CSocket s;
        s.Attach(hSock);
        Message m;
        int code = m.receive(s);
        switch (code)
        {
        case MT_INIT:
        {
            auto session = make_shared<Session>(++maxID, m.data, std::chrono::high_resolution_clock::now()); //создание сессии
            sessions[session->id] = session;
            cout << "Client " << session->id << " connected\n"; //сообщение о присвоении id
            Message::send(s, session->id, MR_BROKER, MT_INIT);
            break;
        }
        case MT_EXIT:
        {
            cout << "Client " + to_string(m.header.from) + " disconnected\n";
            sessions.erase(m.header.from);
            Message::send(s, m.header.from, MR_BROKER, MT_CONFIRM);
            break;
        }
        case MT_GETDATA:
        {
            auto iSession = sessions.find(m.header.from); //поиск сессии

            if (iSession != sessions.end())
            {
                iSession->second->lastInteraction = std::chrono::high_resolution_clock::now();
                iSession->second->send(s);

            }
            break;
        }
        default:
        {
            cout << "Message has been sent\n";
            Sleep(100);
            auto iSessionFrom = sessions.find(m.header.from); //отправитель
            if (iSessionFrom != sessions.end())
            {
                iSessionFrom->second->lastInteraction = std::chrono::high_resolution_clock::now();
                auto iSessionTo = sessions.find(m.header.to); //получатель
                if (iSessionTo != sessions.end())
                {
                    iSessionTo->second->add(m); //кладем в очередь
                    iSessionTo->second->lastInteraction = std::chrono::high_resolution_clock::now();
                }
                else if (m.header.to == MR_ALL)
                {
                    for (auto& [id, session] : sessions)
                    {
                        if (id != m.header.from) {
                            session->lastInteraction = std::chrono::high_resolution_clock::now();
                            session->add(m);
                        }
                    }
                }
            }
            break;
        }
        }
    }

    void RunServer() {
        AfxSocketInit();

        CSocket Server;
        Server.Create(12435);

        for (int i = 0; i < 3; ++i)
        {
            LaunchClient();
        }

        while (true)
        {
            if (!Server.Listen())
                break;
            CSocket s;
            Server.Accept(s);
            thread t(&Server::ProcessClient, this, s.Detach());
            t.detach();
            thread c(&Server::CheckClients, this);
            c.detach();
        }
    }

private:
    int maxID; //id макс клиента
    map<int, shared_ptr<Session>> sessions; //все сессии и id
};

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
                Server Server;
                Server.RunServer();
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