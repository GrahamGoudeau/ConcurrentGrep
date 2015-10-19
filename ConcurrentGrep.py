import os
import sys
import threading
import argparse

kill = False
num_active = 0
num_active_lock = threading.Semaphore(1)

def search(dir, search_term, search_names, threadpool):
    global num_active
    global kill
    if kill: return

    num_active_lock.acquire()
    num_active += 1
    num_active_lock.release()

    contents = os.listdir(dir)
    directories = [item for item in contents if os.path.isdir(os.path.join(dir, item))]
    files = [item for item in contents if item not in directories]

    if dir[-1:] != '/':
        dir = dir + '/'

    threads = [threading.Thread(target=search, args=[dir + directory, search_term, search_names, threadpool])
                for directory in directories if directory != '.git']

    for thread in threads:
        threadpool.acquire()
        thread.start()

    if search_names:
        if search_term in files:
            print '='*30
            print dir + search_term
    else:
        for file_name in files:
            with open(dir + file_name, 'r') as f:
                if search_term in f.read():
                    print '*'*30
                    print dir + file_name + ': ' + search_term

    num_active_lock.acquire()
    num_active -= 1
    num_active_lock.release()

    threadpool.release()

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Concurrent grep')
    parser.add_argument('root_dir', default='.', help='root directory')
    parser.add_argument('search_term', help='Term to search for')
    parser.add_argument('-n', dest='search_names', action='store_true', help='Search file names')
    parser.add_argument('-t', dest='thread_max', type=int, default=2000, help='Max number of threads; default 2000; > 0')
    parser.set_defaults(search_names=False)
    args = parser.parse_args()
    if args.thread_max < 1:
        parser.print_help()
        sys.exit(1)
    return args

def main(argv):
    args = parse_args(argv)
    threadpool = threading.Semaphore(args.thread_max)
    search(args.root_dir, args.search_term, args.search_names, threadpool)

if __name__ == '__main__':
    main(sys.argv)
