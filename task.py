from optparse import OptionParser
from Queue import Queue
from threading import Thread
import time
import random


class Worker(Thread):
    def __init__(self, id, queue, workers=None):
        Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.workers = workers
        self.daemon = True
        self.start()

    def run(self):
        id = self.id

        while True:
            while self.workers and self.queue.empty():
                id = len(self.workers)-1 if (id-1) < 0 else id-1
                if self.workers[id].get_queue().empty():
                    continue
                else:
                    callable = self.workers[id].get_queue().get()
                    task_done = self.workers[id].get_queue().task_done
                    break
            else:
                callable = self.queue.get()
                task_done = self.queue.task_done

            try:
                callable()
            except:
                print("Exception")
            finally:
                task_done()

    def get_queue(self):
        return self.queue


class Pool(object):
    def __init__(self, num_of_threads, steal=False):
        self.steal = steal
        self.num_of_threads = num_of_threads
        self.workers = {}

        if steal:
            for i in xrange(num_of_threads):
                self.workers[i] = \
                    Worker(i, Queue(num_of_threads), self.workers)
        else:
            self.queue = Queue(num_of_threads)

            for i in xrange(num_of_threads):
                self.workers[i] = \
                    Worker(i, self.queue)

    def add_work(self, callable):
        if self.steal:
            self.workers[
                random.randrange(0, self.num_of_threads)].get_queue(). \
                put(callable)
        else:
            self.queue.put(callable)

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        if self.steal:
            [worker.get_queue().join() for worker in self.workers.itervalues()]
        else:
            self.queue.join()

if __name__ == '__main__':
    parser = OptionParser()

    _, args = parser.parse_args()

    Flag = True if args[0] == '1' else False
    print(Flag)

    def compute(start):
        def fab(num=start):
            if num == 1:
                return 1
            elif num == 0:
                return 0
            else:
                return num*fab(num-1)
        return fab

    pool = Pool(8, Flag)

    begin_time = time.time()

    for i in xrange(500000):
        pool.add_work(compute((i+1) % 400))

    pool.wait_completion()

    elapse_time = time.time() - begin_time
    print(elapse_time)
