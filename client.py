
import socket
import ssl
import threading

class C2Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.setup_client()
    
    def setup_client(self):
        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Wrap the socket with SSL for encryption
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile="ca-cert.pem")
        self.secure_socket = context.wrap_socket(self.client_socket, server_hostname=self.host)
        
        # Connect to the server
        try:
            self.secure_socket.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.send_messages()
        except Exception as e:
            print(f"Error connecting to server: {e}")
    
    def receive_messages(self):
        while True:
            try:
                data = self.secure_socket.recv(1024)
                if data:
                    print(f"Received: {data.decode()}")
                else:
                    break
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    
    def send_messages(self):
        while True:
            try:
                message = input("Enter command: ")
                if message.lower() == "quit":
                    break
                self.secure_socket.send(message.encode())
            except Exception as e:
                print(f"Error sending data: {e}")
                break
        self.secure_socket.close()

if __name__ == "__main__":
    host = '127.0.0.1'  # Change this to the server's IP address
    port = 4444
    client = C2Client(host, port)



