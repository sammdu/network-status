#!/usr/bin/python3

import csv

from os       import popen
from datetime import datetime
from time     import sleep


# [CONFIGURATION]

pauseperiod = 60  # How long to pause between tests

log_verbose = 'logs/verbose.csv'  # Where a detailed log of ping results are stored
log_events  = 'logs/events.csv'   # Where logs of significant events are stored
hosts_path  = 'hosts.txt'         # Where a list of hosts to be pinged are stored


# Initialize Global Variables

ups   = 0
downs = 0

refstate = ''

reporttime = ['00:00','08:00','15:00','17:30','19:00']

verbose_entry = []


# [FUNCTIONS]

def readlistfile(filename):
    """
    Read file as a list, each list item separated by being in a different line;
    Ignore the lines commented out with the "#" symbol as well as empty lines.
    """

    listread = []

    for line in open(filename, mode='r', encoding='utf-8', newline=''):
        
        li = line.strip()  # Strip the list items of the '/n' character
        
        # Append the line to the list if it doesn't start with the '#' character and if
        #   it is not empty
        if (not li.startswith("#")) and (not li == ''):
            listread.append(li)
    
    return listread

def ping(host):
    """
    Pings 'host' and return whether host is up or not.
    """

    # Read the 'ping' results into the variable 'response'
    response = popen("ping -W 1 -c 1 " + host).read()
    
    # Return status '  UP' or 'DOWN' based on whether the response contains '1 received'
    if '1 received' in response:
        stat = '  UP'
    else:
        stat = 'DOWN'
    
    return stat

def network_test(hostlist):
    """
    For each item in the 'hostlist', ping the host, then log the status along 
    with the host name and current time in the main log;
    everytime a host is pinged add the results to the 'ups' and 'downs'
    counters, using the 'countstats()' function
    """
    
    global verbose_entry
    verbose_entry = []
    
    for host in hostlist:

        timestamp = '{0:%a %Y-%m-%d %H:%M:%S}'.format(datetime.now())
        statr = ping(host)
        single_entry = [statr,timestamp,host]
        
        verbose_entry.append(single_entry)
        
        countstats(single_entry)

def countstats(data):
    """
    Counts the number of '  UP's and 'DOWN''s received as 'data'
    Needs global variables 'ups' and 'downs' to function properly.
    """
    
    # Access the 'ups' and 'downs' global variables
    global ups
    global downs
    
    # If the input says '  UP', add '1' to the 'ups' counter
    if   data[0] == '  UP':
        ups   = ups   + 1
    
    # If the input says 'DOWN', add '1' to the 'downs' counter
    elif data[0] == 'DOWN':
        downs = downs + 1
    
    # If I receive data that's not been planned for, curse at me
    else:
        print('YOU DUMBASS!!!')

def assess(vlog):
    """
    Assess whether the network is down.
    Requires global variables 'hosts', 'ups', 'downs', and 'event' to function properly.
    As long as some hosts can be reached, keep the 'event' variable as '  UP', otherwise
    make it 'DOWN'.
    """
    
    # Access global variable 'event', and 'verbose_entry'
    global event
    global verbose_entry
    
    # If the times the host is down EQUALS the number of hosts in total (aka when every
    #   host is down), make the 'event' variable 'DOWN'
    if  downs == len(hosts):
        event = 'DOWN'
    
    # As long as some hosts are up, keep the 'event' variable as '  UP'; or overwrite the
    #   'event' variable when the network is restored
    elif downs < len(hosts):
        event = '  UP'
        # Log verbosely when a majority of hosts are down
        if downs > len(hosts)/2-1:
            with open(vlog, mode='a', encoding='utf-8', newline='') as vlogs:
                # Initialize csv logger to log ping results into 'vlogs'
                vlogger = csv.writer(vlogs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for e in verbose_entry:
                    vlogger.writerow(e)
                vlogs.flush()
    
    # If I receive data that's not been planned for, curse at me
    else:
        print('YOU DUMBASS!!!')

def main(hostlist, elog, pause):
    """
    Logs the 'ping()' result of the given hosts in the 'hostlist' input into the log file
    defined in the 'vlog' input.
    Also calls the 'countstats()' and 'assess()' functions to evaluate whether the network
    is down.
    """

    with open(elog, mode='a', encoding='utf-8', newline='') as elogs:
        # Initialize csv logger to log major events into 'elogs'
        elogger = csv.writer(elogs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        while True:
        
            # Access global variables
            global ups
            global downs
            global event
            global refstate
            global reporttime
            
            # Make sure the 'ups' and 'downs' variables are reset every time this loop is
            #   run.
            ups   = 0
            downs = 0 
            
            # Test the network and create a verbose entry
            network_test(hostlist)
            # Create a timestamp upon each test
            timestamp = '{0:%a %Y-%m-%d %H:%M:%S}'.format(datetime.now())
            
            # Evaluate whether the network is down using the 'assess()' function,
            #   supply the verbose log file in order to log conditionally
            assess(log_verbose)
                
            # Writes generic events to the events log if it differed from the previous
            #   state OR if any time set for reporting is reached
            event_entry = [event,ups,downs,timestamp]
            
            if (timestamp[15:20] in reporttime) or (event != refstate):
                elogger.writerow(event_entry)
                refstate = event
            
            # Print out the newtork status (whether is up or down) as well as the number
            #   of hosts that are up or down during that specific iteration of pinging
            print( '{} | Ups: {}; Downs: {}.'.format(event,ups,downs,timestamp) )
            
            # Make sure every time the 'hostlist' is run through, the logs get written
            #   to the files from memory, so it doesn't get lost when an accident
            #   happens
            elogs.flush()
            
            # Wait before the 'hostlist' is run through again
            sleep(pause)


# [MAIN LOGIC]

# Read 'hosts.txt' into the list 'hosts'
hosts = readlistfile(hosts_path)

# Print the list of hosts
print()
print('- LIST OF HOSTS -')
print()
print(str(hosts))
print()
print()

# Start logging the ping status of 'hosts' into 'log_path', and pause 'pauseperiod'
#   seconds between each time a test is run
main(hosts, log_events, pauseperiod)

print()
