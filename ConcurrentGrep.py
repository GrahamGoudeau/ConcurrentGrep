import os
import sys
import threading
import argparse
import resource

print_lock = threading.Semaphore(1)
open_file_limit, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
open_file_lock = threading.Semaphore(open_file_limit / 2)
default_thread_max = 2000

restricted_dirs = ['.git']

def search(dir, search_term, search_names, threadpool):
    global open_file_lock
    threadpool.acquire()

    contents = os.listdir(dir)
    directories = [item for item in contents if os.path.isdir(os.path.join(dir, item))]
    files = [item for item in contents if item not in directories]

    if dir[-1:] != '/':
        dir = dir + '/'

    threads = [threading.Thread(target=search, args=[dir + directory, search_term, search_names, threadpool])
                for directory in directories if directory not in restricted_dirs]

    for thread in threads:
        thread.start()

    if search_names:
        for file_name in files:
            if search_term in file_name:
                with print_lock:
                    print '='*30
                    print dir + file_name
    else:
        for file_name in files:
            with open_file_lock:
                with open(dir + file_name, 'r') as f:
                    if search_term in f.read():
                        with print_lock:
                            print '*'*30
                            print dir + file_name + ': ' + search_term

    threadpool.release()

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Concurrent grep')
    parser.add_argument('root_dir', default='.', help='root directory')
    parser.add_argument('search_term', help='Term to search for')
    parser.add_argument('-n', dest='search_names', action='store_true', help='Search file names')
    parser.add_argument('-t', dest='thread_max', type=int, default=default_thread_max,
                        help='Max number of threads; default 2000; > 0')
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
