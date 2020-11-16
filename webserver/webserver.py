import threading

from tornado import ioloop

class WebServer():
    application = None
    ioloop_instance = ioloop.IOLoop.instance()

    def __init__(self, configuration, application):
        self.application = application
        self.application.listen(configuration["port"])

    def start_block(self):
        self.ioloop_instance.start()

    def start_noblock(self):
        def start_ioloop(ioloop_instance):
            ioloop_instance.start()
        th = threading.Thread(target=start_ioloop, args=(self.ioloop_instance,))
        th.start()

    def stop(self):
        self.ioloop_instance.stop()
    
    def stop_condition(self):
        def stop_ioloop_condition(ioloop_instance, cv, lock):
            lock.acquire()
            cv.wait()
            ioloop_instance.stop()
            return
        lock = threading.Lock()
        lock.acquire()
        cv = threading.Condition(lock)
        th = threading.Thread(target=stop_ioloop_condition, args=(self.ioloop_instance, cv, lock))
        th.start()
        lock.release()
        return cv, lock