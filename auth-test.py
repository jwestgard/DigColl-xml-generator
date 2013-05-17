import requests, re
numPids = input('Enter the number of PIDs you need: ')
url = 'http://fedoradev.lib.umd.edu/fedora/management/getNextPID?numPids={0}&namespace=umd&xml=true'.format(numPids)
username = input('\nEnter the server username: ')
password = input('\nEnter the server password: ')
retrievePids = requests.get(url, auth=(username, password))
print("\nRetrieving PIDs from the server...")
data = retrievePids.text
pidList = []
print('\nServer answered with the following XML file:\n')
print(data)
for line in data.splitlines():
    pid = re.search('<pid>(.*?)</pid>', line)
    if pid:
        pidList.append(pid.group(1))
print("This yielded the following list of PIDs: " + str(pidList))