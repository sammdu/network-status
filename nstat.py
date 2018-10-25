import csv

from os       import popen
from datetime import datetime
from time     import sleep

ups   = 0
downs = 0

event = '  UP'


# [CONFIGURATION]

log_path   = 'stats.csv'
hosts_path = 'hosts.txt'


# [FUNCTIONS]

def readlistfile(filename):
    """
    Read file as a list, each list item separated by being in a different line;
    Ignore the lines commented out with the "#" symbol as well as empty lines.
    """

    listread = []

    for line in open(filename, mode='r', encoding='utf-8', newline=''):
        
        li = line.strip() # Strip the list items of the '/n' character
        
        # Append the line to the list if it doesn't start with the '#' character and if
        #     it is not empty
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

def countstats(data):
    """
    """
    
    global ups
    global downs
    
    if   data[0] == '  UP':
        ups   = ups   + 1
    
    elif data[0] == 'DOWN':
        downs = downs + 1

def assess():
    """
    """
    
    global event
    
    if  downs == len(hosts):
        event = 'DOWN'
            
    elif downs < len(hosts):
        event = '  UP'
            
    else:
        print('YOU DUMBASS!!!')

def logstat(hostlist, logpath):
    """
    Logs the 'ping()' result of the given hosts in the 'hostlist' input into the 'logfile'
    defined in the 'logpath' input.
    """
    
    # Open the main log file as 'logs', close file automatically as the operation finishes
    with open(logpath, mode='a', encoding='utf-8', newline='') as logs:
        
        # Initialize csv logger to log into 'logs'
        logger = csv.writer(logs, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # For each item in the 'host_list', ping the host, print its status, then log the
        #     status along with the host name in the main log
        while True:
            
            global ups
            global downs
            global event
                
            ups   = 0
            downs = 0
            
            for host in hostlist:
                timestamp = '{0:%a %Y-%m-%d %H:%M:%S}'.format(datetime.now())
                statr = ping(host)
                entry = [statr,timestamp,host]
                
                #print('{}  {}  {}'.format(statr,timestamp,host))
                logger.writerow(entry)
                
                countstats(entry)
            
            print('Ups: {}; Downs: {}.'.format(ups,downs))
            assess()
            print(event)
            sleep(30)


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

# Start logging the ping status of 'hosts' into 'log_path'
logstat(hosts, log_path)

print()
