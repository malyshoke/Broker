import threading
from dataclasses import dataclass
import time, json,os
from msg import * 

def ProcessMessages():
    while True:
        m = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if m.Header.Type == MT_DATA:
            print(f"Message: {m.Data}")
            data = []
            try:
                with open('msgstorage.json', 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                pass

            with open('msgstorage.json', 'w') as f:
                print("LogHeaderTo", m.Header.To)
                if m.Header.From == 50:
                    temp = {'all': m.Data}
                    print("New msg added to all")
                else:
                    temp = {str(m.Header.From): m.Data}
                    print(f"New msg added to {m.Header.From}")
                data.append(temp)
                json.dump(data, f)
               

        if m.Header.Type == MT_GETLAST:
            to = str(m.Header.From)
            with open('msgstorage.json', 'r') as f:
                data = json.load(f)
            personal_text = ""
            all_text = ""
            for item in data:
                for key, value in item.items():
                    if key == to:
                        personal_text += value
                        personal_text += ","
                    elif key == 'all':
                        all_text += value
                        all_text += ","
            personal_text = personal_text[:-1]
            all_text = all_text[:-1]

            Message.SendMessage(m.Header.From, MT_GETLAST, personal_text)
            if len(personal_text) == 0:
                print(f"No personal message to user {to}")
            else:
                print(f"Last personal msgs sent to {to}: {personal_text}")

            Message.SendMessage(m.Header.From, MT_GETLAST_PUBLIC, all_text)
            if len(all_text) == 0:
                print("No 'all' messages")
            else:
                print(f"Last 'all' msgs sent to {to}: {all_text}")

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

