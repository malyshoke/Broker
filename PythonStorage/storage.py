import threading
from dataclasses import dataclass
import time, json,os
from msg import * 

def ProcessMessages():
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if (m.Header.Type == MT_DATA):
            print(f"Message: {m.Data}")
            print(f"To: {m.Header.To}")
            print(f"From: {m.Header.From}")
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
            print("Last sent message")
            print(f"Message: {m.Data}")
            print(f"To: {m.Header.To}")
            print(f"From: {m.Header.From}")
            taker = str(m.Header.From)
            with open('msgstorage.json', 'r') as f:
                data = json.load(f)
            text = ""
            for item in data:
                for key, value in item.items():
                    if (key == taker):
                        text += value
                        text += ","
            text = text[:-1]
            Message.SendMessage(m.Header.From, MT_GETLAST, text)
            print(f"Last msgs sent to {taker}: {text}\n")
        else:
            time.sleep(1)

        
def Storage():
    print("Storage has started\n")
    Message.SendMessage(MR_BROKER, MT_INITSTORAGE)
    t = threading.Thread(target=ProcessMessages)
    t.start()
    while True:
        time.sleep(1)             
        
Storage()

