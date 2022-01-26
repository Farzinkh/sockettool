import argparse
import base64
import ctypes
import getpass
import logging
import os
import platform
import select
import socket
import subprocess
import time
import scanning as scanning_service
from math import ceil
from pathlib import Path
import config
from typing import Optional

import enlighten
import psutil
import yaml
from Crypto.Cipher import AES, DES
from Crypto.Random import get_random_bytes


from benchmarkapi import get_cpu_usage_pct, get_ram_total, get_ram_usage

parser=argparse.ArgumentParser(description='socket tool for very easy transfering data',epilog='Attention : if it is going to be a client you most to enter server ip and port too')
parser.add_argument("operation",metavar='operation',help="Choice to be client or server put 'c' for client and 's' for server 'scan' for scan IPs" )
parser.add_argument('-ip',"--serverip",metavar='serverip',help="Enter ip of server")
parser.add_argument('-p',"--port",metavar='port',help="Enter port number of server")
parser.add_argument('-key',"--key",metavar='key',help="Enter key file only if it is client and encrypt is ON")
args=parser.parse_args()
client,scan=False,False
with open("config.yml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)  #dump in reverse 

def current(network_id: str, use_plugin: Optional[str], verbose: bool):
    """ Look at who is currently on the network """
    print("Scanning...")
    scan_id = scanning_service.scan_network_single(network_id, use_plugin, verbose)
    discoveries = scanning_service.get_discoveries_from_scan(scan_id)

    print(f'+-{"-"*17}---{"-"*15}---{"-"*30}-+')
    print(f'| {"MAC Address":^17} | {"IP Address":^15} | {"Hostname":^30} |')
    for discovery in discoveries:
        print(f'| {discovery.device.mac_address:<17} | {discovery.ip_address:^15} | {discovery.hostname:^30} |')
    print(f'+-{"-"*17}---{"-"*15}---{"-"*30}-+')
        
if args.operation=="c" or args.operation=="cd":
    try:
        client=True
        PORT=int(args.port)
        serverip=args.serverip
        if data_loaded['encrypt']['encrypt']:
            key=args.key
            if key==None:
                raise('error')
        if args.operation=="cd":
            logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s',level=logging.DEBUG,filename='client_debug.log',filemode='w') #for debugging
        else:
            import warnings
            warnings.filterwarnings('ignore')
            logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s', level=logging.INFO)
    except Exception:
        raise Exception("Enter ip and port number and key file only if encrypt is ON with -ip & -p & -key")
elif  args.operation=="s" or args.operation=="sd":
    try:
        predifined=True
        PORT=int(args.port)
    except:
        PORT=0
        predifined=False
    if args.operation=="sd":
        logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s',level=logging.DEBUG,filename='server_debug.log',filemode='w') #for debugging
    else:
        import warnings
        warnings.filterwarnings('ignore')
        logging.basicConfig(format='%(asctime)s : %(levelname)s -> %(message)s', level=logging.INFO)  

elif args.operation=="scan":     
    scan=True   
    current(config.DEFAULT_NETWORK_ID,config.DEFAULT_PLUGIN,config.VERBOSE)
    
else:
    raise("OPERATION NOT DITECTED CHOSE ONE OF THIS (c,s,cd,sd,scan,test)")
    
LOGGER = logging.getLogger('sockettool')

def gen():
    for i in range(100):
        yield

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def cls():
    os.system('cls' if platform.system()=='Windows' else 'clear')
    
def wlan_ip():
    global admin,cpumodel
    admin=True
    if platform.system()=='Windows':
        cpumodel=platform.processor()
        LOGGER.info("Windows os detected")
        if is_admin():
            LOGGER.info("admin checked")
        else:
            LOGGER.warning("admin permission might be required !")
            admin=False
        result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True).stdout.lower()
        scan=0
        for i in result.split('\n'):
            if 'wireless' in i: scan=1
            if scan:
                if 'ipv4' in i: return i.split(':')[1].strip() 
                if 'IPv4' in i: return i.split(':')[1].strip() 

    elif subprocess.check_output(['uname','-o']).strip()==b'Android':
        cpumodel=platform.processor()
        LOGGER.info("Android os detected")
        return "192.168.43.1"            
    elif platform.system()=='Linux':
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).strip().decode('utf-8')
        counter=0
        for line in all_info.split("\n"):
            if "model name" in line:
                name=line
                counter=counter+1
        cpumodel=name[13:]      
        LOGGER.info("Linux os detected")
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
global firsttry,trynumber,maxramusage
firsttry,trynumber,maxramusage=True,0,0
LOGGER.info("system info {} number of cpu's {}, frequence {}".format(cpumodel,psutil.cpu_count(),psutil.cpu_freq()))
beginingramusage=ceil(get_ram_usage())
def get_status():
    global maxramusage
    ram=ceil(get_ram_usage())-beginingramusage
    if  ram>maxramusage:
        LOGGER.info("Total ram {} MB, ramusage {} MB cpuusage {}".format(ceil(get_ram_total()),ram,get_cpu_usage_pct()))
        maxramusage=ram
