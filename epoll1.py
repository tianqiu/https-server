#-*- coding:utf-8 -*-
import socket, select,ssl,urllib,os
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
header  = b'HTTP/1.0 200 OK\r\n'
header += b'Content-Type: text/html\r\nConnection:keep-alive\r\ncharset=UTF-8\r\n\r\n'
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 8888))
serversocket.listen(1)
serversocket.setblocking(0)
epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN)
cwd=os.getcwd()

def dealphp(path,url,method,request):
    if method=='GET':
        if len(url.split('?'))>1:
            can=url.split('?')[1]
            cann=can.split('&')
            a=[i.split('=')[1] for i in cann]
            b=' '
            i=0
            while i<len(a):
                b=b+' '+a[i]
                i=i+1
            v=os.popen('php '+cwd+path+b)
            return v.read()
        else:
            return os.popen('php '+cwd+path).read()
    else:
        po=request.split('\n\r\n')[1]
        print po 
        return os.popen('php '+cwd+path).read()       
def dealpy(path):
    pass

def dealhtml(path):
    f=open(cwd+path,"rb")
    y=f.read()
    y=header+y
    return y

def dealjs(path):
    f=open(cwd+path,"rb")
    y=f.read()
    f.close()
    return y


def dealresponse(request):
    method=request.split(' ')[0]
    url=request.split(' ')[1]
    path=url.split('?')[0]
    if method=='GET' or method=='POST':
        if path=='/':
            f=open("index.html","rb")
            x=header+f.read()
            f.close()
            return x
        else:
            if os.path.exists(cwd+path):
                types=path.split('.')[-1]
                if types=='html':
                    return dealhtml(path)
                elif types=='php':
                    return dealphp(path,url,method,request)
                elif (types=='js' or types=='css'):
                    return dealjs(path)
                elif types=='py':
                    return dealpy(path)
                else:
                    f=open(cwd+path,"rb")
                    x=f.read()
                    f.close()
                    return x
            else:
                return "  "   




################################################################################
try:
    print serversocket.fileno()
    connections = {}; requests = {}; responses = {};connstream={}
    while True:
        events = epoll.poll(1)
        print events
        for fileno, event in events:
            print events
            if fileno == serversocket.fileno():
                print ("a")
                connection, address = serversocket.accept()
                connection.setblocking(0)
                print connection.fileno()
                
                #connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connstream[connection.fileno()] = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=False)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = b''
            elif event & select.EPOLLIN:
                print("b")
                while True:
                    try:
                        #connstream[fileno].do_handshake()
                        requests[fileno] += connstream[fileno].recv(1024)
                        print "ffffff"+requests[fileno]
                        break
                    except ssl.SSLWantReadError:
                        #print("sslerror")
                        pass
                    except:
                        print("f")
                        epoll.modify(fileno,0)
                        #pass
                        break
                print('yes')
                if requests[fileno]=='':
                    epoll.unregister(fileno)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                #if True:
                    epoll.modify(fileno, select.EPOLLOUT)
                    requests[fileno]=urllib.unquote(requests[fileno].decode())
                    print('-'*40 + '\n' + requests[fileno])
             
                    responses[fileno]=dealresponse(requests[fileno])
                    #print(responses[fileno])
                    #responses[fileno]=header
            elif event & select.EPOLLOUT:
                print ("c")
                while True:
                    try:
                        print ("try")
                        #connstream[fileno].do_handshake()
                        byteswritten = connstream[fileno].send(responses[fileno])
                        responses[fileno] = responses[fileno][byteswritten:]
                        break
                    except ssl.SSLWantReadError:
                        print ("wanterror")
                        pass
                   
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                    epoll.modify(fileno, 0)
                    try:
                        connstream[fileno].shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    try:
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                    except:
                        pass
            elif event & select.EPOLLHUP:
                print ("d")
                epoll.unregister(fileno)
               
                connstream[fileno].close()
               
                connections[fileno].close()
                
                del connections[fileno]
                del connstream[fileno]
finally:
    print ("e")
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
###############################################################################
