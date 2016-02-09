import os
import sys
import multiprocessing
import time

import distsim
from recorders import SumRecorder
from gridsim.iodata.output import FigureSaver
from gridsim.decorators import timed


@timed
def main(argv):

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    args = argv[1:]

    processes = {}

    # launch each simulation in its own thread
    for arg in [arg for arg in args if arg != '-d']:
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(target=distsim.run, args=(arg, child_conn))
        processes[process] = parent_conn
        process.start()
    # here, simulations are waiting for connections
    print "Wait..."

    while processes:
        time.sleep(0.01)
        for p in processes.keys():
            if p.is_alive():
                c = processes[p]
                while c.poll():
                    print c.recv()
            else:
                processes[p].close()
                del processes[p]

    print "Go!"

    output_dir = "../output/dist/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # for recorder, number in list(distsim.recorders.queue):
    #     if type(recorder) is SumRecorder:
    #         FigureSaver(recorder, "Power").save(output_dir+recorder.attribute_name+number+'.pdf')
    #     else:
    #         FigureSaver(recorder, "Temperature").save(output_dir+recorder.attribute_name+number+'.pdf')

    print "End of simulations"

if __name__ == '__main__':
    main(sys.argv)