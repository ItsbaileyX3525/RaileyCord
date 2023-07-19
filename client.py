from socket import *
from threading import *
import sys

while True:
    nickname = input("Enter a username: ")
    if ' ' in nickname:
        print("Username can't have spaces")
        continue
    else:
        break

client = socket(AF_INET, SOCK_STREAM)
try:
    client.connect(("127.0.0.1", 6969))
except:
    print("There was a problem establishing a connection to the server.")
    sys.exit()
    

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
        message = f"{nickname} > {input(f'>>> ')}"
        client.send(message.encode('ascii'))

        
recieve_thread = Thread(target=recieve)
recieve_thread.start()

write_thread = Thread(target=write)
write_thread.start()