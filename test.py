def greeting():             # A dummy function to initiate interaction with the program.
    import datetime
    name = input("Enter your name: ")
    print("\nHello " + name + ", welcome to the XML generator!")
    currentTime = datetime.datetime.utcnow()
    print('It is now ' + str(currentTime))       # prints the current time
    print("\nThis program is designed to take data from a CSV file and populate " +
          "an XML template with that data in order to generate FOXML files for the University" +
          "of Maryland's digital collections repository.")

def getPids(numPids):       # This function retrieves a specified number of PIDs 
    import requests         # from Fedora server.
    url = 'http://fedoradev.lib.umd.edu/fedora/management/getNextPID?numPids='
    url += '{0}&namespace=umd&xml=true'.format(numPids)
    username = input('\nEnter the server username: ')       # prompts user for auth info
    password = input('Enter the server password: ')
    f = requests.get(url, auth=(username, password)).text   # submits request to fedora server
    print("\nRetrieving PIDs from the server...")
    print('\nServer answered with the following XML file:\n')  # print server's response
    print(f)
    fName = input('Enter a name to save the server\'s PID file: ')
    writeFile(fName, '', f)
    return f

def parsePids(pidFile):
    import re
    pidList = []                                            # create list to hold PIDs
    for line in pidFile.splitlines():                       # for each line in the response
        pid = re.search('<pid>(.*?)</pid>', line)           # search for PID and if found
        if pid:
            pidList.append(pid.group(1))                    # append each PID to list
    print('Successfully loaded the following ', end='')
    print('{0} PIDs: '.format(len(pidList)) + str(pidList)) # print result 
    return pidList                                          # return the PID list

# Prompt the user to enter the name of the UMAM or UMDM template or PID file and
# read that file, returning the contents.
def loadFile(fileType):
    sourceFile = input("\nEnter the name of the %s file: " % (fileType))
    if fileType == 'data':
        f = open(sourceFile, 'r').readlines()
    else:
        f = open(sourceFile, 'r').read()
    return(f)

# Creates a file containing the contents of the "content" string, named [fileName]_[fileType].xml,
# files are saved in a sub-directory called "output".
def writeFile(fileNumber, fileType, content):
    filePath = "output/" + fileNumber + '_' + fileType + ".xml"
    f = open(filePath, mode='w')
    f.write(content)
    f.close()

# When passed a string in the format 'HH:MM:SS', returns the decimal value in minutes,
# rounded to two decimal places.
def convertTime(inputTime):
    if inputTime == "":                 # if the input string is empty, return the same string
        return inputTime
    hrsMinSec = inputTime.split(':')    # otherwise, split the string at the colon
    minutes = int(hrsMinSec[0]) * 60    # multiply the first value by 60
    minutes += int(hrsMinSec[1])        # add the second value
    minutes += int(hrsMinSec[2]) / 60   # add the third value divided by 60
    print('\nTime Conversion: ' + str(hrsMinSec) + ' = ' + str(round(minutes, 2))) # print result
    return round(minutes, 2)            # return the resulting decimal rounded to two places

def createUMAM(data, template):     # Performs series of find and replace operations to
    import datetime                 # generate UMDM file from the template.
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    outputfile = template.replace('!!!Digitized by!!!', data['Digitized by DCMR'])
    outputfile = outputfile.replace('!!!TITLE!!!', data['Title'])
    outputfile = outputfile.replace('!!!Digitization Notes!!!', data['Digitization Notes'])
    outputfile = outputfile.replace('!!!FILE NAME!!!', data['File Name'])
    outputfile = outputfile.replace('!!!Mono/Stereo!!!', data['Mono/Stereo'])
    outputfile = outputfile.replace('!!!Sharestream!!!', data['SharestreamURLS'])
    convertedRunTime = str(convertTime(data['TotalRunTimeDerivatives']))
    outputfile = outputfile.replace('!!!TotalRunTimeDerivatives!!!', convertedRunTime)
    outputfile = outputfile.replace('!!!Track Format!!!', data['Track Format'])
    outputfile = outputfile.replace('!!!YYYY-MM-DD!!!', timeStamp)
    return outputfile

