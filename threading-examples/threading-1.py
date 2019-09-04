import logging
import threading
import time

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    # Looks like a thread takes a function to run and then runs it. I
    # suppose the thread ends when the function ends? Perhaps there's
    # more fine-grained control for threads which are not intended to
    # stop?
    x = threading.Thread(target=thread_function, args=(1,))
    logging.info("Main    : before running thread")
    x.start()
    # How does this happen? Does sleep cause the main thread to
    # start running again?
    logging.info("Main    : wait for the thread to finish")
    x.join()
    logging.info("Main    : all done")
