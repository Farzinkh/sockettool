import argparse
import base64
import logging
import os,platform
import select
import socket
import subprocess
import time
import ctypes
import psutil
from math import ceil
from tqdm import tqdm
from pathlib import Path

parser=argparse.ArgumentParser(description='socket tool for very easy transfering data',epilog='Attention : if it is going to be a client you most to enter server ip and port too')
parser.add_argument("operation",metavar='operation',help="Choice to be client or server put 'c' for client and 's' for server" )
parser.add_argument('-ip',"--serverip",metavar='serverip',help="Enter ip of server")
parser.add_argument('-p',"--port",metavar='port',help="Enter port number of server")
args=parser.parse_args()
client=False
if args.operation=="c" or args.operation=="cd":
    try:
        client=True
        PORT=int(args.port)
        serverip=args.serverip
        if args.operation=="cd":
            logging.basicConfig(level=logging.DEBUG) #for debugging
        else:
            import warnings
            warnings.filterwarnings('ignore')
            logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s', level=logging.INFO)
    except Exception:
        raise Exception("Enter ip and port number with -ip and -p")
elif  args.operation=="s" or args.operation=="sd":
    if args.operation=="sd":
        logging.basicConfig(level=logging.DEBUG) #for debugging
    else:
        import warnings
        warnings.filterwarnings('ignore')
        logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s', level=logging.INFO)  
else:
    raise("OPERATION NOT DITECTED CHOSE ONE OF THIS (c,s,cd,sd)")

def gen():
    for i in range(100):
        yield

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
logging.info("system info number of cpu's {}, frequence {}".format(psutil.cpu_count(),psutil.cpu_freq()))
def check_mem(THRESHOLD):
    mem = psutil.virtual_memory() 
    av=mem.available
    if  av<= THRESHOLD:
        logging.debug("Not enough memory available")
        return False
    else:
        logging.debug("Memory checked {} GB available".format(av/2**30))   
        return True 

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
        Hugeflag,Hugeflagfinish=False,False
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
                        if Hugeflag:
                            txt=''
                        else:
                            data = sock.recv(buffer_size)
                            txt = data.decode('utf-8')
                            logging.debug("server received {}".format(txt))
                        if txt.startswith('SIZE'):
                            tmp = txt.split()
                            name = tmp[1]
                            gender = tmp[2]
                            if gender=="Normal":
                                size = int(tmp[3])
                                logging.info('I/O NAME {} & SIZE {} MB'.format(name,size/2**20))
                                logging.debug("server sent GOT SIZE")
                                sock.send(b"GOT SIZE")
                                Hugeflag=False
                            else:
                                parts = int(tmp[3])
                                size = int(tmp[4])
                                logging.info('I/O NAME {} Huge type & {} parts and size {}'.format(name,parts,size))  
                                logging.debug("server sent GOT SIZE")
                                sock.send(b"GOT SIZE")
                                Hugeflag=True  
                        elif txt.startswith('BYE'):
                            logging.info('RECEIVED SUCCESSFULLY')
                            logging.info('recived : '+str(receiveddata)+' real size : '+str(size))
                            #return 
                            if Hugeflagfinish:
                                pass
                            else:
                                logging.debug("server sent done")
                                sock.send(b"done")
                                Hugeflagfinish=False
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
                            logging.info("{} files are going to download ".format(numbers))
                            sock.send(b"ok")
                            logging.debug("server sent ok")
                        elif data or Hugeflag:            
                            logging.info('downloading...')  
                            try:    
                                myfile = open('DATA/{}'.format(name), 'wb')
                            except:
                                os.mkdir("DATA") 
                                myfile = open('DATA/{}'.format(name), 'wb')   
                            if not data:
                                myfile.close()
                                break
                            pbar = tqdm(total=100)
                            if Hugeflag:
                                eachbarcounter=100/(parts)
                            else:  
                                as_text=data
                                original = base64.b64decode(as_text)
                                receiveddata=len(as_text)    
                                barcounter=100/(size/receiveddata)
                            if Hugeflag:
                                sum=0
                                for i in range(parts):
                                    txt=sock.recv(2048).decode('utf-8')
                                    logging.debug("server received {}".format(txt))
                                    tmp = txt.split()
                                    partnumber=int(tmp[1])
                                    size=int(tmp[3])
                                    receiveddata=0
                                    logging.debug("for i {} and partnumber {} size {}".format(i,partnumber,size))
                                    logging.debug("server is going to download a chunk")
                                    sock.send(b"ready")
                                    while receiveddata<size:
                                        data = sock.recv(buffer_size)
                                        barcounter=eachbarcounter/(size/len(data))
                                        sum+=barcounter
                                        pbar.update(barcounter)
                                        try:
                                            original += base64.b64decode(data)
                                        except:
                                            original = base64.b64decode(data)   
                                        receiveddata+=len(data)
                                        if not receiveddata<size:
                                            break
                                    logging.debug("chunk downloaded") 
                                    sock.send(b'GOT IT')  
                                    txt=sock.recv(2048).decode('utf-8')
                                    if txt=="Next":
                                        pass     
                                pbar.update(100-sum)    
                                pbar.close()
                                logging.info('saveing...')
                                myfile.write(original)
                                myfile.close()    
                                sock.send(b'done')
                                Hugeflag,Hugeflagfinish=False,True
                            else:  
                                pbar.update(barcounter)
                                logging.debug("server is going to download")
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
                                logging.debug("server sent GOT IT")
                                sock.send(b"GOT IT")
            except Exception as E:
                if E.args[0]=="Incorrect padding" : 
                    logging.debug("server sent RETRY Error code {}".format(E.args[0]))
                    sock.send(b"RETRY")
                    try:
                        pbar.close()
                    except:
                        pass    
                    a=a*10
                    buffer_size = int(10000000/a)
                    logging.info("buffersize set to : "+str(buffer_size))
                elif E.args[0].startswith("Invalid base64-encoded string:"):
                    logging.info("Invalid file retrying...")
                    logging.debug("server sent RETRY")  
                    sock.send(b"RETRY")
                    try:
                        pbar.close()
                    except:
                        pass   
                else :
                    logging.error(E,exc_info=True)
                    logging.error(E.args[0])
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

