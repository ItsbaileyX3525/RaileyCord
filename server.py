from threading import *
from socket import *
import re
import sys

host = '127.0.0.1'
port = 6969

server=None
def startServer():
    global server
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    recieve_thread = Thread(target=recieve)
    recieve_thread.start()

clients = []
nicknames = []
clientList = {}
IPList = {}
blacklist = []

with open('blacklist.txt', 'r') as file:
    for line in file:
        ip = line.strip()
        blacklist.append(ip)

def kick(arg=None, reason=None):
    if arg == ' ' or arg == None:
        addToLog("Missing username.")
    else:
        try:
            value = clientList[arg]
            index = clients.index(value)
            nickname = nicknames[index]
            value.close()
            addToLog(f"Kicked {nickname} successfully.")
            if reason != None:
                broadcast(f"Admin kicked {arg} for {reason}".encode('ascii'))
            else:
                broadcast(f"Admin kicked {arg}".encode('ascii'))
        except KeyError as e:
            addToLog(f"User {e} not found.")
            
def ban(arg=None):
    if arg == ' ' or arg == None:
        addToLog("Missing username")
    else:
        try:
            value = clientList[arg]
            ip = IPList[arg]
            index = clients.index(value)
            nickname = nicknames[index]
            value.close()
            with open('blacklist.txt', 'w') as file:
                file.write(ip)
            addToLog("Kicked banned.")
            broadcast(f"User {nickname} has been banned!".encode("ascii"))
        except KeyError as e:
            addToLog(f"User {e} not found.")

def help(arg=None):
    if arg == 'kick':
        addToLog("/kick [username] (case sensitive.)")
        addToLog("Kicks client/player from server")
    elif arg == 'list':
        addToLog("/list all, username")
        addToLog("Lists players and their info")
    elif arg == '' or arg == None:
        addToLog("kick, ban, list, stop, start, update")
    else:
        pass

def stop(arg=None):
    global server
    if arg == None or arg == ' ':
        for client in clients:
            client.close()
        server.close()
        server = None
        app.title("Server - standing by")
        addToLog("Server stopped.")
    else:
        addToLog("Arguments not required. Please remove them.")

def start(arg=None):
    if arg == None or arg == ' ':
        startServer()
        app.title("Server - running")
        addToLog("Server started.")
    else:
        addToLog("Arguments not required. Please remove them.")

def update(arg=None):
    global blacklist
    if arg == None or arg == ' ':
        addToLog("blacklist")
    elif arg == 'blacklist':
        blacklist = []
        with open('blacklist.txt', 'r') as file:
            for line in file:
                ip = line.strip()
                blacklist.append(ip)

def say(arg=None):
    broadcast(f"Admin: {arg}".encode('ascii'))
    print(arg)
    addToLog(f"Said {arg} to {len(clients)} clients.")

def displayClients(arg=None):
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
    elif arg == ' ' or arg == None:
        addToLog("all, username")

def callFunction():
    input_text = entry.get()
    entry.delete(0, "end") 
    pattern = r"/(\w+)\s*(\"[^\"]*\"|\S*)"

    match = re.match(pattern, input_text)

    if match:
        function_name = match.group(1)
        raw_argument = match.group(2)

        if raw_argument.startswith('"') and raw_argument.endswith('"'):
            argument = raw_argument[1:-1]
        else:
            argument = raw_argument

        if argument == '' or argument == ' ':
            argument=None
        try:
            if function_name in functions_dict and callable(functions_dict[function_name]):
                addToLog(input_text)
                functions_dict[function_name](argument)
            else:
                addToLog(f"Command '{function_name}' not found.")
        except TypeError:
            addToLog(input_text)
            functions_dict[function_name]
    else:
        addToLog(input_text)

def addToLog(text):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, text + '\n')
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)

def broadcast(message):
    try:
        for c in clients:
            c.send(message)
    except OSError:
        pass
        
def handle(client):
    while server != None:
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
    sys.exit()
        
def recieve():
    while server != None:
        try:
            client, address = server.accept()
            if address[0] in blacklist:
                client.send(f"True".encode('ascii'))
                addToLog(F"banned address of {address} tried to join.")
                client.close()
            else:
                client.send(f"False".encode('ascii'))
                client.send(f"{nicknames}".encode('ascii'))
                client.send("NICK".encode('ascii'))
                nickname = client.recv(512).decode('ascii')
                nicknames.append(nickname)
                clients.append(client)
                clientList.update({nickname:client})
                IPList.update({nickname:address[0]})
            
                broadcast(f"{nickname} has joined the chat.".encode('ascii'))
                addToLog(f"connetion from {address} with name of {nickname}")
                client.send("Connection established!".encode('ascii'))
                thread = Thread(target=handle, args=(client,))
                thread.start()  
        except:
            print("Exception happened, probably ok")
            sys.exit()
    sys.exit()

functions_dict = {
    "kick": kick,
    "list": displayClients,
    "help": help,
    "stop": stop,
    "start": start,
    "ban": ban,
    "update": update,
    "say": say,
}
startServer()
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
addToLog("Server started.")
app.mainloop()