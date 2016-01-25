import os
import sys
import threading

import singlesim
import distsim
from recorders import SumRecorder
from gridsim.iodata.output import FigureSaver


if __name__ == '__main__':

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    args = sys.argv[1:]

    # the '-d' option distributes the simulations
    if '-d' in args:

        threads = []

        # launch each simulation in its own thread
        for arg in [arg for arg in args if arg != '-d']:
            thread = threading.Thread(target=distsim.run, args=(arg,))
            threads.append(thread)
            thread.start()
        # here, simulations are waiting for connections
        print "Wait..."

        while threads:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)

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
