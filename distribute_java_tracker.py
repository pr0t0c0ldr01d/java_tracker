import os
import os.path
import shutil
import sys
import win32wnet
import getpass
import time


#Set up variables
computers = "batch.txt"
file_to_copy = "usagetracker.properties"


#Define functions
def convert_unc(host, path):
    """ Convert a file path on a host to a UNC path."""
    return ''.join(['\\\\', host, '\\', path.replace(':', '$')])


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
#This function actually does all the magic of the program. It iterates over all Java subdirectories and drops the
#usagetracker file in the right place. If that place does not exist or if the file exists already, or if there is some
#regular file in there which doesn't belong, it handles that by skipping the cruft and creating directories as needed.
#It verifies the copy and prints an insightful, one-line message for each action taken.
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

#Gather username and password the Python way
username = input("Username:")
password = getpass.getpass(stream=sys.stdout)

#This is the main program. It iterates over all the computers in the supplied file, connects to each, distributes
#the file, then closes the connection.

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
        time.sleep(1)
