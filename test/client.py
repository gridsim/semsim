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
    all_data = {}
    while True:
        try:
            data_buffer += mySocket.recv(4096)
            # print str(port) + '-> ' + data_buffer

            while LINE_SEPARATOR in data_buffer:
                reception, _, data_buffer = data_buffer.partition(LINE_SEPARATOR)
                reception = reception.replace("'", '"')
                print reception

                listrcv= json.loads(reception)

                if 'VALUE' in listrcv:
                    list_value = listrcv['VALUE']
                    key = list_value[0]+'.'+list_value[1]
                    if key not in all_data:
                        all_data[key] = []
                    all_data[key].append(float(list_value[3]))

                if 'STEP' in listrcv:
                    time = listrcv['STEP'][1]
                    print "time: "+str(time)

            if time > 86400*3:  # day
                break
            else:
                on_off = False  # bool(random.getrandbits(1))
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

    for k, d in all_data.iteritems():
        with open('output/'+k, 'w') as fd:
            fd.writelines([str(x)+'\n' for x in d])


if __name__ == "__main__":

    thread = threading.Thread(target=run, args=("localhost", 10600)).start()
