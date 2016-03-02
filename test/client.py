import socket
import sys
import threading
import json

def run(host, port):

    print("run "+str(host)+':'+str(port))

    LINE_SEPARATOR = '#'

    data_buffer = ""

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        mySocket.connect((host, port))
    except socket.error:
        print "connection failed."
        sys.exit()
    print "OK for "+str(port)

    time = 0
    while True:
        try:
            data_buffer += mySocket.recv(4096)
            # print str(port) + '-> ' + data_buffer
            reception, _, data_buffer = data_buffer.partition(LINE_SEPARATOR)
            reception = reception.replace("'", '"')
            print reception

            listrcv= json.loads(reception)

            if 'STEP' in listrcv:
                time = listrcv['STEP'][1]
                print "time: "+str(time)

            if time > 8600:
                break
            else:
                on_off = True  # bool(random.getrandbits(1))
                # print on_off
                data = 'thermostat_001 %s' % str(on_off)
                data += LINE_SEPARATOR
                data += 'STEP'
                data += LINE_SEPARATOR
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

    thread = threading.Thread(target=run, args=("localhost", 10600)).start()
