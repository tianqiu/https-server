#-*- coding:utf-8 -*-
import socket, select,ssl,urllib,os,time
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
header  = b'HTTP/1.0 200 OK\r\n'
header += b'Content-Type: text/html\r\nConnection:keep-alive\r\ncharset=UTF-8\r\n\r\n'
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('192.168.1.104', 8888))
serversocket.listen(100)
serversocket.setblocking(0)
epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN)
cwd=os.getcwd()


##外部调用php或python文件等各种脚本文件
def dealphp(path,url,method,request,types):
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
        else:
            if types=='py':
                v=os.popen('python '+cwd+path)
            elif types=='c':
                os.system('gcc '+cwd+path+' -o '+cwd+path[0:-2])
                v=os.popen(cwd+path[0:-2]).read()
                os.system('rm '+cwd+path[0:-2]+' -f') 
            else:
                v=os.popen(types+' '+cwd+path)
            return v.read()
    else:
        po=request.split('\n\r\n')[1]
        if po!='':
            print "po"
            cann=po.split('&')
            print 'cann'
            a=[i.split('=')[1] for i in cann]
            print a
            b=' '
            i=0
            while i<len(a):
                b=b+' '+a[i]
                i=i+1
            print 'B'

            print b
            if types=='py':
                v=os.popen('python '+cwd+path+b).read()
            elif types=='c':
                os.system('gcc '+cwd+path+' -o '+cwd+path[0:-2])
                v=os.popen(cwd+path[0:-2]+b).read()
                os.system('rm '+cwd+path[0:-2]+' -f')
            else:
                v=os.popen(types+' '+cwd+path+b).read()
            v=urllib.unquote(v)
            return header+v       

##外部调用html文件
def dealhtml(path):
    f=open(cwd+path,"rb")
    y=f.read()
    y=header+y
    return y

##外部调用js和css文件
def dealjs(path):
    f=open(cwd+path,"rb")
    y=f.read()
    f.close()
    return y

##处理的到的请求
def dealresponse(request):
    method=request.split(' ')[0]
    if len(request.split(' '))>1:
     url=request.split(' ')[1]
     path=url.split('?')[0]
     if method=='GET' or method=='POST':
        if path=='/':
            if method=='POST':
                po=request.split('\n\r\n')[1]
                print "po"
                cann=po.split('&')
                print 'cann'
                a=[i.split('=')[1] for i in cann]
                print a
                b=' '
                i=0
                while i<len(a):
                    b=b+' '+a[i]
                    i=i+1
                print b
            f=open("index.html","rb")
            x=header+f.read()
            f.close()
            return x
        else:
            if os.path.exists(cwd+path):
                types=path.split('.')[-1]
                b=' '
                if len(url.split('?'))>1:
                    can=url.split('?')[1]
                    cann=can.split('&')
                    a=[i.split('=')[1] for i in cann]
                    i=0
                    while i<len(a):
                        b=b+' '+a[i]
                        i=i+1
                if path=='/his.txt':
                    if a[0]!='undefined':
                        b=urllib.unquote(b)
                        v=os.system('python sub.py '+b)
                    f=open("his.txt","r")
                    v=f.read()
                    f.close()
                    return v
                if types=='html':
                    return dealhtml(path)
                elif types=='php' or types=='py' or types=='c' or types=='sh':
                    return dealphp(path,url,method,request,types)
                elif (types=='js' or types=='css'):
                    return dealjs(path)
                else:
                    f=open(cwd+path,"rb")
                    x=f.read()
                    f.close()
                    return x
            else:
                f=open("index.html","rb")
                x=header+f.read()
                f.close()
                return x  




################################################################################
try:
    print serversocket.fileno()
    connections = {}; requests = {}; responses = {};connstream={}
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            print events
            if fileno == serversocket.fileno():
                print ("a")
                connection, address = serversocket.accept()
                connection.setblocking(0)
                #print connection.fileno()               
                epoll.register(connection.fileno(), select.EPOLLIN)
                connstream[connection.fileno()] = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=False)
                connstream[connection.fileno()].setblocking(0)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = b''
            elif event & select.EPOLLIN:
                print("b")
                while True:
                    try:
                        connstream[fileno].do_handshake()
                        requests[fileno] += connstream[fileno].recv(1024)
                        break
                    except ssl.SSLWantReadError:
                        #print("sslerror")
                    
                        pass
                    except:
                        print("f")
                        try:
                            connstream[fileno].shutdown(socket.SHUT_RDWR)
                        except:
                            pass
                        try:
                            connections[fileno].shutdown(socket.SHUT_RDWR)
                        except:
                            pass

                        epoll.unregister(fileno)
                        connstream[fileno].close()
                        connections[fileno].close()
                        del connections[fileno]
                        del connstream[fileno]
                        break
                print('yes')
                if requests[fileno]=='':
                    epoll.unregister(fileno)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                    epoll.modify(fileno, select.EPOLLOUT)
                    print('-'*40 + '\n' + requests[fileno])
                    responses[fileno]=dealresponse(requests[fileno])
            elif event & select.EPOLLOUT:
                print ("c")
                while True:
                    try:
                        print ("try")
                        connstream[fileno].do_handshake()
                        byteswritten = connstream[fileno].send(responses[fileno])
                        responses[fileno] = responses[fileno][byteswritten:]
                        break
                    except ssl.SSLWantReadError:
                        print ("wanterror")
                        pass
                    except :
                       # epoll.modify(fileno,0)
                        try:
                            connstream[fileno].shutdown(socket.SHUT_RDWR)
                        except:
                            pass
                        try:
                            connections[fileno].shutdown(socket.SHUT_RDWR)
                        except:
                            pass
  
                        epoll.unregister(fileno)
                        connstream[fileno].close()
                        connections[fileno].close()
                        del connections[fileno]
                        del connstream[fileno]                      
                        break
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
