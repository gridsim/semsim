import socket
import sys
import random
import threading


def run(host, port):

    print("run "+str(host)+':'+str(port))

    LINE_SEPARATOR = '#'

    data_buffer = ""

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        mySocket.connect((host, port))
        mySocket.settimeout(1.)
    except socket.error:
        print "connection failed."
        sys.exit()
    print "OK for "+str(port)

    while True:
        try:
            data_buffer += mySocket.recv(4096)
            # print str(port) + '-> ' + data_buffer
            reception, separator, data_buffer = data_buffer.partition(LINE_SEPARATOR)
            # print reception, '|', separator, '|', data_buffer

            on_off = True # bool(random.getrandbits(1))
            # print on_off
            data = '{"receiver": "thermostat_%03d", "value": "%s"}' % ((port-60120), str(on_off))
            data+=LINE_SEPARATOR
            mySocket.send(data)
        except socket.error as e:
            print "error rised: "+str(e)
            if data_buffer:
                break
            else:
                continue

    mySocket.send(LINE_SEPARATOR)
    print "Interrupted connection."
    mySocket.close()
    print("close "+str(host)+':'+str(port))


if __name__ == "__main__":

    #for port in range(60121, 60221):
        thread = threading.Thread(target=run, args=("localhost", 60101)).start()
