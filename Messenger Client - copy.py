# TCP Chat Client
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
# Created on 16-03-2016
import socket, threading, random
from tkinter import *
from urllib import request

# this program uses a graphical user interface

class App(Frame):
    version = 0.1 
    def __init__(self, master):
        super(App, self).__init__(master)

        self.repo_url = "https://raw.githubusercontent.com/Nytra/messenger/master/Messenger%20Client.py"
        self.check_update()
        self.server = input("Enter an IP address: ").strip()
        self.name = input("Enter your username: ").strip()
        if not name:
            self.name = "Anonymous" + str(random.randrange(1, 10000))
        self.port = 45009
        self.grid()
        self.data_buff = 4096
        if not self.connect():
            #print("Unable to connect to", self.server, "on port", str(self.port), "\nClosing program...")
            quit()
        self.create_widgets()

        t1 = threading.Thread(target = self.get_messages)
        t1.start()

    def check_update(self):
        print("Checking for updates...")
        response = request.urlopen(self.repo_url)
        data = response.read()
        data_str = data.decode("utf-8")
        with open("Messenger Client.py", "r") as f:
            file = f.read().strip()
        if data_str != file:
            print("An update is available. Would you like to download it? [Y/N]: ", end = "")
            print(data_str)
            choice = input().lower().strip()
            if choice == "y":
                print("\nDownloading...")
                self.download_update(data_str)
            else:
                print()
        else:
            print("The program is up to date.")
            
    def download_update(self, update):
        with open("Messenger Client.py", "w") as f:
            f.write(update)
        print("The update has been installed. Please restart the program.")
        while True:
            quit()
        
    def __str__(self):
        rep = "Chat Instance\nServer: " + self.server \
              + "\nPort: " + str(self.port) + "\nVersion: " \
              + str(self.version)
        return rep

    def create_widgets(self):
        self.message_lbl = Label(self, text = "Message: ")
        self.message_lbl.grid(row = 0, column = 0, sticky = W)
        self.message_output = Text(self, width = 40, height = 80, wrap = WORD)
        self.message_output.grid(row = 1, column = 0, sticky = W)
        self.message_input = Entry(self)
        self.message_input.grid(row = 0, column = 1, sticky = W)
        self.submit_bttn = Button(self, text = "Send", command = self.submit_message)
        self.submit_bttn.grid(row = 0, column = 2, sticky = W)

    def submit_message(self):
        message = self.message_input.get().strip()
        if not message:
            self.message_input.delete(0, END)
            return
        message = self.name + "> " + message
        data = message.encode()
        s.send(data)
        self.message_input.delete(0, END)

    def insert_message(self, message):
        log = self.message_output.get("1.0", END)
        log = log + message
        self.message_output.delete("1.0", END)
        self.message_output.insert("1.0", log)
        
    def get_messages(self):
        while True:
            data = s.recv(self.data_buff)
            if not data:
                break
            decoded = data.decode("utf-8")
            self.insert_message(decoded)
        s.close()
        self.insert_message("Connection Lost.")

    def connect(self):
        print("Attempting to connect to", self.server, "on port", self.port)
        try:
            s.connect((self.server, self.port))
            print("Connection established.")
            return True
        except Exception as e:
            print(e)
            input("\nPress enter to continue . . .")
            return False


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
root = Tk()
app = App(root)
root.title("Messenger V{}".format(str(App.version)))
root.geometry("512x720")
root.mainloop()