def check_mem(THRESHOLD):
    mem = psutil.virtual_memory() 
    av=mem.available
    if  av<= THRESHOLD:
        LOGGER.debug("Not enough memory available")
        return False
    else:
        LOGGER.debug("Memory checked {} GB available".format(av/2**30))   
        return True 
        
def encipher(data):
    ct_bytes = cipher.encrypt(data)
    return cipher.iv,ct_bytes
        
def decipher(data,cipher):
    return cipher.decrypt(data)
        
def set_buffersize(size,buffer_size):
    temp=int(round(size/buffer_size,0))
    a=1
    #if temp%2==1: #odd
    while 1:
        a=a+1
        temp=temp+a
        t=size/temp
        if round(t-int(t),2)<=0.05:
            break
    buffer_size=int(round(t,0))
    #else: 
    #    buffer_size = int(10000000/a)
    LOGGER.debug("buffer_size:{}, a:{}".format(buffer_size,a))
    return buffer_size  

def makeserver(PORT):
    global firsttry,trynumber
    connected_clients_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        if predifined:
            server_socket.bind((HOST,PORT))
        else:    
            server_socket.bind((HOST, 0))
        server_socket.listen(10)
        PORT=server_socket.getsockname()[1]
        connected_clients_sockets.append(server_socket)
        buffer_size = 10000000
        Hugeflag,Hugeflagfinish=False,False
        if data_loaded['encrypt']['encrypt']: 
            LOGGER.info('listening on : '+str(HOST)+':'+str(PORT) + ' secured by '+data_loaded['encrypt']['algorithm'])
            if args.operation=="sd" or args.operation=="cd":
                print('listening on : '+str(HOST)+':'+str(PORT) + ' secured by '+data_loaded['encrypt']['algorithm'])
        else:
            LOGGER.info('listening on : '+str(HOST)+':'+str(PORT))  
            if args.operation=="sd" or args.operation=="cd":
                print('listening on : '+str(HOST)+':'+str(PORT))
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
                            if len(txt)>30:
                                LOGGER.debug("server received data")
                            else:
                                LOGGER.debug("server received {}".format(txt))
                        if txt.startswith('SIZE'):
                            tmp = txt.split()
                            name = tmp[1]
                            gender = tmp[2]
                            if gender=="Normal":
                                size = int(tmp[3])
                                if firsttry:
                                    LOGGER.info('I/O NAME {} & SIZE {} MB'.format(name,size/2**20))
                                    firsttry=False
                                LOGGER.debug("server sent GOT SIZE")
                                sock.send(b"GOT SIZE")
                                Hugeflag=False
                            else:
                                parts = int(tmp[3])
                                size = int(tmp[4])
                                LOGGER.info('I/O NAME {} Huge type & {} parts and size {} GB'.format(name,parts,size/2**30)) 
                                size=size*1.3333336 #predicting  
                                LOGGER.debug("server sent GOT SIZE")
                                sock.send(b"GOT SIZE")
                                Hugeflag=True  
                        elif txt.startswith('BYE'):
                            LOGGER.info('RECEIVED SUCCESSFULLY')
                            LOGGER.debug('recived : '+str(receiveddata)+' real size : '+str(size))
                            if data_loaded['encrypt']['encrypt']:
                                LOGGER.debug('Total decrypt time is {}'.format(decrypttime))
                            #return 
                            if Hugeflagfinish:
                                pass
                            else:
                                LOGGER.debug("server sent done")
                                sock.send(b"done")
                                Hugeflagfinish=False
                            buffer_size = 10000000
                            numbers=numbers-1
                            if numbers==0:
                                sock.shutdown(1)
                                return
                            else:
                                LOGGER.info("Downloading next one")    
                        elif txt.startswith('NUMBER'):  
                            tmp = txt.split() 
                            numbers = int(tmp[1]) 
                            if firsttry:
                                LOGGER.info("{} files are going to download ".format(numbers))
                            sock.send(b"ok")
                            LOGGER.debug("server sent ok")
                        elif data or Hugeflag:            
                            LOGGER.info('downloading... {} MB/b'.format(buffer_size/1048576))   
                            try:    
                                myfile = open('DATA/{}'.format(name), 'wb')
                            except:
                                os.mkdir("DATA") 
                                myfile = open('DATA/{}'.format(name), 'wb')   
                            if not data:
                                myfile.close()
                                break
                            #pbar = tqdm(unit='B',unit_scale=True,unit_divisor=1024,file=sys.stdout,total=size)
                            manager = enlighten.get_manager()
                            status = manager.status_bar(status_format=u'Sockettool{fill}Stage: {demo}{fill}{elapsed}',
                                                        color='red',
                                                        justify=enlighten.Justify.CENTER, demo='Downloading...',position=6,
                                                        autorefresh=True, min_delta=0.5)
                            manager.status_bar(name, position=5, fill='-',
                                    justify=enlighten.Justify.CENTER)                            
                            pbar=enlighten.Counter(color = 'red',desc=name, total = ceil(size), unit = 'B')
                            if Hugeflag:
                                pass
                            else:   
                                if data_loaded['encrypt']['encrypt'] and data_loaded['encrypt']['algorithm']=='AES':
                                    original = base64.b64decode(data)
                                    receiveddata=len(data)   
                                    LOGGER.debug("AES Original received {} receiveddata {}".format(len(original),receiveddata))
                                    cipher=AES.new(key, AES.MODE_CFB, iv=original[0:16])
                                    LOGGER.debug("iv received {}".format(original[0:16]))
                                    tic = time.clock()
                                    original=decipher(original[16:],cipher)
                                    toc = time.clock()
                                    decrypttime=toc - tic
                                elif data_loaded['encrypt']['encrypt'] and data_loaded['encrypt']['algorithm']=='DES':
                                    original = base64.b64decode(data)
                                    receiveddata=len(data)   
                                    LOGGER.debug("DES Original received {} receiveddata {}".format(len(original),receiveddata))
                                    cipher=DES.new(key, DES.MODE_OFB, iv=original[0:8])
                                    LOGGER.debug("iv received {}".format(original[0:8]))
                                    tic = time.clock()
                                    original=decipher(original[16:],cipher)    
                                    toc = time.clock()
                                    decrypttime=toc - tic
                                else :
                                    original = base64.b64decode(data)
                                    receiveddata=len(data)
                                LOGGER.debug("Original received {}".format(len(original)))    
                            if Hugeflag:
                                remainpart=parts
                                for i in range(parts):
                                    t1=time.time()
                                    txt=sock.recv(2048)
                                    LOGGER.debug("server received {}".format(txt))
                                    tmp = txt.split()
                                    partnumber=int(tmp[1].decode('utf-8'))
                                    size=int(tmp[3].decode('utf-8'))
                                    if data_loaded['encrypt']['encrypt']:
                                        iv=base64.b64decode(tmp[4])
                                        cipher=AES.new(key, AES.MODE_CFB, iv=iv)
                                        LOGGER.debug("for i {} and partnumber {} size {} with iv".format(i,partnumber,size))
                                    else:
                                        LOGGER.debug("for i {} and partnumber {} size {}".format(i,partnumber,size))
                                    LOGGER.debug("server is going to download a chunk")
                                    receiveddata=0
                                    sock.send(b"ready")
                                    while receiveddata<size:
                                        data = sock.recv(buffer_size)
                                        get_status()
                                        try:
                                            if data_loaded['encrypt']['encrypt']:
                                                tic = time.clock()
                                                original+=decipher(base64.b64decode(data),cipher)
                                                toc = time.clock()
                                                decrypttime+=toc - tic
                                            else:    
                                                original += base64.b64decode(data)
                                        except:
                                            if data_loaded['encrypt']['encrypt']:
                                                tic = time.clock()
                                                original=decipher(base64.b64decode(data),cipher)
                                                toc = time.clock()
                                                decrypttime+=toc - tic
                                            else:  
                                                original = base64.b64decode(data) 
                                        pbar.update(ceil(len(data)))    
                                        receiveddata+=len(data)
                                        if not receiveddata<size:
                                            break
                                    LOGGER.debug("chunk downloaded") 
                                    sock.send(b'GOT IT')  
                                    txt=sock.recv(2048).decode('utf-8')
                                    remainpart=remainpart-1
                                    t=time.strftime("%H:%M:%S", time.gmtime(remainpart*(time.time() - t1)))
                                    status.update(demo='Downloading part number {}/{} estimated time: {}'.format(i+1,parts,t))                                
                                    if txt=="Next":
                                        pass     
                                if data_loaded['encrypt']['encrypt']:
                                    LOGGER.debug('Total decrypt time is {}'.format(decrypttime))       
                                LOGGER.info('saveing...')
                                myfile.write(original)
                                myfile.close()    
                                sock.send(b'done')
                                get_status()
                                Hugeflag,Hugeflagfinish=False,True
                            else:  
                                pbar.update(len(data))
                                LOGGER.debug("server is going to download")
                                while receiveddata<size:
                                    data = sock.recv(buffer_size)
                                    receiveddata+=len(data) 
                                    if data_loaded['encrypt']['encrypt']:
                                        tic = time.clock()
                                        original+=decipher(base64.b64decode(data),cipher)
                                        toc = time.clock()
                                        decrypttime+=toc - tic
                                    else:    
                                        original +=  base64.b64decode(data)
                                    LOGGER.debug("Original received in while {} receiveddata {}".format(len(original),receiveddata))        
                                    get_status()   
                                    pbar.update(ceil(len(data)))
                                    status.update(demo='Downloading...')                               
                                LOGGER.info('saveing...')
                                myfile.write(original)
                                myfile.close()
                                LOGGER.debug("server sent GOT IT")
                                sock.send(b"GOT IT")
            except Exception as E:
                if E.args[0]=="Incorrect padding" : 
                    LOGGER.debug("server sent RETRY Error code {}".format(E.args[0]))
                    sock.send(b"RETRY")
                    manager.stop()  
                    buffer_size=set_buffersize(size,buffer_size)
                    LOGGER.debug("buffersize set to : "+str(buffer_size))
                    Hugeflag=False
                elif E.args[0].startswith("Invalid base64-encoded string:"):
                    trynumber=trynumber+1
                    Hugeflag=False
                    if trynumber>=2:
                        buffer_size=set_buffersize(size,buffer_size)
                        LOGGER.debug("buffersize set to : "+str(buffer_size))
                    LOGGER.info("Invalid file retrying...")
                    LOGGER.debug("server sent RETRY")  
                    sock.send(b"RETRY")
                    manager.stop()   
                else :
                    Hugeflag=False
                    LOGGER.error(E,exc_info=True)
                    LOGGER.error(E.args[0])
                    manager.stop()  
                cls()    
                sock.close()
                connected_clients_sockets.remove(sock)
                continue
        server_socket.close()
    except Exception as E:
        if not admin:
            raise Exception("Admin permission required !")
        else:    
            LOGGER.error(E,"ip :",HOST)
            LOGGER.error("you are offline")  
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
        raise("there is nothing to send put file's in SEND directory")
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
    global message,datas,myfile,firsttry
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        # open inputdata
        sock.send(bytes("NUMBER {}".format(len(datas)),'utf-8'))
        LOGGER.debug("client sent NUMBER {}".format(len(datas)))
        count=len(datas)
        answer = sock.recv(4096)
        answer=answer.decode('utf-8')
        if answer=="ok":
            pass 
        else:
            LOGGER.debug("client is waited for ok message from server")
            while True:
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                if answer=="ok":
                    break 
        for i in range(count):
            myfile = open(datas[0], 'rb')
            name=os.path.basename(myfile.name).replace(" ","_")
            if firsttry:
                LOGGER.info('Reading {}'.format(name))
            fsize=Path(datas[0]).stat().st_size
            if  fsize>200*2**20 or not check_mem(fsize): #it is huge
                manager = enlighten.get_manager()           
                status = manager.status_bar(status_format=u'Sockettool{fill}Stage: {demo}{fill}{elapsed}',
                            color='red',
                            justify=enlighten.Justify.CENTER, demo='Uploading...',position=6,
                            autorefresh=True, min_delta=0.5)
                manager.status_bar(name, position=5, fill='-',
                        justify=enlighten.Justify.CENTER) 
                parts=ceil(fsize/10000000)        
                pbar=enlighten.Counter(color = 'red',desc=name, total = parts,unit = 'P')
                LOGGER.info('Huge file detected {} about {} GB'.format(name,fsize/2**30))
                sock.send(bytes("SIZE {} Huge {} {}".format(name,parts,fsize),'utf-8'))
                LOGGER.debug("client sent SIZE {} Huge {} {}".format(name,parts,fsize))
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                LOGGER.debug("client received {}".format(answer))
                if answer=="GOT SIZE":
                    pass
                else:
                    LOGGER.debug("client is waiting for GOT SIZE")
                    while True:
                        answer = sock.recv(4096)
                        answer=answer.decode('utf-8')
                        if answer=="GOT SIZE":
                            break             
                s,remainpart=0,parts
                for count in range(ceil(parts)):
                    t1=time.time()
                    piece=read1k()
                    if data_loaded['encrypt']['encrypt']:
                        tic = time.clock()
                        iv,piece=encipher(piece)
                        toc = time.clock()
                        encrypttime+=toc - tic
                        s=s+len(piece)
                        as_text_base64 = base64.b64encode(piece)
                        LOGGER.debug("client sent enciphered PART {} size {} with iv".format(count,len(as_text_base64)))
                        sock.send(bytes("PART {} size {} ".format(count,len(as_text_base64)),'utf-8')+iv)
                    else:    
                        s=s+len(piece)
                        as_text_base64 = base64.b64encode(piece)
                        LOGGER.debug("client sent PART {} size {}".format(count,len(as_text_base64)))
                        sock.send(bytes("PART {} size {}".format(count,len(as_text_base64)),'utf-8'))
                    answer = sock.recv(4096)
                    answer=answer.decode('utf-8')
                    LOGGER.debug("client received {}".format(answer))
                    if answer=="ready":
                        LOGGER.debug("client is going to send a chunk")
                        get_status()
                        sock.sendall(as_text_base64)
                        answer = sock.recv(4096)
                        answer=answer.decode('utf-8')
                        LOGGER.debug('server answer = %s' % answer)
                        if answer == 'GOT IT' :
                            LOGGER.debug("clinet sent Next chunk")
                            sock.send(b"Next")
                        elif answer=='RETRY':
                            sock.close()
                            while True:
                                LOGGER.info('RETRYING...')
                                if retrying(as_text_base64)=='GOT IT':
                                    pass  
                    pbar.update(1)
                    remainpart=remainpart-1
                    t=time.strftime("%H:%M:%S", time.gmtime(remainpart*(time.time() - t1)))
                    status.update(demo='Uploading part number {}/{} estimated time: {}'.format(count+1,ceil(parts),t))                                
                    if s==fsize:
                        break     #all parts sent
                datas.remove(datas[0]) 
                LOGGER.info('HUGE DATA SUCCESSFULLY SENT TO SERVER')  
                if data_loaded['encrypt']['encrypt']:
                    LOGGER.debug('Total encrypt time is {} s'.format(encrypttime)) 
                answer = sock.recv(4096).decode('utf-8')
                LOGGER.debug("client recived {}".format(answer))
                if answer=="done" and len(datas)>0:
                    LOGGER.info('Sending next file')
                sock.sendall(b"BYE BYE ")
            else:
                buffer = myfile.read()
                if data_loaded['encrypt']['encrypt']:
                    tic = time.clock()
                    iv,buffer=encipher(buffer)
                    toc = time.clock()
                    encrypttime=toc - tic
                    LOGGER.debug('Normal iv {} iv encode {}'.format(len(iv),len(base64.b64encode(iv))))
                    #as_text_base64 = base64.b64encode(buffer)
                    ##as_text_base64=base64.b64encode(iv)+as_text_base64 
                    as_text_base64=base64.b64encode(iv+buffer)
                else:    
                    as_text_base64 = base64.b64encode(buffer)
                size = len(as_text_base64)
                if firsttry:
                    LOGGER.info('BUFFER size '+str(fsize/2**20)+' MB file size '+str(size/2**20)+' MB')
                    firsttry=False
                # send inputdata size to server
                sock.send(bytes("SIZE {} Normal {}".format(name,size),'utf-8'))
                answer = sock.recv(4096)
                answer=answer.decode('utf-8')
                LOGGER.debug('server answer = %s' % answer)
                if answer == 'GOT SIZE':
                    LOGGER.info('sending...')
                    get_status()
                    sock.sendall(as_text_base64)
                    # check what server send
                    answer = sock.recv(4096)
                    answer=answer.decode('utf-8')
                    LOGGER.debug('server answer = %s' % answer)
                    if answer == 'GOT IT' :
                        sock.sendall(b"BYE BYE ")
                        LOGGER.info('DATA SUCCESSFULLY SENT TO SERVER')
                        if data_loaded['encrypt']['encrypt']:
                            LOGGER.debug('Total encrypt time is {} s'.format(encrypttime))
                        datas.remove(datas[0])
                        answer = sock.recv(4096).decode('utf-8')
                        if answer=="done" and len(datas)>0:
                            LOGGER.info('Sending next file')
                    elif answer=='RETRY':
                        LOGGER.info('RETRYING...')
                        sock.close()
                        return False
                myfile.close()
        LOGGER.info('TRANSPORTATION FINISHED')    
        return True
    except Exception as E:
        if E.args[0]==10054:
            LOGGER.error("An error acured in server retrying...")
        elif E.args[0]==101:
            LOGGER.error('Connection crupted check connection and try again')
            sock.close()
            raise('Network not found')
        elif E.args[0]==104: #broken pipe 
            LOGGER.info('Speed down and retrying...')
        elif E.args[0]==111: #broken pipe 
            LOGGER.info('Still searching for {}:{}'.format(serverip,PORT))
        else:    
            LOGGER.error(E.args[0],exc_info=True)   
        try:    
            manager.stop()        
        except:
            if E.args[0]==111:
                time.sleep(10)
            elif E.args[0]==104:
                pass
            else:    
                raise('server not found!!!')
        sock.close()
        return False
