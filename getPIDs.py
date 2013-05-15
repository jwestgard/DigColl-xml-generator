def extractPIDs(filename):
    import re
    pidlist = []
    with open(filename) as f:
        for line in f.readlines():
            pid = re.search('<pid>(.*?)</pid>', line)
            if pid:
                pidlist.append(pid.group(1))
    return pidlist

target = input('Enter the file from which you would like to extract the PIDs: ')
pids = extractPIDs(target)
print(pids)

