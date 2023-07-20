from socket import *
from threading import *
import sys

client = socket(AF_INET, SOCK_STREAM)
try:
    client.connect(("127.0.0.1", 6969))
except:
    print("There was a problem establishing a connection to the server.")
    sys.exit()

isBanned = client.recv(2048).decode('ascii')
takenNames = client.recv(2048).decode('ascii')

if isBanned == 'False':
    while True:
        nickname = input("Enter a username: ")
        if ' ' in nickname or nickname in takenNames:
            print("Invalid username")
            continue
        else:
            break
else:
    print("Sorry you have been IP banned from this server")

def recieve():
    while True:
        try:
            message = client.recv(512).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("Oops, there was an error.")
            client.close()
            break
        
def write():
    while True:
        message = f"{nickname} > {input(f'')}"
        client.send(message.encode('ascii'))

if isBanned == 'False':
    recieve_thread = Thread(target=recieve)
    recieve_thread.start()

    write_thread = Thread(target=write)
    write_thread.start()