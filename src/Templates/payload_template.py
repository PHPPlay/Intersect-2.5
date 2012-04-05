#!/usr/bin/python
# intersect 2.0 | created by ohdae
# copyright 2012
# payload_template to be used with Create.py

import sys, os, re, signal
from subprocess import Popen,PIPE,STDOUT,call
import platform
import shutil
import getopt
import tarfile
import socket
import urllib2
import random, string
import logging
import struct
import getpass
import pwd
import thread
import base64
import operator
import SocketServer, SimpleHTTPServer

cut = lambda s: str(s).split("\0",1)[0]
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

try:
    from scapy.all import *
except ImportError:
    try:
        from scapy import *
    except ImportError:
        print("Scapy is not installed. It can be downloaded here => https://www.secdev.org/projects/scapy/\n")

def environment():
    global Home_Dir
    global Temp_Dir
    global Config_Dir
    global User_Ip_Address
    global UTMP_STRUCT_SIZE    
    global LASTLOG_STRUCT_SIZE
    global UTMP_FILEPATH      
    global WTMP_FILEPATH       
    global LASTLOG_FILEPATH
    global distro
    global distro2

    ## Global variables for remote shells are defined during the creation process
    ## Variables for Scrub module. Do not change unless you know what you're doing. 
    UTMP_STRUCT_SIZE    = 384
    LASTLOG_STRUCT_SIZE = 292
    UTMP_FILEPATH       = "/var/run/utmp"
    WTMP_FILEPATH       = "/var/log/wtmp"
    LASTLOG_FILEPATH    = "/var/log/lastlog"

    distro = os.uname()[1]
    distro2 = platform.linux_distribution()[0]
 
    Home_Dir = os.environ['HOME']
    User_Ip_Address = socket.gethostbyname(socket.gethostname())
    
    Rand_Dir = ''.join(random.choice(string.letters) for i in xrange(12))
    Temp_Dir = "/tmp/lift-"+"%s" % Rand_Dir
    Config_Dir = Temp_Dir+"/configs/"

    if os.geteuid() != 0:
        print("[*] Intersect should be executed as a root user. If you are not root, Intersect can check for privilege escalation vulnerabilites.")
        print("[*] Enter '1' to check for possible vulnerabilities (privesc module must be loaded). Enter '99' to exit without checking.")
        option = raw_input("=> " )
        if option == '1':
            privesc()
            sys.exit()
        else:
            sys.exit()
    else:
        pass

    signal.signal(signal.SIGINT, signalHandler)

    os.system("clear")
    print("[+] Creating temporary working environment....")

    os.chdir(Home_Dir)

    if os.path.exists(Temp_Dir) is True:
        os.system("rm -rf "+Temp_Dir)

    if os.path.exists(Temp_Dir) is False:
        os.mkdir(Temp_Dir)

    print "[!] Reports will be saved in: %s" % Temp_Dir


def signalHandler(signal, frame):
    print("[!] Ctrl-C caught, shutting down now");
    Shutdown()

  
def Shutdown():
    if not os.listdir(Temp_Dir):
        os.rmdir(Temp_Dir)
    sys.exit()

def whereis(program):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
            not os.path.isdir(os.path.join(path, program)):
                return os.path.join(path, program)
    return None


def copy2temp(filename, subdir=""):
    if os.path.exists(filename) is True: 
        pass
        if subdir == "" is True:
            shutil.copy2(filename, Temp_Dir)
        else:
            if os.path.exists(Temp_Dir+"/"+subdir) is True:
                subdir = (Temp_Dir+"/"+subdir)
                shutil.copy2(filename, subdir)
            elif os.path.exists(subdir) is True:
                shutil.copy2(filename, subdir)
            else:
                subdir = (Temp_Dir+"/"+subdir)
                os.mkdir(subdir)
                shutil.copy2(filename, subdir)
    else:
        pass

def write2file(filename, text):
    if os.path.exists(filename) is True:
        target = open(filename, "a")
        target.write(text)
        target.close()
    else:
        pass

def writenew(filename, content):
    new = open(filename, "a")
    new.write(content)
    new.close()

def file2file(readfile, writefile):
    if os.path.exists(readfile) is True:
        readfile = open(readfile)
        if os.path.exists(writefile) is True:
            writefile = open(writefile, "a")
            for lines in readfile.readlines():
                writefile.write(lines)
            writefile.close()
            readfile.close()
        else:
            readfile.close()
    else:
        pass
			
def maketemp(subdir):
    moddir = (Temp_Dir+"/"+subdir)
    if os.path.exists(moddir) is False:
        os.mkdir(moddir)
    else:
        pass

def users():
    global userlist
    userlist = []
    passwd = open('/etc/passwd')
    for line in passwd:
        fields = line.split(':')
        uid = int(fields[2])
        if uid > 500 and uid < 32328:
            userlist.append(fields[0])

def combinefiles(newfile, filelist):
    content = ''
    for f in filelist:
        if os.path.exists(f) is True:
            content = content + '\n' + open(f).read()
            open(newfile,'wb').write(content)
        else:
            pass

