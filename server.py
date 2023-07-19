from threading import *
from socket import *
import re

host = '127.0.0.1'
port = 6969

server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
clientList = {}

def kick(arg):
    if arg == '':
        addToLog("Missing username.")
    else:
        try:
            value = clientList[arg]
            index = clients.index(value)
            clients.remove(value)
            value.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} has left the chat".encode("ascii"))
            addToLog(f"{nickname} has disconnected")
            nicknames.remove(nickname)
            broadcast(f"Admin kicked {arg}".encode('ascii'))
        except KeyError:
            addToLog("User not found.")

def help(arg):
    if arg == 'kick':
        addToLog("/kick [username] (case sensitive.)")
    elif arg == 'list':
        addToLog("/list all")
    elif arg == '':
        addToLog("kick, list")
    else:
        pass

def displayClients(arg):
    if arg == 'all':
        new_window = tk.Toplevel(app)
        new_window.title("List Items")
        
        list_label = tk.Label(new_window, text="Player usernames in server:")
        list_label.pack()
        
        def update_list():
            list_items.set(',\n'.join(nicknames))

        list_items = tk.StringVar()
        list_box = tk.Label(new_window, textvariable=list_items)
        list_box.pack()

        update_button = tk.Button(new_window, text="Update List", command=update_list)
        update_button.pack()

        update_list()

def callFunction():
    input_text = entry.get()
    entry.insert(0, "")
    pattern = r"/(\w+)\s*(.*)"

    match = re.match(pattern, input_text)

    if match:
        function_name = match.group(1)
        arguments = match.group(2)
        if function_name in functions_dict and callable(functions_dict[function_name]):
            functions_dict[function_name](arguments)
        else:
            addToLog(f"Function '{function_name}' not found or not callable.")
    else:
        addToLog(input_text)

def addToLog(text):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, text + '\n')
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

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
            addToLog(f"{nickname} has disconnected")
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
        addToLog(f"connetion from {address} with name of {nickname}")
        client.send("Connection established!".encode('ascii'))
        
        thread = Thread(target=handle, args=(client,))
        thread.start()

print("Server is live! Enjoy hosting.")
recieve_thread = Thread(target=recieve)
recieve_thread.start()

functions_dict = {
    "kick": kick,
    "list": displayClients,
    "help": help,
}

import tkinter as tk

app = tk.Tk()
icon = tk.PhotoImage(file = "icon.png")
app.iconphoto(False, icon)
app.title("Server - running")
app.geometry("500x200")

log_text = tk.Text(app, wrap=tk.WORD, state=tk.DISABLED)
log_text.grid(row=0, column=0, columnspan=2, sticky="nsew")

entry = tk.Entry(app)
entry.grid(row=1, column=0, sticky="ew")

button = tk.Button(app, text="Confirm", command=callFunction)
button.grid(row=1, column=1)

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

connected_users = []

app.mainloop()