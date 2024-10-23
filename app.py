import threading
import paramiko
import socket
from flask import Flask

# Initialize Flask web service
app = Flask(__name__)

# Web route for HTTP
@app.route('/')
def hello_world():
    return 'Hello from the web service!'

# SSH server functionality
class SSHServer(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == 'admin' and password == 'password':  # Adjust credentials as needed
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def start_ssh_server(self, host="0.0.0.0", port=2200):
        try:
            # SSH server setup
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(100)

            print(f"SSH Server listening on {host}:{port}")

            while True:
                client, addr = server_socket.accept()
                print(f"Connection from {addr}")

                transport = paramiko.Transport(client)
                transport.add_server_key(paramiko.RSAKey.generate(2048))

                ssh_server = SSHServer()

                try:
                    transport.start_server(server=ssh_server)
                except paramiko.SSHException:
                    print("SSH negotiation failed")
                    continue

                channel = transport.accept(20)
                if channel is None:
                    print("No channel")
                    continue

                channel.send("Welcome to the SSH server!\n")
                while True:
                    data = channel.recv(1024)
                    if not data:
                        break
                    channel.send(data)  # Echo back the received data
                channel.close()

        except Exception as e:
            print(f"SSH Server error: {str(e)}")

# Start SSH server in a separate thread
def run_ssh_server():
    ssh_server = SSHServer()
    ssh_server.start_ssh_server()

if __name__ == "__main__":
    # Start the SSH server in a separate thread
    threading.Thread(target=run_ssh_server).start()

    # Start the Flask web service
    app.run(host='0.0.0.0', port=5000)
