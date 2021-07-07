import argparse
import base64
import logging
import os,platform
import select
import socket
import subprocess
import time
import ctypes
from tqdm import tqdm

logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s', level=logging.INFO)

parser=argparse.ArgumentParser(description='socket tool for very easy transfering data',epilog='Attention : if it is going to be a client you most to enter server ip and port too')
parser.add_argument("operation",metavar='operation',help="Choice to be client or server put 'c' for client and 's' for server" )
parser.add_argument('-ip',"--serverip",metavar='serverip',help="Enter ip of server")
parser.add_argument('-p',"--port",metavar='port',help="Enter port number of server")
args=parser.parse_args()
client=False
if args.operation=="c":
    try:
        client=True
        PORT=int(args.port)
        serverip=args.serverip
    except Exception:
        raise Exception("Enter ip and port number with -ip and -p")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def wlan_ip():
    global admin
    admin=True
    if platform.system()=='Windows':
        logging.info("Windows os detected")
        if is_admin():
            logging.info("admin checked")
        else:
            logging.warning("admin permission might be required !")
            admin=False
        result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True).stdout.lower()
        scan=0
        for i in result.split('\n'):
            if 'wireless' in i: scan=1
            if scan:
                if 'ipv4' in i: return i.split(':')[1].strip() 
                if 'IPv4' in i: return i.split(':')[1].strip() 

    elif subprocess.check_output(['uname','-o']).strip()==b'Android':
        logging.info("Android os detected")
        return "192.168.43.1"            
    elif platform.system()=='Linux':
        logging.info("Linux os detected")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP            

HOST=wlan_ip()   

def makeserver():
    connected_clients_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, 0))
        server_socket.listen(10)
        PORT=server_socket.getsockname()[1]
        connected_clients_sockets.append(server_socket)
        buffer_size = 10000000
        logging.info('listening on : '+str(HOST)+':'+str(PORT))
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
                            logging.info('I/O NAME {} & SIZE {} bytes'.format(name,size))
                            sock.send(b"GOT SIZE")
                        elif txt.startswith('BYE'):
                            logging.info('RECEIVED SUCCESSFULLY')
                            logging.info('recived : '+str(receiveddata)+' real size : '+str(size))
                            #return 
                            sock.send(b"done")
                            buffer_size = 10000000
                            a=1
                            numbers=numbers-1
                            if numbers==0:
                                sock.shutdown(1)
                                return
                            else:
                                logging.info("Downloading next one")    
                        elif txt.startswith('NUMBER'):  
                            tmp = txt.split() 
                            numbers = int(tmp[1]) 
                            logging.info("{} file's are going to download ".format(numbers))
                        elif data:            
                            logging.info('downloading...')  
                            try:    
                                myfile = open('DATA/{}'.format(name), 'wb')
                            except:
                                os.mkdir("DATA") 
                                myfile = open('DATA/{}'.format(name), 'wb')   
                            if not data:
                                myfile.close()
                                break
                            as_text=data
                            original = base64.b64decode(as_text)
                            receiveddata=len(as_text)
                            pbar = tqdm(total=100)
                            barcounter=100/(size/receiveddata)
                            pbar.update(barcounter)
                            while receiveddata<size:
                                data = sock.recv(buffer_size)
                                barcounter=100/(size/len(data))
                                pbar.update(barcounter)
                                original += base64.b64decode(data)
                                receiveddata+=len(data)
                            pbar.close()
                            logging.info('saveing...')
                            myfile.write(original)
                            myfile.close()
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
                    logging.info("buffersize set to : "+str(buffer_size))
                else :
                    logging.error(E,exc_info=True)
                sock.close()
                connected_clients_sockets.remove(sock)
                continue
        server_socket.close()
    except Exception as E:
        if not admin:
            raise Exception("Admin permission required !")
        else:    
            logging.error(E,"ip :",HOST)
            logging.error("you are offline")  
        return
def inputdata():
    l=[]
    for root, dirs, files in os.walk(r"./SEND", topdown=False):
        for name in files:
            if name==".gitignore":
                pass
            else:
                l.append(os.path.join(root, name))
        for name in dirs:
            if name==".gitignore":
                pass
            else:
                l.append(os.path.join(root, name))
    if len(l)==0:
        raise("there is nothing available for sending put file's in SEND directory")
    return(l) 
def send():
    global message
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        # open inputdata
        datas=inputdata()
        sock.send(bytes("NUMBER {}".format(len(datas)),'utf-8'))
        for i in datas:
            myfile = open(i, 'rb')
            name=os.path.basename(myfile.name).replace(" ","_")
            buffer = myfile.read()
            as_text_base64 = base64.b64encode(buffer)
            size = len(as_text_base64)
            logging.info('len bytes '+str(len(buffer))+' len bytes '+str(size))
            # send inputdata size to server
            sock.send(bytes("SIZE {} {}".format(name,size),'utf-8'))
            answer = sock.recv(4096)
            answer=answer.decode('utf-8')
            logging.debug('server answer = %s' % answer)
            if answer == 'GOT SIZE':
                base64.b64decode(as_text_base64)
                sock.sendall(as_text_base64)
                logging.info('sending...')
                # check what server send
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                logging.debug('server answer = %s' % answer)
                if answer == 'GOT IT' :
                    sock.sendall(b"BYE BYE ")
                    logging.info('DATA SUCCESSFULLY SENTED TO SERVER')
                    answer = sock.recv(4096).decode('utf-8')
                    if answer=="done":
                        logging.info('Sending next file if exist')
                elif answer=='RETRY':
                    logging.info('RETRYING...')
                    sock.close()
                    return False
            myfile.close()
        logging.info('TRANSPORTATION FINISHED')    
        return True
    except Exception as E:
        logging.error(E,exc_info=True)    
        logging.debug('still searching for ',HOST)
        sock.close()
        return False
def connect():
    while 1:
        if send():
            return
        time.sleep(2)

if client:    
    if os.path.isdir(r'./SEND'):
        pass
    else:
        os.mkdir("SEND") 
    connect()
else:
    makeserver()    
