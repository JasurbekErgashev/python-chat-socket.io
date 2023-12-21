import socket
import threading

# Server configuration
HOST = "127.0.0.1"
PORT = 5556

# Socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Dictionary to store client sockets and their usernames
clients = {}


def handle_client(client_socket, addr):
    # Receive and set the username
    username = client_socket.recv(1024).decode("utf-8")
    clients[client_socket] = username

    # Broadcast new user joining
    broadcast(f"{username} has joined the chat.", client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                remove_client(client_socket)
                break
            broadcast(f"{username}: {message}", client_socket)
        except:
            continue


def broadcast(message, sender_socket):
    for client, username in clients.items():
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except:
                remove_client(client)


def remove_client(client_socket):
    if client_socket in clients:
        username = clients[client_socket]
        broadcast(f"{username} has left the chat.", client_socket)
        del clients[client_socket]


# Accept and handle incoming connections
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection established with {addr}")
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
