import os
import socket
import sys
import threading
import json
import random


def run(host, port):

    OUTPUT_DIR = 'output/'

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

    current_time = time = 0
    all_data = {}
    finished = False
    while not finished:
        try:
            data_buffer += mySocket.recv(4096)
            # print str(port) + '-> ' + data_buffer

            while LINE_SEPARATOR in data_buffer:
                reception, _, data_buffer = data_buffer.partition(LINE_SEPARATOR)
                reception = reception.replace("'", '"')
                # print reception

                listrcv = json.loads(reception)

                if 'VALUE' in listrcv:
                    list_value = listrcv['VALUE']
                    key = list_value[0]+'.'+list_value[1]
                    if key not in all_data:
                        all_data[key] = []
                    all_data[key].append(float(list_value[3]))

                if 'STEP' in listrcv:
                    time = listrcv['STEP'][1]
                    if current_time < time:
                        print "time: "+str(time)
                        current_time = time

                        if time > 86400/24:  # day
                            finished = True
                            break
                        else:
                            on_off = bool(random.getrandbits(1))
                            # print on_off
                            data = 'nothing %s' % str(on_off)
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

    try:
        mySocket.send(LINE_SEPARATOR)
        print "Interrupted connection."
        mySocket.close()
    except socket.error as e:
        print "error rised: " + str(e)

    print("close "+str(host)+':'+str(port))

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for k, d in all_data.iteritems():
        with open(OUTPUT_DIR+k, 'w') as fd:
            fd.writelines([str(x)+'\n' for x in d])


if __name__ == "__main__":

    thread = threading.Thread(target=run, args=("localhost", 10600)).start()
