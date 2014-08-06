# coding=utf-8
# !/usr/bin/python

"""
__synopsis__    : DropBox Files duplicate detector
__description__ :Checks if the there are duplicate files in the dropbox
                 account and report them
__project__     : dropbox_dup
__author__      : Subhadeep Maji, Samujjwal Ghosh
__version__     : " 0.1.1 "
__date__        : "25-Jun-14"
__copyright__   : "Copyright (c) 2014 Samujjwal_Ghosh"
__license__     : "Python"

script options
--------------
--drpbx_id : Dropbox user id of the user
--file     : output to be written to a file

__classes__     :

__variables__   :

__methods__     :

"""

from hashlib import md5
from itertools import izip
from threading import RLock, Thread
from optparse import OptionParser

import webbrowser
import dropbox, pprint, pickle,\
    sys, simplejson as json, Queue


app_key = '85ahzkk3ix0m0q3'
app_secret = '0ox9bhf31thtp2v'


def connect_user(drpbx_id):
    """
    Connect a user to the app and get the
    client validation id

    @param drpbx_id : Email id of the user, login
    for DropBox
    """
    drpbx_id = drpbx_id.strip()
    user_info = None
    try:
        info_file = open("user_info.p", "r")
        user_info = pickle.load(info_file)
    except IOError:
        pass

    if user_info and drpbx_id in user_info:
        access_token = user_info[drpbx_id]
        client = dropbox.client.DropboxClient(access_token)
        return client

    db_flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    auth_url = db_flow.start()
    print "\n\nPlease Visit the URL and grant permissions to the App\n\n" +\
          auth_url
    webbrowser.open(auth_url)  # will open the URL in browser
    auth_code = raw_input("Enter Authentication Code::").strip()

    access_token, user_id = db_flow.finish(auth_code)
    client = dropbox.client.DropboxClient(access_token)

    accnt_mail_id = str(client.account_info()['email'])
    if accnt_mail_id != drpbx_id:
        print "You did not seem to have logged in from\n"\
              " your account, please login as: " + drpbx_id
        return None

    user_info = dict()
    user_info[drpbx_id] = access_token
    pickle.dump(user_info, open("user_info.p", "a"))
    return client


def get_all_files_metadata(client):
    """
    Get all the files meta-data info going recursively
    over directories

    @param client : A dropbox api client object
    """
    files_metadata = list()
    root_dir = "/"
    dir_queue = list()
    dir_queue.append(root_dir)
    print "Scanning folders for potential file matches:"
    while len(dir_queue):
        curr_dir = dir_queue.pop(0)
        dir_meta = client.metadata(curr_dir)
        print curr_dir
        if 'contents' in dir_meta:
            dir_content = dir_meta['contents']
            dir_queue.extend([d['path'] for d in dir_content if d['is_dir']])
            files_metadata.extend([f for f in dir_content if not f['is_dir']
                                   and not 'is_deleted' in f])

    return files_metadata


def split_by_size(files_metadata):
    """
    Split the files by size in bytes and report
    files with same size

    @param files_metadata : file_metadata as returned by
    the dropbox api
    """
    paths = [f['path'] for f in files_metadata]
    sizes = [f['bytes'] for f in files_metadata]

    path_to_size = dict(izip(paths, sizes))
    size_to_path = dict()
    for path, size in path_to_size.iteritems():
        if size not in size_to_path:
            size_to_path[size] = list()
        size_to_path[size].append(path)

    return [(k, v) for k, v in size_to_path.iteritems()
            if len(size_to_path[k]) > 1 and k > 0]


def compare_hash(client, files_by_size):
    """
    compare files by hash and report files which
    have same hash values

    @param client : A dropbox client object
    @param files_by_size : A list of list files of having
    same size by size
    """
    potential_dup_files = list()
    file_handles = Queue.Queue(maxsize=100)
    lock = RLock()
    printer = pprint.PrettyPrinter(indent=4)

    conn_closer = ConnectionCloser(file_handles, lock)
    conn_closer.start()
    print "Checking for duplicates, This might take a while..\n\n"
    for size, files in files_by_size:
        file_hashes = list()

        print "Checking duplicates in: \n"
        printer.pprint(files)

        for f in files:
            f_handle = client.get_file(f)
            file_data = f_handle.read(amt=4096)

            lock.acquire()
            if not file_handles.full():
                file_handles.put(f_handle)
            lock.release()
            hash_val = md5(file_data).hexdigest()
            file_hashes.append(hash_val)

        file_hashes = zip(files, file_hashes)
        same_hash_files = dict()

        for f, hash_val in file_hashes:
            if hash_val not in same_hash_files:
                same_hash_files[hash_val] = list()
            same_hash_files[hash_val].append(f)

        for hash_val, hash_files in same_hash_files.iteritems():
            if len(hash_files) > 1:
                potential_dup_files.append(tuple(hash_files))

    conn_closer.stop()
    return potential_dup_files


def report_potential_dups(client, opts):
    """
    Report Potential duplicate files from the entire user's
    Dropbox account

    @param client : DropBox client object
    @param opts : script options object
    """
    files_metadata = get_all_files_metadata(client)
    file_size_split = split_by_size(files_metadata)

    dup_files = compare_hash(client, file_size_split)
    txt = "Possible Duplicates" + "\n"
    txt += "-------------------" + "\n\n"
    printer = pprint.PrettyPrinter(indent=4)
    txt = printer.pformat(txt)
    txt += printer.pformat(dup_files)

    if opts.write_file == 0:
        print "\nNot writing in file as write_file = 0.\n"
        return txt

    if not opts.file:
        opts.file = "possible_duplicates.txt"

    try:
        f_handle = open(opts.file, "w")
        f_handle.write(txt)
    except IOError, e:  # todo: what to do with var "e"?
        print "Error Creating File, Dumping Output\n\n"
        return txt

    return txt


def parse_options():
    """
    Parse script options
    """
    parser = OptionParser()
    parser.add_option("-u", "--drpbx_id", help="Dropbox user id of the user")
    parser.add_option("-f", "--file", help="write output to a file; default"
                                           " file name: 'possible_duplicates."
                                           "txt")
    parser.add_option("-n", "--write_file", help="do not write output"
                                                 " if value=0; default: !0")
    opts, args = parser.parse_args()
    return opts


class ConnectionCloser(Thread):
    """
    A class that works as a thread to clear used
    socket connections
    """

    def __init__(self, queue, lock):
        Thread.__init__(self)
        self.queue = queue
        self.lock = lock
        self.grace_stop = False

    def run(self):
        """
        Runs
        """
        while True:
            fp = None
            if self.grace_stop:
                break

            self.lock.acquire()
            if not self.queue.empty():
                fp = self.queue.get()
            self.lock.release()

            if fp:
                fp.close()

    def stop(self):
        """
        Stopa
        """
        self.grace_stop = True


if __name__ == "__main__":
    opts = parse_options()

    print "Started"
    if not opts.drpbx_id:
        opts.drpbx_id = raw_input("Please provide user-id for DropBox: ")
    if not opts.drpbx_id:
        print "DropBox user-id not provided, Quitting!"
        sys.exit(1)

    client = connect_user(opts.drpbx_id)
    while not client:
        retry = raw_input("Error getting connection, check internet connection,"
                          " retry? (y/n;default:n): ")
        if retry != 'y':
            sys.exit(1)
        client = connect_user(opts.drpbx_id)

    print report_potential_dups(client, opts)