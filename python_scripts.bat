@echo off
chcp 1251 > nul
cd /d "D:\Рабочий стол\Учеба\7 семестр\TRIS\MsgSockets"

start cmd /k python "PythonStorage\storage.py"
start cmd /k python "PythonRestClient\RestServer.py"
start cmd /k python "PythonClient\client2.py"
start cmd /k python "PythonWebClient\client.py"

pause
