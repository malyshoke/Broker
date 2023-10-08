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

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


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
            std::chrono::duration<double> seconds = std::chrono::steady_clock::now() - session.second->lastInteraction;
            if (seconds.count() >= 5)
            {
                del = session.first;
            }
        }
        if (del != 0) {
            cout << "Session " + to_string(del) + " deleted\n";
            sessions.erase(del);
        }
    }



    void Server::IsActive()
    {
        while (true)
        {
            std::vector<int> allIds(sessions.size());
            for (auto& [id, session] : sessions)
            {
                allIds.push_back(id);
            }

            for (int id : allIds)
            {
                auto sessionIt = sessions.find(id);

                if (sessionIt != sessions.end() && !(sessionIt->second->stillActive()))
                {
                    cout << "Time out. Client " << id << " disconnected" << endl;
                    sessions.erase(sessionIt);
                }
            }
            Sleep(100);
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
            auto session = make_shared<Session>(++maxID, m.data, std::chrono::steady_clock::now()); 
            sessions[session->id] = session;
            cout << "Client " << session->id << " connected\n"; 
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
            auto iSession = sessions.find(m.header.from); 

            if (iSession != sessions.end())
            {
                iSession->second->lastInteraction = std::chrono::steady_clock::now();
                iSession->second->send(s);

            }
            else
            {
            }
            break;
        }
        default:
        {
            Sleep(100);
            auto iSessionFrom = sessions.find(m.header.from); 
            if (iSessionFrom != sessions.end())
            {
                iSessionFrom->second->lastInteraction = std::chrono::steady_clock::now();
                auto iSessionTo = sessions.find(m.header.to); 
                if (iSessionTo != sessions.end())
                {
                    iSessionTo->second->add(m); 
                    cout << "Message delivered successfully\n";
                    iSessionTo->second->lastInteraction = std::chrono::steady_clock::now();
                }
                else if (m.header.to == MR_ALL)
                {
                    for (auto& [id, session] : sessions)
                    {
                        if (id != m.header.from) {
                            session->lastInteraction = std::chrono::steady_clock::now();
                            session->add(m);
                        }
                    }
                    cout << "Message delivered successfully\n";
                }
                else cout << "Message not delivered\n";
            }
            break;
        }
        }
    }
    void RunServer() {
       
        thread clientConnection(&Server::IsActive, this);
        clientConnection.detach(); 
        
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
          
        }
    }

private:
    int maxID; 
    map<int, shared_ptr<Session>> sessions; 
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