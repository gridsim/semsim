import os
import sys
import multiprocessing
import time

import singlesim
import distsim
from recorders import SumRecorder
from gridsim.iodata.output import FigureSaver
from gridsim.decorators import timed


@timed
def main(argv):

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    args = argv[1:]

    # the '-d' option distributes the simulations
    if '-d' in args:

        processes = []

        # launch each simulation in its own thread
        for arg in [arg for arg in args if arg != '-d']:
            process = multiprocessing.Process(target=distsim.run, args=(arg,))
            processes.append(process)
            process.start()
        # here, simulations are waiting for connections
        print "Wait..."

        while processes:
            time.sleep(0.01)
            for p in processes:
                if not p.is_alive():
                    processes.remove(p)

        print "Go!"

        output_dir = "../output/dist/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for recorder, number in list(distsim.recorders.queue):
            if type(recorder) is SumRecorder:
                FigureSaver(recorder, "Power").save(output_dir+recorder.attribute_name+number+'.pdf')
            else:
                FigureSaver(recorder, "Temperature").save(output_dir+recorder.attribute_name+number+'.pdf')

        print "End of simulations"

    else:  # a standard run is started
        singlesim.run(args)

if __name__ == '__main__':
    main(sys.argv)