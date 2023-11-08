import requests
from message import *

class Session:
    id = 0
    def __init__(self):
        r = requests.get("http://127.0.0.1:5000/api/init")
        data = r.json()
        if (data.get('To') != '0'):
            Session.id = data.get('To')
            print(f"Welcome user: {Session.id}")
        else:
            print("Error")

    def send(self, To, Type, Data = None):
        payload = {'to': To, 'from': Session.id, 'type': Type, 'data': Data}
        r = requests.post("http://127.0.0.1:5000/api/send", json=payload, headers=None)
        
    def getData():
        r = requests.get(f"http://127.0.0.1:5000/api/getData/{Session.id}")
        data = r.json()
        m = Message(data.get('To'), data.get('From'), data.get('Type'), data.get('Data'))
        return m

    def getLast(self):
        r = requests.get(f"http://127.0.0.1:5000/api/getLast/{Session.id}")

    
    def __del__(self):
        r = requests.get(f"http://127.0.0.1:5000/api/exit/{Session.id}")