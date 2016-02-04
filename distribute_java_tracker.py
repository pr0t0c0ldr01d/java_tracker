import os
import os.path
import shutil
import sys
import pywin
import pywin32_system32
import win32wnet
import re
import getpass
import time

#Set up variables
#computers = "java_index.txt"
computers = "batch.txt"
file_to_copy = "usagetracker.properties"
username = input("Username:")
password = getpass.getpass(stream=sys.stdout)

#Define functions
def convert_unc(host, path):
    """ Convert a file path on a host to a UNC path."""
    return ''.join(['\\\\', host, '\\', path.replace(':', '$')])

def netcopy(host, source, dest_dir, username=None, password=None, move=False):
    """ Copies files or directories to a remote computer. """

    #wnet_connect(host, username, password)

    dest_dir = convert_unc(host, dest_dir)

    # Pad a backslash to the destination directory if not provided.
    if not dest_dir[len(dest_dir) - 1] == '\\':
        dest_dir = ''.join([dest_dir, '\\'])

    # Create the destination dir if its not there.
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
    # Create a directory anyway if file exists so as to raise an error.
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

    if move:
        return shutil.move(source, dest_dir)
    else:
        return shutil.copy(source, dest_dir)



def wnet_connect(host, username, password):
    unc = ''.join(['\\\\', host])
    try:
        win32wnet.WNetAddConnection2(0, None, unc, None, username, password)
    except Exception as err:
        if isinstance(err, win32wnet.error):
            # Disconnect previous connections if detected, and reconnect.
            if err[0] == 1219:
                win32wnet.WNetCancelConnection2(unc, 0, 0)
                return wnet_connect(host, username, password)
        raise err


def wnet_disconnect(host):
    unc = ''.join(['\\\\', host])
    win32wnet.WNetCancelConnection2(unc, 0, 0)


def distribute(remote_dir,filename):
    if os.path.exists(remote_dir):
            for name in os.listdir(remote_dir):
                if os.path.isfile(remote_dir + name):
                    print (remote_dir + name + ": Regular File. Skipping...")
                    continue
                destination = remote_dir + name + "\\lib\\management"
                destinationfile = destination + "\\" + filename
                if not os.path.exists(destination):
                    os.makedirs(destination)
                    print (destination + ": Created")
                if os.path.exists(destinationfile):
                    print (destinationfile + ": File exists")
                else:
                    shutil.copy(filename, destination)
                    if os.path.exists(destinationfile):
                        print (destinationfile + ": File copied successfully")

with open(computers) as f:
    for line in f:
        host = line.rstrip()
        try:
            wnet_connect(host=host,username=username,password=password)
        except Exception as err:
            print(host,err)
            continue
        remote_dir_32 = "\\\\" + host + "\\c$\Program Files (x86)\\Java\\"
        remote_dir_64 = "\\\\" + host + "\\c$\Program Files\\Java\\"
        distribute(remote_dir_32,file_to_copy)
        distribute(remote_dir_64,file_to_copy)

        wnet_disconnect(host)
