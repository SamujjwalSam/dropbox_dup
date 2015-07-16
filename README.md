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

`$ ./dropbox_dup.py

During `dropbox_dup.py` running, all the temporary files will be stored in `/tmp/` directory. 
And in the local dir, there will be a log file named `dropbox_dup.log` generated to give 
log information during `dropbox_dup.py` running.

__Prerequesit__ : Python 2.7

__Files__ :
- `dropbox_dup.py` : The main file which contains all the logic.
- 
  
__TODO__ :
- Integrate with MongoDB,
- Create a php page for accessing OAuth2,
- Deploy on cloud.
- Add other services
  - Onedrive
  - Google drive
  - Copy
  - Mega
