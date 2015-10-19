import os
import sys
import threading
import argparse

HOME = os.path.expanduser('~')

def search(dir, search_term, search_names):
    print 'Spawning with ' + dir
    contents = os.listdir(dir)
    directories = [item for item in contents if os.path.isdir(os.path.join(dir, item))]
    files = [item for item in contents if item not in directories]

    if dir[-1:] != '/':
        dir = dir + '/'

    threads = [threading.Thread(target=search, args=[dir + directory, search_term, search_names])
                for directory in directories if directory != '.git']
    for thread in threads:
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

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Concurrent grep')
    parser.add_argument('root_dir', default='.', help='root directory')
    parser.add_argument('search_term', help='Term to search for')
    parser.add_argument('-n', dest='search_names', action='store_true', help='Search file names')
    parser.set_defaults(search_names=False)
    return parser.parse_args()

def main(argv):
    args = parse_args(argv)
    search(args.root_dir, args.search_term, args.search_names)

if __name__ == '__main__':
    main(sys.argv)
