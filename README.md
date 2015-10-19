# ConcurrentGrep

### Description
Search for file names or file contents recursively from the given directory tree root.  Each recursive call spawns a thread for each sub-directory before checking the contents of its own directory for the pattern.
### Command Line Arguments
- -n: Switch to searching by file names instead of file contents
- -t {int}: Set the maximum size of the threadpool; defaults to 2000; greater than 0
