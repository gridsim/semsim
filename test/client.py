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

    hlist = []

    with open("10000.lst", 'r') as f:
        for line in f:
            end = line.rfind('.')
            begin = line.rfind('-')
            hlist.append(int(line[begin + 1:end]))

    print hlist

    data_true = ''
    for i in hlist:
        data_true += 'thermostat_%06d True' % i
        data_true += LINE_SEPARATOR
        data_true += 'thermostat_boiler_%06d True' % i
        data_true += LINE_SEPARATOR

    data_false = ''
    for i in hlist:
        data_false += 'thermostat_%06d False' % i
        data_false += LINE_SEPARATOR
        data_false += 'thermostat_boiler_%06d False' % i
        data_false += LINE_SEPARATOR
    current_break = False

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

                        if time > 86400:  # day
                            finished = True
                            break
                        else:
                            data = ''
                            if time > 8*3600 and time < 15*3600:
                                if not current_break:
                                    data += data_false
                                    current_break = True
                            else:
                                if current_break:
                                    data += data_true
                                    current_break = False
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
