import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore, storage
import _thread
import os
from tkinter import *
from tkinter import scrolledtext
import random
#from pynput.keyboard import Key, Listener
from pynput import keyboard
'''CONFIG'''
logging = 1 # 1 - Data logging enabled, 0 - Data logging disabled
loadprevious = 1 # 1 - loads previous messages from the log, 0 - doesn't
'''CONFIG END'''

'''
pip install requests
pip install pynput
pip install python-firebase
pip install 
'''

import sys
if sys.version_info.major == 3:
    unicode = str
# the rest of your code goes here

randomnr = random.randint(1,99)
name = "guest"+str(randomnr)
nameUnicode = unicode(name)

group = 'Group1'
groupUnicode = unicode(group)

print("hello " + nameUnicode)
print("Initializing..")

#//Firestore related
cred = credentials.Certificate("./databasecertificate.json")
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'airr-75928.appspot.com'
})

bucket = storage.bucket()
store = firestore.client()

datadict = {} #the dictionary of info to be sent to the database
incomingdict = {}

newmsg = ""

def refresh():
    newdict = {}
    
    # Create a callback on_snapshot function to capture changes
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            #if change.type.name == 'ADDED':
             #   print(u'New city: {}'.format(change.document.id))
            if change.type.name == 'MODIFIED':
                #print(u'Modified city: {}'.format(change.document.id))
                newdict = change.document.to_dict()
                #print("\n")
                print(change.document.id + ": " + newdict[u'message'] + "\n")
                global newmsg
                newmsg = change.document.id+ ": "+ newdict[u'message']+"\n"
                global logging
                if(logging == 1):
                    text_file = open("chatlog.txt", "a+")
                    text_file.write(newmsg)
                    text_file.close()
                    
                updateChatbox()
                
            #elif change.type.name == 'REMOVED':
            #    print(u'Removed city: {}'.format(change.document.id))

    col_query = store.collection(groupUnicode)

    # Watch the collection query
    query_watch = col_query.on_snapshot(on_snapshot)

refresh()

message = name + " has connected"
messageUnicode = unicode(message)

datadict[u'message']=messageUnicode
			
store.collection(groupUnicode).document(nameUnicode).set(datadict)
def loadHistory():
    if(loadprevious == 1):
        if(os.path.isfile('chatlog.txt')):
            chatlogfile = open("chatlog.txt", "r")
            #print(oldmsgdata)
            oldmsgdata = chatlogfile.read()
            chatBox.configure(state='normal')
            chatBox.insert(INSERT,oldmsgdata)
            chatBox.see(END)

def getMotd():
    doc_ref = store.collection(groupUnicode).document(u'MOTD')

    try:
        docc = doc_ref.get()
        #print(u'Document data: {}'.format(doc.to_dict()))
        motddict = docc.to_dict()
        motd = motddict[u'message']

        chatBox.configure(state='normal')
        chatBox.insert(INSERT,"\n")
        chatBox.insert(INSERT,motd)
        chatBox.insert(INSERT,"\n")
        chatBox.see(END)
        
    except google.cloud.exceptions.NotFound:
        print("MOTD not found")

def guiSend():
    datadict = {}
    message = messageBox.get()
    messageUnicode = unicode(message)
    datadict[u'message']=messageUnicode
    store.collection(groupUnicode).document(nameUnicode).set(datadict)
    messageBox.delete(0, 'end')
    
    
def sendMsg():
    datadict = {}
    message = input()
    messageUnicode = unicode(message)
    datadict[u'message']=messageUnicode
    store.collection(groupUnicode).document(nameUnicode).set(datadict)

def sendClicked():
    guiSend()

def setName():
    global name
    global nameUnicode
    name = nameBox.get()
    nameUnicode = unicode(name)
    chatBox.configure(state='normal')
    chatBox.insert(INSERT,"You changed your name to: "+name +"\n")

def setRoom():
    global group
    global groupUnicode
    group = roomBox.get()
    groupUnicode = unicode(group)
    chatBox.configure(state='normal')
    chatBox.insert(INSERT,"you are connected to "+group +"\n")

def updateChatbox():
    global newmsg
    chatBox.configure(state='normal')
    chatBox.insert(INSERT,newmsg)
    chatBox.see(END)

window = Tk()
window.title("Rooms")
window.geometry('350x500')
#window.configure(background='black')

nameLbl = Label(window,text="Name: ")
nameBtn = Button(window, text="Set",command = setName)
nameBox = Entry(window, width=12)

roomLbl = Label(window,text ="Room: ")
roomBox = Entry(window, width=12)
roomBtn = Button(window, text="Set",command = setRoom)

chatBox = scrolledtext.ScrolledText(window,state='disabled', width=46,height=27)

messageLbl = Label(window, text="Message:")
sendBtn = Button(window, text="Send",command = sendClicked)
messageBox = Entry(window,width=24)

nameLbl.grid(column=0,row=0,sticky=W)
nameBtn.grid(column=2,row=0)
nameBox.grid(column=1,row=0,sticky = E)

roomLbl.grid(column=0,row=1,sticky=W)
roomBox.grid(column=1,row=1,sticky = E)
roomBtn.grid(column=2,row=1)

chatBox.grid(column=0,row=2,columnspan=3)

messageLbl.grid(column=0,row=3)
sendBtn.grid(column=2, row=3)
messageBox.grid(column=1,  row=3)

roomBtn.configure(state='disabled')
roomBox.configure(state='disabled')
roomLbl.configure(state='disabled')

loadHistory()

chatBox.configure(state='normal')
chatBox.insert(INSERT,"\n")
chatBox.insert(INSERT,"Welcome to rooms! "+name +"\n")
chatBox.insert(INSERT,"you are connected to "+group +"\n")
chatBox.configure(state='disabled')

getMotd()

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.enter:
        guiSend()

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

messageBox.focus_set()

window.mainloop()
