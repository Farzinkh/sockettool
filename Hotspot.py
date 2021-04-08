import socket,select
import base64
import subprocess
from tqdm import tqdm
from threading import *
import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import  ThemedTk
import os,time
import warnings
import playsound
warnings.filterwarnings("ignore")

def raise_frame(frame,kind="",label=""):
    if kind=="S" or kind=="R":
        Refresher(frame,label)                   
    frame.tkraise()

def Refresher(frame,label):
    label.configure(text=message)
    frame.after(1000, lambda:Refresher(frame,label))     

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def main():
    global message
    message=""
    if "alarm.mp3" not in os.listdir("."):
        print("alarm.mp3 not found please check it out")
        time.sleep(5)
        raise Exception("alarm.mp3 not found please check it out")
    LARGE_FONT= ("Verdana", 12)
    root=ThemedTk(theme="adapta")
    root.title('HOTSPOT')
    root.bind('<Escape>', lambda e: root.destroy())
    root.protocol("WM_DELETE_WINDOW", root.iconify)
    root.update_idletasks()
    root.iconbitmap('icon.ico')
    home=ttk.Frame(root)
    home.grid(row=0, column=0, sticky='news')
    home.rowconfigure([0], weight=1)
    home.columnconfigure([0,1], weight=1)
    server=ttk.Frame(root)
    server.grid(row=0, column=0, sticky='news')
    server.rowconfigure([0,1,2,3], weight=1)
    server.columnconfigure([0], weight=1)
    status5 = ttk.Label(server,text="", font=LARGE_FONT,anchor=tk.CENTER)
    status5.grid(row=2,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    status7 = ttk.Label(server,text="", font=LARGE_FONT,anchor=tk.CENTER)
    status7.grid(row=1,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    progress2 = ttk.Progressbar(server, orient="horizontal",
                                         mode="determinate",
                                         cursor='spider')
    progress2.grid(row=3,column=0,sticky=tk.N+tk.S+tk.E+tk.W) 
    progress2["maximum"] = 100  
    button3 = ttk.Button(server,text="Start",width=15,
                        command=lambda:Thread(target=lambda:makeserver(status7,progress2,server)).start())
    button3.grid(row=1, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
    button3 = ttk.Button(home,text="Recieve",width=15,
                        command=lambda:raise_frame(server,"R",status5))
    button3.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    button4 = ttk.Button(home,text="Send",width=15,
                        command=lambda:raise_frame(page,"S",status6))
    button4.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)

    page = ttk.Frame(root)
    page.grid(row=0, column=0, sticky='news')
    page.rowconfigure([0,1,2], weight=1)
    page.columnconfigure([0], weight=1)
    progress = ttk.Progressbar(page, orient="horizontal",
                                         mode="determinate",
                                         cursor='spider')
    progress.grid(row=1,column=0,sticky=tk.N+tk.S+tk.E+tk.W) 
    progress["maximum"] = 100  
    status6 = ttk.Label(page,text="", font=LARGE_FONT,anchor=tk.CENTER)
    status6.grid(row=2,column=0,sticky=tk.N+tk.S+tk.E+tk.W)                       
    startpage = ttk.Frame(page)
    startpage.grid(row=0, column=0, sticky='news')
    startpage.rowconfigure([0,1,2], weight=1)
    startpage.columnconfigure([0,1,2], weight=1)
    HOST = ttk.Entry(startpage)
    HOST.grid(row=1,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
    PORT = ttk.Entry(startpage)
    PORT.grid(row=2,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
    PORT.insert(tk.END, '65432')
    button = ttk.Button(startpage,text="send",width=15,
                        command=lambda: Thread(target=lambda:connect(page,progress,HOST.get(),int(PORT.get()))).start())
    button.grid(row=2, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
    status = ttk.Label(startpage,text="click for connecting and sending", font=LARGE_FONT,anchor=tk.CENTER)
    status.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    status1 = ttk.Label(startpage,text="", font=LARGE_FONT,anchor=tk.CENTER)
    status1.grid(row=0,column=2,sticky=tk.N+tk.S+tk.E+tk.W)
    status2 = ttk.Label(startpage,text="", font=LARGE_FONT,anchor=tk.CENTER)
    status2.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W)
    status3 = ttk.Label(startpage,text="IP ", font=LARGE_FONT,anchor=tk.CENTER)
    status3.grid(row=1,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    status4 = ttk.Label(startpage,text="PORT", font=LARGE_FONT,anchor=tk.CENTER)
    status4.grid(row=2,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    button2 = ttk.Button(startpage,text="open file",width=15,
                        command=lambda: Open(progress))
    button2.grid(row=1, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
    center(root)
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=False)
    filemenu.add_command(label="Home", command=lambda:raise_frame(home))
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="MENU", menu=filemenu)
    root.config(menu=menubar)
    root.deiconify()
    root.resizable(width=False, height=False)  
    raise_frame(home)
    root.mainloop()  
def Open(progress):
    global inputdata
    inputdata =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("all files","*.*"),("jpeg files","*.jpg")))
    inputdata= r"{}".format(inputdata)
    progress.start(5) 
def send(root,progress,HOST,PORT):
    global inputdata,message
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if HOST==wlan_ip():
            message='you cannot send file to yourself :|'
            raise Exception('you cannot send file to yourself :|')
        server_address = (HOST, PORT)
        sock.connect(server_address)
        # open inputdata
        progress["value"] = 1
        myfile = open(inputdata, 'rb')
        name=os.path.basename(myfile.name)
        buffer = myfile.read()
        as_text_base64 = base64.b64encode(buffer)
        size = len(as_text_base64)
        print('len {}:'.format(type(buffer)),len(buffer),'\nlen {}'.format(type(as_text_base64)),size)
        # send inputdata size to server
        sock.send(bytes("SIZE {} {}".format(name,size),'utf-8'))
        answer = sock.recv(4096)
        answer=answer.decode('utf-8')
        print ('server answer = %s' % answer)
        message='server answer = %s' % answer
        progress["value"] = 10
        # send inputdata to server
        if answer == 'GOT SIZE':
            base64.b64decode(as_text_base64)
            sock.sendall(as_text_base64)
            progress["value"] = 90
            print('sending...')
            message='sending...'
            # check what server send
            answer = sock.recv(4096)
            answer=answer.decode('utf-8')
            print ('server answer = %s' % answer)
            message='server answer = %s' % answer
            if answer == 'GOT IT' :
                sock.sendall(b"BYE BYE ")
                print ('DATA SUCCESSFULLY SENTED TO SERVER')
                message='DATA SUCCESSFULLY SENTED TO SERVER'
                progress["value"] = 100
                file = "alarm.mp3"
                playsound.playsound(file,block=False)
            elif answer=='RETRY':
                print ('RETRYING...')
                message="RETRYING..."
                sock.close()
                return False
        myfile.close()
        return True
    except Exception as E:
        print(E)    
        if E.args[0]=='you cannot send file to yourself :|':
            time.sleep(2)
            message="Enter another ip address"
            return True
        print('still searching for ',HOST)
        message='still searching for '+HOST
        sock.close()
        return False
def connect(root,progress,HOST,PORT):
    while 1:
        if send(root,progress,HOST,PORT):
            return
        time.sleep(2)
def makeserver(label,bar,frame):
    global message
    HOST=wlan_ip()   
    PORT = 65432

    connected_clients_sockets = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
        connected_clients_sockets.append(server_socket)
        buffer_size = 10000000
        print('listening on :',HOST,':',PORT)
        label.configure(text='listening on : '+HOST+':'+str(PORT))
        frame.update()
        a=1
        while True:
            try:
                read_sockets, write_sockets, error_sockets = select.select(connected_clients_sockets, [], [])
                for sock in read_sockets:
                    if sock == server_socket:
                        sockfd, client_address = server_socket.accept()
                        connected_clients_sockets.append(sockfd)
                    else:
                        data = sock.recv(buffer_size)
                        txt = data.decode('utf-8')
                        if txt.startswith('SIZE'):
                            tmp = txt.split()
                            name = tmp[1]
                            size = int(tmp[2])
                            print ('I/O NAME {} & SIZE {} bytes'.format(name,size))
                            message='I/O NAME {} & SIZE {} bytes'.format(name,size)
                            sock.send(b"GOT SIZE")
                            # Now set the buffer size for the image 
                        elif txt.startswith('BYE'):
                            sock.shutdown(1)
                            print('\nRECEIVED SUCCESSFULLY','recived :',receiveddata,'real size :',size)
                            message='RECEIVED SUCCESSFULLY RECEIVED'
                            file = "alarm.mp3"
                            playsound.playsound(file,block=False)
                            return

                        elif data:            
                            print('downloading...')  
                            message='downloading...' 
                            try:    
                                myfile = open('DATA/{}'.format(name), 'wb')
                            except:
                                os.mkdir("DATA") 
                                myfile = open('DATA/{}'.format(name), 'wb')   
                            if not data:
                                myfile.close()
                                break
                            jpg_as_text=data
                            jpg_original = base64.b64decode(jpg_as_text)
                            receiveddata=len(jpg_as_text)
                            pbar = tqdm(total=100)
                            barcounter=100/(size/receiveddata)
                            pbar.update(barcounter)
                            bar["value"] = barcounter
                            frame.update()
                            while receiveddata<size:
                                data = sock.recv(buffer_size)
                                barcounter=100/(size/len(data))
                                pbar.update(barcounter)
                                bar["value"] = bar["value"]+ barcounter
                                frame.update()
                                jpg_original += base64.b64decode(data)
                                receiveddata+=len(data)
                                #print('receiveddata:',receiveddata)
                            pbar.close()
                            print('saveing...')
                            message="saveing..."
                            myfile.write(jpg_original)
                            myfile.close()
                            #buffer_size = 4096
                            sock.send(b"GOT IT")
            except Exception as E:
                if E.args[0]=="Incorrect padding":
                    sock.send(b"RETRY")
                    try:
                        pbar.close()
                    except:
                        pass    
                    a=a*10
                    buffer_size = int(10000000/a)
                    print("buffersize set to :",buffer_size)
                else :
                    print(E)
                sock.close()
                connected_clients_sockets.remove(sock)
                continue
        server_socket.close()
    except Exception as E:
        print(E,"ip :",HOST)
        message="you are offline"  
        return

def wlan_ip():
    result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True).stdout.lower()
    scan=0
    for i in result.split('\n'):
        if 'wireless' in i: scan=1
        if scan:
            if 'ipv4' in i: return i.split(':')[1].strip() 
            if 'IPv4' in i: return i.split(':')[1].strip()        
if __name__ == '__main__':
    main()
