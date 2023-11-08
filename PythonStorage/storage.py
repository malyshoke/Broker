import threading
from dataclasses import dataclass
import time, json,os
from msg import * 

def ProcessMessages():
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if (m.Header.Type == MT_DATA):
            print(f"Message: {m.Data}")
            data = []
            try:
                with open('msgstorage.json', 'r') as f:
                    data = json.load(f)
            except:
                with open('msgstorage.json', 'w') as f:
                    pass

            with open('msgstorage.json', 'w') as f:
                temp = {m.Header.From: m.Data}
                data.append(temp)
                json.dump(data, f)
                print(f"New msg added to {m.Header.From}")

        if (m.Header.Type == MT_GETLAST):
            to = str(m.Header.From)
            with open('msgstorage.json', 'r') as f:
                data = json.load(f)
            text = ""
            for item in data:
                for key, value in item.items():
                    if (key == to):
                        text += value
                        text += ","
            text = text[:-1]
            Message.SendMessage(m.Header.From, MT_GETLAST, text)
            if (len(text) == 0):
                print(f"No message to user {to}")
            else:
                print(f"Last msgs sent to {to}: {text}")
        else:
            time.sleep(1)

        
def Storage():
    print("Storage has started")
    Message.SendMessage(MR_BROKER, MT_INITSTORAGE)
    t = threading.Thread(target=ProcessMessages)
    t.start()
    while True:
        time.sleep(1)             
        
Storage()

