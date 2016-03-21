# TCP Chat Server
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016

import socket, threading, time, datetime

def listen(s):
    global admin, num_conn, nc_const, total_connections
    server_log("[" + time(full=True) + "] " + "Listening for connections to " + server + ":" + str(port) + " . . .")
    s.listen(1)
    c, addr = s.accept()
    connections.append(c)
    addresses[c] = addr
    num_conn += 1
    total_connections += 1
    server_log("[" + time(full=True) + "] " + "Connection established with " + str(addr) + " [{}/{}]".format(num_conn, nc_const))
    tc = threading.Thread(target = threaded_client, args = (c, addr))
    tc.start()

def process_command(message, c, addr):
    global admin, num_conn, nc_const, parties, total_connections
    message = message[1:]
    params = message.split(" ")
    command = params[0]
    params = params[1:]
    server_response = ""
    response = ""
    if command == "nick":
        if params:
            nick = " ".join(x for x in params).strip()
            if nick not in illegal_nicks:
                try:
                    prev_nick = nicks[addr]
                except:
                    prev_nick = ""
                if " " not in nick:
                    if admin == [c, addr]:
                        nicks[addr] = "[ADMIN] " + nick
                    else:
                        nicks[addr] = nick
                    server_command(c, "$%server%^mod%^widget%^nick%^label%^text%^{}".format(nick))
                    if prev_nick:
                        response = "{} changed nickname to {}".format(prev_nick, nick)
                        server_log("[" + time(full=True) + "] " + "{} changed nickname to {}".format(prev_nick, nick))
                    else:
                        response = "{} joined the server.".format(nick)
                        server_log("[" + time(full=True) + "] " + "{} joined the server.".format(nick))
                else:
                    server_response = "Names cannot contain spaces."
            else:
                server_log("[" + time(full=True) + "] " + str(addr) + " nick change blocked. (Value: \"{}\")".format(nick))
                server_response = "Nickname change denied."
        else:
            server_response = "Invalid parameters. /nick (name)"
    elif command == "kick":
        if params:
            if admin == [c, addr]:
                target = params[0]
                for connection in connections:
                    a = addresses[connection]
                    if nicks[a].lower() == target.lower():
                        kick(connection)
                        break
            else:
                server_response = "Access denied."
        else:
            server_response = "Invalid parameters. /kick (name)"
    elif command == "kickall" and admin == [c, addr]:
        for connection in connections:
            if connection not in admin:
                kick(connection)
        server_response = "All clients have been removed from the session."
    elif command == "$dev_admin_on":
        admin = [c, addr]
        server_response = "You are now an administrator."
    elif command == "$dev_admin_off":
        admin = []
        server_response = "You are no longer an administrator."
    elif command == "list":
        for index, nick in enumerate(list(nicks.values())):
            num = index+1
            if num < len(list(nicks.values())):
                server_response += nick + ", "
            else:
                server_response += nick
    elif command == "msg":
        if params:
            message = "[PRIVATE] {}: ".format(nicks[addr]) + " ".join(x for x in params[1:])
            recipient = params[0]
            server_response = "Message failed to send. {} could not be found.".format(recipient)
            for conn in connections:
                if nicks[addresses[conn]] == recipient:
                    recipient = conn
                    direct_msg(message, recipient)
                    server_response = "Message sent."
        else:
            server_response = "You must specify a recipient and a message in the format /msg {recipient} {msg}"
    elif command == "stat":
        server_response = "Connected clients: [{}/{}] - Server running since: [{}] - Number of epileptic seizures: {} - Total number of connections: {}".format(num_conn, nc_const, start_time_full, parties, total_connections)
    elif command == "party":
        server_command(c, "$%server%^do%^party")
        parties += 1
    elif command == "clear":
        server_command(c, "$%server%^do%^clear")
    elif command == "disconnect":
        server_command(c, "$%server%^do%^disconnect")
    else:
        server_response = "\"/{}\" is not a valid command.".format(command)
        
    if response:
        broadcast(response, sender=c, server_msg = True)
    if server_response:
        direct_msg(server_response, c)

