import json
from flask import Flask, jsonify, request, Response
from msg import *

app = Flask(__name__)

@app.route('/api/init', methods=['GET'])
def init():
    m = Message.SendMessage(MR_BROKER, MT_INIT)
    return jsonify( To = m.Header.To, 
                    From = m.Header.From,
                    Type = m.Header.Type,
                    Data = m.Data)

@app.route('/api/getLast/<int:id>', methods=['GET'])
def getLast(id):
    m = Message.SendMessageFrom(MR_BROKER, id, MT_GETLAST)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/api/getData/<int:id>', methods=['GET'])
def getData(id):
    m = Message.SendMessageFrom(MR_BROKER, id, MT_GETDATA)
    return jsonify( To = m.Header.To, 
                    From = m.Header.From,
                    Type = m.Header.Type,
                    Data = m.Data,)
    
@app.route('/api/send', methods=['POST'])
def send():
    m = json.loads(request.data)
    Message.SendMessageFrom(m.get('to'),
                            m.get('from'),
                            m.get('type'),
                            m.get('data'))
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/api/exit/<int:id>', methods=['GET'])
def exit(id):
    Message.SendMessageFrom(MR_BROKER, int(id), MT_EXIT)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run(debug=True)
