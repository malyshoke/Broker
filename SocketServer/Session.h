#pragma once
#include <string>
#include <queue>
#include <afxmt.h> 
#include <chrono>

class Session
{
public:
    int id;
    string name;
    queue<Message> messages;
    std::chrono::steady_clock::time_point lastInteraction;

    CCriticalSection cs;
    Session(int _id, string _name, std::chrono::steady_clock::time_point _lastInteraction)
        : id(_id), name(_name), lastInteraction(_lastInteraction)
    {
    }

    Session(int _id, std::chrono::steady_clock::time_point _lastInteraction)
        :id(_id), lastInteraction(_lastInteraction)
    {
    }

    bool stillActive()
    {
        if (this->inActivity() > 10000)
            return false;
        else
            return true;
    }

    int inActivity()
    {
        auto now = std::chrono::steady_clock::now();
        auto intMilliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastInteraction);
        return static_cast<int>(intMilliseconds.count());
    }

    void add(Message& m)
    {
        CSingleLock lock(&cs, TRUE);
        messages.push(m);
    }

    void send(CSocket& s)
    {
        CSingleLock lock(&cs, TRUE);
        if (messages.empty())
        {
            Message::send(s, id, MR_BROKER, MT_NODATA);
        }
        else
        {
            messages.front().send(s);
            messages.pop();
        }
    }

    void printContents() {
        cout << endl;
        cout << "Session ID: " << id << endl;
        cout << "Messages:" << endl;
        while (!messages.empty()) {
            Message msg = messages.front();
            cout << "Message: " << msg.clientID << endl << "Data:" << msg.data << endl;
            messages.pop();
        }
    }
};