def direct_msg(message, target):
    try:
        server_log("[{}] {} \"{}\" Server Direct Message: ".format(time(full=True), addresses[target], nicks[addresses[target]]) + message)
    except:
        server_log("[{}] {} Server Direct Message: ".format(time(full=True), addresses[target]) + message)
    message = "[{}] ".format(time()) + message
    try:
        target.send(message.encode())
    except socket.error:
        kick(target)

def server_command(c, message):
    try:
        c.send(message.encode())
    except socket.error as e:
        kick(c)

def kick(c):
    global num_conn, nc_const
    c.close()
    connections.remove(c)
    num_conn -= 1
    try:
        server_log("[" + time(full=True) + "] " + "{} \"{}\" disconnected.".format(addresses[c], nicks[addresses[c]]) + " [{}/{}]".format(num_conn, nc_const))
        broadcast("{} disconnected.".format(nicks[addresses[c]]), server_msg = True)
    except KeyError:
        server_log("[" + time(full=True) + "] " + "{} disconnected.".format(addresses[c]) + " [{}/{}]".format(num_conn, nc_const))
        #broadcast("{} disconnected.".format(addresses[c]), server_msg = True)
    try:
        del(nicks[addresses[c]])
    except KeyError:
        pass
        server_log("[" + time(full=True) + "] " + "{} has no nickname.".format(addresses[c]))

def server_log(message):
    print(str(message))
    with open("serverlog.txt", "a") as f:
        f.write(str(message) + "\n")

def threaded_client(c, addr):
    while True:
        try:
            data = c.recv(data_buff)
        except socket.error as e:
            break
        if not data:
            break
        message = data.decode("utf-8")
        if message[0] == "/":
            try:
                server_log("[" + time(full=True) + "] " + "{} \"{}\": \"{}\"".format(addr, nicks[addr], message))
            except:
                server_log("[" + time(full=True) + "] " + "{}: \"{}\"".format(addr, message))
            process_command(message, c, addr)
        else:
            server_log("[" + time(full=True) + "] " + str(addr) + " \"{}\":".format(nicks[addr]) + " \"{}\"".format(message))
            broadcast(message, sender=c)
    kick(c)

def broadcast(message, sender = None, server_msg=False):
    original = message
    with open("chatlog.txt", "a") as f:
        if not server_msg:
            message = "[" + time(full=True) + "] " + nicks[addresses[sender]] + ": " + original
        else:
            message = "[" + time(full=True) + "] " + original
        f.write(message + "\n")
    for connection in connections:
        if not server_msg and sender != None:
            message = "[" + time() + "] " + nicks[addresses[sender]] + ": " + original
        else:
            message = "[" + time() + "] " + original
        try:
            connection.send(message.encode())
        except socket.error as e:
            kick(connection)

def time(full = False, date_only = False):
    if not full and not date_only:
        time = datetime.datetime.now().strftime('%H:%M:%S')
    elif not date_only and full == True:
        time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    elif not full and date_only == True:
        time = datetime.datetime.now().strftime('%d-%m-%Y')
    return time

connections = []
addresses = {}
nicks = {}
illegal_nicks = ["", " ", ":"]
admin = []
if __name__ == "__main__":
    server = socket.gethostbyname(socket.gethostname()) # "10.13.9.89" # MCS IP Address
    port = 45011
    parties = 0
    total_connections = 0
    data_buff = 4096 # data buffer
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((server, port))
    except socket.error: # if port 45011 is not available
        s.bind((server, 0)) # chooses a random available port
        port = s.getsockname()[1]
    start_time_date = time(date_only = True)
    start_time_time = time()
    start_time_full = time(full=True)
    server_log("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n[{}] Starting Server...".format(time(full=True)))
    server_log("[{}] IP Address: ".format(time(full=True)) + server)
    server_log("[{}] Port: ".format(time(full=True)) + str(port))
    
    num_conn = 0
    nc_const = 256 # maximum number of connected users
    printed = False
    while True:
        if num_conn >= nc_const:
            if not printed:
                server_log("[" + time(full=True) + "] " + "The server has stopped accepting connections. [{}/{}]".format(num_conn, nc_const))
                printed = True
        else:
            if printed:
                server_log("[" + time(full=True) + "] " + "The server is now accepting connections. [{}/{}]".format(num_conn, nc_const))
            printed = False
            listen(s)