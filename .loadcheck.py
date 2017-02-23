#!/usr/bin/env python
#--------------------------------
#checks the 5min av load on hostnames then displays them sorted and normalized
#This is run by .bashrc entry:
# if [[ $- =~ "i" ]]; then
#      ~/.loadcheck.py
# fi
#
#
#-------------------------------

import sys
import os
import re
from socket import gethostname
from multiprocessing import Pool

#hostnames and number of cores in each
hostnames = ['greywagtail','greypartridge','greyheron','greyplover','greyostrich']
cores = [96,48,96,48,48]
N=len(hostnames)

#terminal color modifiers
green='\033[32m'
yellow='\033[33m'
red='\033[31m'
reset='\033[0m'

def getuptime(hostname):
    #get the uptime string over ssh
    return os.popen("timeout 2 ssh {} \'uptime\'".format(hostname)).read()

def upstring2load(upstring):
    #match the load numbers, 1 5 and 15min averages
    rematch = re.search('load average:\s*(\d+.\d+),\s*(\d+.\d+),\s*(\d+.\d+)',upstring)
    if not rematch:
        #load is inf if ssh uptime didn't respond or gave an error
        return float('inf')
    else:    
        loadall= map(float,rematch.group(1,2,3))
    #use the 5min load
    return loadall[1]

def getloads():
    #get the uptime strings in parallel
    p=Pool(5)
    upstrings=p.map(getuptime,hostnames)
    #match the 5min load and convert to float
    loads = map(upstring2load,upstrings)
    #divide by number of cores and build a {name:load} dict
    normloads = dict(zip(hostnames,[loads[i]/cores[i] for i in range(N)]))
    return normloads

def printloads(loads):
    #print name and load ordered and colored by load
    for host in sorted(loads,key=loads.__getitem__):
        l=loads[host]
        if l<0.75:
            col=green
        elif l<1.25:
            col=yellow
        else:
            col=red
        print col+host+':'+' '*(20-len(host))+str(l)+reset

if __name__=="__main__":
    if gethostname()=='blackcap2.stats.ox.ac.uk':
        printloads(getloads())
    sys.exit()

