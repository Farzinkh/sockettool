import argparse
import base64
import logging
import os
import select
import socket
import subprocess
import time

from tqdm import tqdm

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

parser=argparse.ArgumentParser(description='socket tool for very easy transfering data',epilog='Attention : if it is going to be a client you most to enter server ip and file address too')
parser.add_argument("operation",metavar='operation',help="Choice to be client or server put 'c' for client and 's' for server" )
parser.add_argument('-ip',"--serverip",metavar='serverip',help="Enter ip of server")
parser.add_argument('-f',"--file-address",metavar='file_address',help="Enter the address of file with it's name completely for example : blabla/hello.txt")
args=parser.parse_args()
client=False
if args.operation=="c":
    try:
        client=True
        inputdata=args.file_address
        serverip=args.serverip
    except Exception:
        raise Exception("Enter ip and file address with -ip and -f")

def wlan_ip():
    try:
        result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True).stdout.lower()
        scan=0
        for i in result.split('\n'):
            if 'wireless' in i: scan=1
            if scan:
                if 'ipv4' in i: return i.split(':')[1].strip() 
                if 'IPv4' in i: return i.split(':')[1].strip() 
    except:
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
PORT = 65432

def makeserver():
    connected_clients_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)
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
                            sock.shutdown(1)
                            logging.info('RECEIVED SUCCESSFULLY')
                            logging.info('recived : '+str(receiveddata)+' real size : '+str(size))
                            return

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
        logging.error(E,"ip :",HOST)
        logging.error("you are offline")  
        return

def send():
    global inputdata,message
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        sock.connect(server_address)
        # open inputdata
        myfile = open(inputdata, 'rb')
        name=os.path.basename(myfile.name)
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
            elif answer=='RETRY':
                logging.info('RETRYING...')
                sock.close()
                return False
        myfile.close()
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
    connect()
else:
    makeserver()    