def createUMDM(data, template):     # Performs series of find and replace operations to
    import datetime                 # generate UMDM file from the template.
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    outputfile = template.replace('!!!Title!!!', data['Title'])
    outputfile = outputfile.replace('!!!Alternate Title!!!', data['Alternate Title'])
    outputfile = outputfile.replace('!!!Contributor!!!', data['Contributor'])
    outputfile = outputfile.replace('!!!Item Control Number!!!', data['Item Control Number'])
    outputfile = outputfile.replace('!!!Description/Summary!!!', data['Description/Summary'])
    outputfile = outputfile.replace('!!!Copyright Holder!!!', data['Copyright Holder'])
    outputfile = outputfile.replace('!!!Continent!!!', data['Continent'])
    outputfile = outputfile.replace('!!!Country!!!', data['Country'])
    outputfile = outputfile.replace('!!!Region/State!!!', data['Region/State'])
    outputfile = outputfile.replace('!!!Settlement/City!!!', data['Settlement/City'])
    outputfile = outputfile.replace('!!!DateAnalogCreated!!!', data['DateAnalogCreated'])
    outputfile = outputfile.replace('!!!Repository!!!', data['Repository'])
    if data['SizeReel'].endswith('"'):
        data['SizeReel'] = data['SizeReel'][0:-1]
    outputfile = outputfile.replace('!!!Size Reel!!!', data['SizeReel'])
    convertedRunTime = str(convertTime(data['TotalRunTimeDerivatives']))
    outputfile = outputfile.replace('!!!TotalRunTimeDerivativesMinutes!!!', convertedRunTime)
    outputfile = outputfile.replace('!!!Type of Material!!!', data['TypeofMaterial'])
    outputfile = outputfile.replace('!!!Collection!!!', data['Collection'])
    outputfile = outputfile.replace('!!!Box Number!!!', data['Box Number'])
    outputfile = outputfile.replace('!!!Accession Number!!!', data['Accession Number'])
    outputfile = outputfile.replace('!!!YYYY-MM-DD!!!', timeStamp)
    return outputfile

def createMETS():
    metsFile = open('mets.xml', 'r').read()
    return(metsFile)
 
def main():
    import csv
    greeting()
    dataFile = loadFile('data')
    dataLength = len(dataFile)
    print('The datafile you specified has {0} rows.'.format(dataLength))
    print('Load PIDs from a file or request them from the server?')
    pidMethod = input('Enter F (file) or S (server): ')
    pidList = []
    if pidMethod == 'F':
        pidFileName = input('Enter the name of the PID file: ')
        pidFile = open(pidFileName, 'r').read()
    elif pidMethod == 'S':
        pidFile = getPids(dataLength)   # Requests as many PIDs as lines of data.
    else:
        print('Invalid response.')
        quit()
    pidList = parsePids(pidFile)    # Parses PIDs from the PID file (either local or from the server)
    if len(pidList) < dataLength:
        print('Not enough PIDs for that dataset. Exiting program.')
        quit()
    umam = loadFile('UMAM')         # Loads UMAM template.
    print("\n UMAM:\n" + umam)      # Prints UMAM.
    print('*' * 30)                 # Prints a divider.
    umdm = loadFile('UMDM')         # Loads UMDM template.
    print("\n UMDM:\n" + umdm)      # Prints UMDM.
    print('*' * 30)                 # Prints a divider.
    myData = csv.DictReader(dataFile)
    i = 0
    mets = ""
    objectParts = 0                 # a counter for number of UMAM parts
    for x in myData:
        x['PID'] = pidList[i]       # Attaches the PID to the dataset.
        i += 1
        if x['XML_Type'] == 'UMDM':
            if mets != "":
                print('Creating UMDM for object with {0} parts!\n'.format(objectParts))
                objectParts = 0    
                myFile = createUMDM(tempData, umdm)
                myFile = myFile.replace('!!!INSERT_METS_HERE!!!', mets)
                print('Writing UMDM...')
                writeFile(tempData['Item Control Number'].strip(), 'umdm', myFile)
                filesWritten += 1
            tempData = x
            mets = createMETS()
        elif x['XML_Type'] == 'UMAM':             # checks whether it's a UMAM row
            objectParts += 1
            outputFile = createUMAM(x, umam)      # if yes, calls function to populate UMAM template
            print('Writing UMAM...')
            writeFile(x['File Name'].strip(), 'umam', outputFile)   # writes output to file
            filesWritten += 1
    print('\n' + ('*' * 30))        # Print a divider and summarize output.
    print('\n{0} files written. Thanks for '.format(filesWritten), end='')
    print('using the XML generator!\n\n')
    
def test():
    metadata = readData()
    for x in metadata:
        print(x)
    
main()
