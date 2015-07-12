#-*- coding:utf-8 -*-
import ssl,socket,gevent,time,urllib
header  = b'HTTP/1.0 200 OK\r\n'
header += b'Content-Type: text/html\r\nConnection:keep-alive\r\ncharset=UTF-8\r\n\r\n'
if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    bindsocket = socket.socket()
    bindsocket.bind(('',8000))
    while True:
        bindsocket.listen(5)
        newsocket, fromaddr = bindsocket.accept()
        if True:
            connstream = context.wrap_socket(newsocket, server_side=True)
            data = connstream.recv(1024)
            data=urllib.unquote(data)
           # data = data.encode(encoding)
            print "1"
            print(data)
            method=data.split(' ')[0]
            url=data.split(' ')[1]
            if method == 'POST':
                 f=open('index.html','a')
                 f.write("<p>"+data.split('=')[-1])
                 f.close()
            f=open('index.html','rb')
            index=f.read()
            f.close()     
            #index=index.decode(encoding)  
            urllib.quote(index)
            x="document.write('<p>asdf</p>');"
            if url=='/':
                connstream.send(header+index)
            else :
                connstream.send(x)
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()
            newsocket.close()
   
