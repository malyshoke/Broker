#!/usr/bin/env python3

import cgi, pickle, cgitb, codecs, sys, datetime, os, html
from msg import *
class ProcessMessages:
 def __init__(self, form):
        self.req = form
        id = form.getfirst("id", "none")
        self.id = html.escape(id)
        to = form.getfirst("to", "none")
        self.to = html.escape(to)
        msg = form.getfirst("msg", "")
        self.msg = html.escape(msg)

	Message.ClientID = int(id)
	Message.SendMessage(MR_BROKER, MT_INIT)
        if (Message.ClientID == "none"):
            print(f"""
                <html>
                <body> """)
            print(f"<h1>No user with id {self.id}!</h1>")
            print("<a href='/'>Go back</a>")
            print("</body></html>")
        else:
            if (msg != "" and self.to != "none"):
                Message.SendMessage(int(self.to), MT_DATA, msg)
            if (msg != "" and self.to == "none"):
                Message.SendMessage(MR_ALL, MT_DATA, msg)
            try:
                self.printHeader()
                self.printBody()
                self.load()
                self.printFooter()
            except Exception as e:
                print(e)

def load(self):
        m = Message.SendMessage(MR_BROKER, MT_GETLAST)
        ms = Message.SendMessage(MR_BROKER, MT_GETDATA)
        if (ms.Header.Type == MT_GETLAST and ms.Header.From == MR_BROKER):
            print("<br>")
            print("<textarea rows=10 cols=50 wrap=virtual >")
            print(f"{ms.Data}")
            print("</textarea>")

def printHeader(self):
        print("Content-type: text/html\n")
        print("""<!DOCTYPE HTML>
            <html>
            <head>
                <meta charset="utf-8">
                <title>New Year's Chat</title>
            </head>
            <body>""")

    def printBody(self):
        print(f"<h2>Client {Message.ClientID}</h2>")
        print(f"""<form action="/cgi-bin/handler.py">
                    <p>Enter ID 50 to send message to all users</p>
                     <ul>
                        <li>
                          <label for="to">To Client:</label>
                          <input type="text" id="to" name="to" value="50">
                          <br>
                        </li>
                        <li>
                          <label for="msg">Message:</label>
                          <textarea id="msg" name="msg"></textarea>
                          <input type="hidden" name="id" value ="{Message.ClientID}">
                        <input type="submit" value="Send">
                        </li>
                    </ul>

                </form>""")

    def printFooter(self):
        print("""</body>
            </html>""")


def main():
    form = cgi.FieldStorage()
    msg = msgLogic(req)


main()