def read1k():
    return myfile.read(10000000)

def retrying(as_text_base64):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORT)
    sock.connect(server_address)
    sock.sendall(as_text_base64)
    answer = sock.recv(4096)
    answer=answer.decode('utf-8')
    return answer

def send():
    global message,datas,myfile
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        # open inputdata
        sock.send(bytes("NUMBER {}".format(len(datas)),'utf-8'))
        logging.debug("client sent NUMBER {}".format(len(datas)))
        count=len(datas)
        answer = sock.recv(4096)
        answer=answer.decode('utf-8')
        if answer=="ok":
            pass 
        else:
            logging.debug("client is waited for ok message from server")
            while True:
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                if answer=="ok":
                    break 
        for i in range(count):
            myfile = open(datas[0], 'rb')
            name=os.path.basename(myfile.name).replace(" ","_")
            logging.info('Reading {}'.format(name))
            fsize=Path(datas[0]).stat().st_size
            if  fsize>200*2**20 or not check_mem(fsize): #it is huge
                logging.info('Huge file detected {} about {} GB'.format(name,fsize/2**30))
                parts=ceil(fsize/10000000)
                sock.send(bytes("SIZE {} Huge {} {}".format(name,parts,fsize/2**20),'utf-8'))
                logging.debug("client sent SIZE {} Huge {} {}".format(name,parts,fsize/2**20))
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                logging.debug("client received {}".format(answer))
                if answer=="GOT SIZE":
                    pass
                else:
                    logging.debug("client is waiting for GOT SIZE")
                    while True:
                        answer = sock.recv(4096)
                        answer=answer.decode('utf-8')
                        if answer=="GOT SIZE":
                            break
                pbar = tqdm(total=100)
                barcounter=100/parts
                s,count=0,0
                for piece in iter(read1k, ''):
                    count=count+1
                    s=s+len(piece)
                    if count==parts:
                        barcounter=100-(100*barcounter)
                    as_text_base64 = base64.b64encode(piece)
                    logging.debug("client sent PART {} size {}".format(count,len(as_text_base64)))
                    sock.send(bytes("PART {} size {}".format(count,len(as_text_base64)),'utf-8'))
                    answer = sock.recv(4096)
                    answer=answer.decode('utf-8')
                    logging.debug("client received {}".format(answer))
                    if answer=="ready":
                        logging.debug("client is going to send a chunk")
                        sock.sendall(as_text_base64)
                        answer = sock.recv(4096)
                        answer=answer.decode('utf-8')
                        logging.debug('server answer = %s' % answer)
                        if answer == 'GOT IT' :
                            logging.debug("clinet sent Next chunk")
                            sock.send(b"Next")
                        elif answer=='RETRY':
                            sock.close()
                            while True:
                                logging.info('RETRYING...')
                                if retrying(as_text_base64)=='GOT IT':
                                    pass
                    pbar.update(barcounter)    
                    if s==fsize:
                        break     #all parts sent
                pbar.close()   
                datas.remove(datas[0]) 
                logging.info('HUGE DATA SUCCESSFULLY SENT TO SERVER')   
                answer = sock.recv(4096).decode('utf-8')
                logging.debug("client recived {}".format(answer))
                if answer=="done" and len(datas)>0:
                    logging.info('Sending next file')
                sock.sendall(b"BYE BYE ")
            else:
                buffer = myfile.read()
                as_text_base64 = base64.b64encode(buffer)
                size = len(as_text_base64)
                logging.info('BUFFER size '+str(fsize/2**20)+' MB file size '+str(size/2**20)+' MB')
                # send inputdata size to server
                sock.send(bytes("SIZE {} Normal {}".format(name,size),'utf-8'))
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                logging.debug('server answer = %s' % answer)
                if answer == 'GOT SIZE':
                    base64.b64decode(as_text_base64) # for testing
                    sock.sendall(as_text_base64)
                    logging.info('sending...')
                    # check what server send
                    answer = sock.recv(4096)
                    answer=answer.decode('utf-8')
                    logging.debug('server answer = %s' % answer)
                    if answer == 'GOT IT' :
                        sock.sendall(b"BYE BYE ")
                        logging.info('DATA SUCCESSFULLY SENT TO SERVER')
                        datas.remove(datas[0])
                        answer = sock.recv(4096).decode('utf-8')
                        if answer=="done" and len(datas)>0:
                            logging.info('Sending next file')
                    elif answer=='RETRY':
                        logging.info('RETRYING...')
                        sock.close()
                        return False
                myfile.close()
        logging.info('TRANSPORTATION FINISHED')    
        return True
    except Exception as E:
        if E.args[0]==10054:
            logging.error("An error acured in server retrying...")
        #elif E.args[0]==32: #broken pipe 
        else:    
            logging.error(E.args[0],exc_info=True)    
            logging.debug('still searching for {}'.format(serverip))
        sock.close()
        return False
def connect():
    global datas
    datas=inputdata()
    while 1:
        if send():
            return
        time.sleep(2)

if client:    
    if os.path.isdir(r'./SEND'):
        pass
    else:
        os.mkdir("SEND") 
    logging.info("Start connecting to server")    
    connect()
else:
    logging.info("Starting server")
    makeserver()    
