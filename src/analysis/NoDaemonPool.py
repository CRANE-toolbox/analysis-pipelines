# Credit to the following SO for this custom thread pool
# https://stackoverflow.com/a/53180921
# The pool allows us to run the LDA multicore inside a thread pool(nested pools of threads basically)
#

import multiprocessing


class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess


# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NoDaemonPool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(NoDaemonPool, self).__init__(*args, **kwargs)
