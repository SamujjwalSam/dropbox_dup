dropbox_dup
===========
__Synopsis__    : DropBox Files duplicate detector.

__Description__ :Checks if the there are duplicate files in the dropbox account and report them.
                 
__Project__     : dropbox_dup,

__Author__      : Samujjwal Ghosh, Subhadeep Maji.

__Version__     : " 0.1.1 ",

__Date__        : "25-Jun-14",

__Copyright__   : "Copyright (c) 2014 Samujjwal_Ghosh",

__License__     : Python.

__How to Run__  : `dropbox_dup/` is the source code running in the server, which will generate an js file. This js file contains the trace information which will be used by the frontend js engine to render.

__To run it__   : 

`$ cd  dropbox_dup`

`$ ./dropbox_dup.py < hello.c > index.js`

put `index.js` to the python tutor `js/` directory, so that the front end could render it.

During `dropbox_dup.py` running, all the temporary files will be stored in `/tmp/` directory. 
And in the local dir, there will be a log file named `dropbox_dup.log` generated to give 
log information during `dropbox_dup.py` running.

__Prerequest__ : Python 2.7.

__Files__ :
- `dropbox_dup.py` : The main entry to run the CTutor.
- `Trace.py`: The class used to call lldb to generate the trace, and put it in a js file.
- `Trace_test.py`: Unit test for trace generator, currently still under development.
- `Makefile_buildlib`: Makefile used to generate the library used for heap memory management. We need to get information about the `malloc`, `alloca` and `free` function call. It is used to generate libsample.so by running `$make -f Makefile_buildlib`
- `sample.c`: The source code for a self-defined `malloc/alloc/free` function.
- `hello.c`: An example code used to generate js.
  
__TODO__ :
- Integrate with MongoDB,
- Create a php page for accessing OAuth2,
- Deploy on cloud.
- Add other services
  - Onedrive
  - Google drive
  - Copy
  - Mega