def connect():
    global datas
    datas=inputdata()
    while 1:
        if send():
            return
        cls()
        time.sleep(2)

if __name__ == '__main__':
    if scan :
        print('Done')
    elif client:      
        if data_loaded['encrypt']['encrypt']:    
            if data_loaded['encrypt']['algorithm']=='AES':
                if not os.path.exists(key): 
                    raise('key not found!!!')
                else:
                    file_in = open(key, "rb") # Read bytes
                    key = file_in.read() 
                    file_in.close()
                cipher = AES.new(key, AES.MODE_CFB)
            elif  data_loaded['encrypt']['algorithm']=='DES':
                if not os.path.exists(key): 
                    raise('key not found!!!')
                else:
                    file_in = open(key, "rb") # Read bytes
                    key = file_in.read() 
                    file_in.close()       
                cipher = DES.new(key, DES.MODE_OFB) 
            else:
                raise('algorithm is not supported just AES or DES')
            LOGGER.info("Start connecting to server secured by {}".format(data_loaded['encrypt']['algorithm']))        
        else:
            LOGGER.info("Start connecting to server")    
        if os.path.isdir(r'./SEND'):
            pass
        else:
            os.mkdir("SEND") 
        connect()
    else:      
        if data_loaded['encrypt']['encrypt']:    
            if data_loaded['encrypt']['algorithm']=='AES':
                if not os.path.exists('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm'])): 
                    key=get_random_bytes(16)
                    file_out = open('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm']), "wb") # wb = write bytes
                    file_out.write(key)
                    file_out.close() 
                else:
                    file_in = open('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm']), "rb") # Read bytes
                    key = file_in.read() 
                    file_in.close()
            elif  data_loaded['encrypt']['algorithm']=='DES':
                if not os.path.exists('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm'])): 
                    key=get_random_bytes(8)
                    file_out = open('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm']), "wb") # wb = write bytes
                    file_out.write(key)
                    file_out.close() 
                else:
                    file_in = open('{}_{}_KEY.bin'.format(getpass.getuser(),data_loaded['encrypt']['algorithm']), "rb") # Read bytes
                    key = file_in.read() 
                    file_in.close()       
            else:
                raise('algorithm is not supported just AES or DES')
        LOGGER.info("Starting server")
        makeserver(PORT)    
