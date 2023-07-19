from threading import *
from socket import *

host = '127.0.0.1'
port = 6969

server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
clientList = {}

def AdminControls():
    while True:
        command = input("Enter command: ")
        if command == '/kick':
            userToKick = input("Which user do you want to kick: ")
            if userToKick:
                value = clientList[userToKick]
                value.close()
            else:
                pass
        elif command == '/ban':
            userToABan = input("Which user do you want to ban: ")
        elif command == '/list':
            for e in nicknames:
                print(e)
def broadcast(message):
    for c in clients:
        c.send(message)
        
def handle(client):
    while True:
        try:
            message = client.recv(512)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} has left the chat".encode("ascii"))
            nicknames.remove(nickname)
            break
        
def recieve():
    while True:
        client, address = server.accept()
        
        client.send("NICK".encode('ascii'))
        nickname = client.recv(512).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)
        clientList.update({nickname:client})
        
        broadcast(f"{nickname} has joined the chat.".encode('ascii'))
        client.send("Connection established!".encode('ascii'))
        
        thread = Thread(target=handle, args=(client,))
        thread.start()
        




print("Server is live! Enjoy hosting.")
recieve_thread = Thread(target=recieve)
recieve_thread.start()
admin_thread = Thread(target=AdminControls)
admin_thread.start()