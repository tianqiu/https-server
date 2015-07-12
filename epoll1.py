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

def dealphp(path):
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
    if method=='GET':
        if path=='/':
            f=open("1.html","rb")
            x=header+f.read()
            f.close()
            return x
        else:
            if os.path.exists(cwd+path):
                types=path.split('.')[-1]
                if types=='html':
                    return dealhtml(path)
                elif types=='php':
                    dealphp(path)
                elif (types=='js' or types=='css'):
                    return dealjs(path)
                elif types=='py':
                    dealpy(path)
            else:
                return " "   




################################################################################
try:
    connections = {}; requests = {}; responses = {}
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            if fileno == serversocket.fileno():
                print ("a")
                connection, address = serversocket.accept()
                connstream = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=False)
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = b''
            elif event & select.EPOLLIN:
                print("b")
                while True:
                    try:
                        connstream.do_handshake()
                        requests[fileno] += connstream.recv(1024)
                        break
                    except ssl.SSLWantReadError:
                        pass
                    except:
                        epoll.modify(fileno, 0)
                        break
                print('yes')
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
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
                        connstream.do_handshake()
                        byteswritten = connstream.send(responses[fileno])
                           # responses[fileno] = responses[fileno][byteswritten:]
                        break
                    except ssl.SSLWantWriteError:
                        pass
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                    epoll.modify(fileno, 0)
                    connstream.shutdown(socket.SHUT_RDWR)
                    try:
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                    except:
                        pass
            elif event & select.EPOLLHUP:
                print ("d")
                epoll.unregister(fileno)
                connstream.close()
                try:
                    connections[fileno].close()
                except: 
                    pass
                del connections[fileno]
finally:
    print ("e")
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
###############################################################################
