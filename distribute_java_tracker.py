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


#Pseudocode follows
#What I really need to do is say  if exists c:\program files\java  then foreach subdir of same, drop file in that dir\lib\management, same for c:\program files (x86)


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
        if os.path.exists(remote_dir_32):
            for name in os.listdir(remote_dir_32):
                if os.path.isfile(remote_dir_32 + "\\" + name):
                    continue
                destination = remote_dir_32 + name + "\\lib\\management"
                destinationfile = destination + "\\" + file_to_copy
                #result = netcopy(host=host, source=file_to_copy, dest_dir=destination, username=username, password=password, move=False)
                if not os.path.exists(destination):
                    os.makedirs(destination)
                if os.path.exists(destinationfile):
                    print (destinationfile + ": File exists")
                else:
                    shutil.copy(file_to_copy, destination)
                    if os.path.exists(destinationfile):
                        print (destinationfile + ": File copied successfully")
        if os.path.exists(remote_dir_64):
            for name in os.listdir(remote_dir_64):
                if os.path.isfile(remote_dir_32 + "\\" + name):
                    continue
                destination = remote_dir_64 + name + "\\lib\\management"
                destinationfile = destination + "\\" + file_to_copy
                if not os.path.exists(destination):
                    os.makedirs(destination)
                if os.path.exists(destinationfile):
                    print (destinationfile + ": File exists")
                else:
                    shutil.copy(file_to_copy, destination)
                    if os.path.exists(destination + "\\" + file_to_copy):
                        print (destinationfile + ": File copied successfully")


        wnet_disconnect(host)
        #time.sleep(1)
        #m = re.match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)",version)
        #if m.group(2) == "8":
        #    remote_dir = "\c$\Program Files (x86)\\Java\\jre" + m.group(1) + "." + m.group(2) + "." + m.group(3) + "_" + m.group(4) + "\\lib\\management"
        #else:
        #    remote_dir = "\c$\Program Files (x86)\\Java\\jre" + m.group(2) + "\\lib\\management"
        #result = netcopy(host=host, source=file_to_copy, dest_dir=remote_dir, username=username, password=password, move=False)
        #print (host,version,result)