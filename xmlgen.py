def greeting():             # A dummy function to initiate interaction with the program.
    import datetime
    name = input("\nEnter your name: ")
    print("\nHello " + name + ", welcome to the XML generator!")
    currentTime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print('It is now ' + str(currentTime))       # prints the current time
    print("\nThis program is designed to take data from a CSV file,")
    print("and use that data to generate FOXML files for the")
    print("University of Maryland's digital collections repository.")

def getPids(dataLength):
    pidList = []
    pidSource = input('Enter F (file) or S (server): ')
    while (pidSource not in ('F','S')):
        print("ERROR: you must enter either 'F' to load PIDs from a file, or 'S' to request them from the server!")
        pidSource = input('Please try again: ')
    if pidSource == 'F':
        pidFileName = input('Enter the name of the PID file: ')
        pidFile = open(pidFileName, 'r').read()
    elif pidSource == 'S':
        pidFile = requestPids(dataLength)   # Requests as many PIDs as lines of data.
    return pidFile

def requestPids(numPids):       # This function retrieves a specified number of PIDs 
    import requests             # from Fedora server.
    url = 'http://fedora.lib.umd.edu/fedora/management/getNextPID?numPids='
    url += '{0}&namespace=umd&xml=true'.format(numPids)
    username = input('\nEnter the server username: ')          # prompts user for auth info
    password = input('Enter the server password: ')
    f = requests.get(url, auth=(username, password)).text      # submits request to fedora server
    print("\nRetrieving PIDs from the server...")
    print('\nServer answered with the following XML file:\n')  # print server's response
    print(f)
    fName = input('Enter a name under which to save the server\'s PID file: ')
    writeFile(fName, f, '.xml')
    return f

def parsePids(pidFile):
    import re
    pidList = []                                            # create list to hold PIDs
    for line in pidFile.splitlines():                       # for each line in the response
        pid = re.search('<pid>(.*?)</pid>', line)           # search for PID and if found
        if pid:
            pidList.append(pid.group(1))                    # append each PID to list
    resultLength = str(len(pidList))
    print('\nSuccessfully loaded the following {0} PIDs: '.format(resultLength))
    print(pidList)
    return pidList

def generateDateTag(inputDate, inputAttribute):
    dateTagList = []
    myDate = parseDate(inputDate, inputAttribute)
    if myDate['Type'] == 'range':
        elements = myDate['Value'].split('-')   # split the date into its parts
        if len(elements) == 2:                  # if there are two parts, use those as begin/end years
            beginDate = elements[0]
            endDate = elements[1]
        elif len(elements) == 6:                # if there are 6 parts, use index 0 and 4 as begin/end years
            beginDate = elements[0]             # i.e. we assume YYYY-MM-DD-YYYY-MM-DD format for exact date ranges
            endDate = elements[4]
        myTag = '<date certainty="{0}" era="ad" from="{1}" to="{2}">{3}</date>'.format(myDate['Certainty'], beginDate, endDate, myDate['Value'])
        dateTagList.append(myTag)
    elif myDate['Number'] == 'multiple':
        for i in myDate['Value']:
            myTag = '<date certainty="{0}" era="ad">{1}</date>'.format(myDate['Certainty'], i.strip())
            dateTagList.append(myTag)
    else:
        myTag = '<date certainty="{0}" era="ad">{1}</date>'.format(myDate['Certainty'], myDate['Value'])
        dateTagList.append(myTag)
    return '\n'.join(dateTagList)

def parseDate(inputDate, inputAttribute):
    myDate = {}
    if 'multiple' in inputAttribute:            # multiple or single date?
        myDate['Number'] = 'multiple'
    else:
        myDate['Number'] = 'single'
    if 'circa' in inputAttribute:               # exact or circa?
        myDate['Certainty'] = 'circa'
    else:
        myDate['Certainty'] = 'exact'
    if 'range' in inputAttribute:               # range or point?  
        myDate['Type'] = 'range'
    else:
        myDate['Type'] = 'date'
    if myDate['Number'] == 'multiple':          # set value --> split if multiple, otherwise single value
        myDate['Value'] = inputDate.split(';')
    else:
        myDate['Value'] = inputDate
    return myDate

# Prompt the user to enter the name of the UMAM or UMDM template or PID file and
# read that file, returning the contents.
def loadFile(fileType):
    sourceFile = input("\nEnter the name of the %s file: " % (fileType))
    if fileType == 'data':
        f = open(sourceFile, 'r').readlines()
    else:
        f = open(sourceFile, 'r').read()
    return(f, sourceFile)

# Creates a file containing the contents of the "content" string, named umd_[PID].xml,
# with all files saved in dir 'output', and XML files in the sub-dir 'foxml'.
def writeFile(fileStem, content, extension):
    if extension == '.xml':
        filePath = 'output/foxml/' + fileStem + extension
    else:
        filePath = 'output/' + fileStem + extension
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
    print('Time Conversion: ' + str(hrsMinSec) + ' = ' + str(round(minutes, 2))) # print result
    return round(minutes, 2)            # return the resulting decimal rounded to two places

def createUMAM(data, template):     # Performs series of find and replace operations to
    import datetime                 # generate UMDM file from the template.
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    outputfile = template.replace('!!!PID!!!', data['PID'])
    outputfile = outputfile.replace('!!!Title!!!', data['Title'])
    outputfile = outputfile.replace('!!!DigitizationNotes!!!', data['Digitization Notes'])
    outputfile = outputfile.replace('!!!FileName!!!', data['File Name'])
    outputfile = outputfile.replace('!!!Mono/Stereo!!!', data['Mono/Stereo'])
    outputfile = outputfile.replace('!!!Sharestream!!!', data['ShareStreamURLs'])
    convertedRunTime = convertTime(data['TotalRunTimeDerivatives'])
    outputfile = outputfile.replace('!!!TotalRunTimeDerivatives!!!', str(convertedRunTime))
    outputfile = outputfile.replace('!!!TrackFormat!!!', data['Track Format'])
    outputfile = outputfile.replace('!!!TimeStamp!!!', timeStamp)
    outputfile = outputfile.replace('!!!DateDigitized!!!', data['DateDigitized'])
    outputfile = outputfile.replace('!!!DigitizedByPers!!!', data['DigitizedByPers'])
    return outputfile, convertedRunTime

def createUMDM(data, template, summedRunTime):      # Performs series of find and replace operations to
    import datetime                                 # generate UMDM file from the template.
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    outputfile = template.replace('!!!PID!!!', data['PID'])
    outputfile = outputfile.replace('!!!Title!!!', data['Title'])
    outputfile = outputfile.replace('!!!AlternateTitle!!!', data['Alternate Title'])
    outputfile = outputfile.replace('!!!Contributor!!!', data['Contributor'])
    outputfile = outputfile.replace('!!!ItemControlNumber!!!', data['Item Control Number'])
    outputfile = outputfile.replace('!!!Description/Summary!!!', data['Description/Summary'])
    outputfile = outputfile.replace('!!!CopyrightHolder!!!', data['Copyright Holder'])
    outputfile = outputfile.replace('!!!Continent!!!', data['Continent'])
    outputfile = outputfile.replace('!!!Country!!!', data['Country'])
    outputfile = outputfile.replace('!!!Region/State!!!', data['Region/State'])
    outputfile = outputfile.replace('!!!Settlement/City!!!', data['Settlement/City'])
    outputfile = outputfile.replace('!!!DateAnalogCreated!!!', data['DateAnalogCreated'])
    dateTagString = generateDateTag(data['DateAnalogCreated'], data['CreatedDateCertainty'])
    outputfile = outputfile.replace('!!!InsertDateHere!!!', dateTagString)
    outputfile = outputfile.replace('!!!Repository!!!', data['Repository'])
    if data['SizeReel'].endswith('"'):
        data['SizeReel'] = data['SizeReel'][0:-1]
    outputfile = outputfile.replace('!!!SizeReel!!!', data['SizeReel'])
    runTimeMasters = str(round(summedRunTime, 2))
    outputfile = outputfile.replace('!!!TotalRunTimeMasters!!!', runTimeMasters)
    outputfile = outputfile.replace('!!!TypeOfMaterial!!!', data['TypeofMaterial'])
    outputfile = outputfile.replace('!!!Collection!!!', data['Collection'])
    outputfile = outputfile.replace('!!!BoxNumber!!!', data['Box Number'])
    outputfile = outputfile.replace('!!!AccessionNumber!!!', data['Accession Number'])
    outputfile = outputfile.replace('!!!TimeStamp!!!', timeStamp)
    return outputfile

def createMets():
    metsFile = open('mets.xml', 'r').read()
    return(metsFile)
 
def updateMets(partNumber, mets, fileName, pid):
    id = str(partNumber + 2)   # first part is file 3 because the first two files are the collection PIDs for AlbUM and WMUC
    metsSnipA = open('metsA.xml', 'r').read() + '!!!Anchor-A!!!'
    metsSnipB = open('metsB.xml', 'r').read() + '!!!Anchor-B!!!'
    metsSnipC = open('metsC.xml', 'r').read() + '!!!Anchor-C!!!'
    mets = mets.replace('!!!Anchor-A!!!', metsSnipA)
    mets = mets.replace('!!!Anchor-B!!!', metsSnipB)
    mets = mets.replace('!!!Anchor-C!!!', metsSnipC)
    mets = mets.replace('!!!FileName!!!', fileName)
    mets = mets.replace('!!!ID!!!', id)
    mets = mets.replace('!!!PID!!!', pid)
    mets = mets.replace('!!!Order!!!', str(partNumber))
    return mets

def stripAnchors(target):
    import re
    f = re.sub(r"\n\s*!!!Anchor-[ABC]!!!", "", target)
    return f

def main():
    import csv
    import datetime
    
    mets = ""			# empty string for compiling METS record
    umdmList = []		# empty list for compiling list of UMDM pids
    outputFiles = []	        # empty list for compiling list of all pids written
    summaryList = []		# empty list for compiling list of PIDs and Object IDs
    objectGroups = 0            # counter for UMDM plus UMAM(s) as a group
    objectParts = 0             # counter for the number of UMAM parts for each UMDM
    filesWritten = 0            # counter for file outputs
    summedRunTime = 0
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    greeting()
    
    dataFile, fileName = loadFile('data')
    dataFileSize = len(dataFile)
    dataLength = dataFileSize - 1
    print('The datafile you specified has {0} rows.'.format(dataFileSize))
    print('Assuming there is a header row, you need {0} PIDs.'.format(dataLength))
    print('Load {0} PIDs from a file or request them from the server?'.format(dataLength))
    pidFile = getPids(dataLength)
    pidList = parsePids(pidFile)    # Parses PIDs from the PID file (either local or from the server)
    if len(pidList) < dataLength:
        print('Not enough PIDs for your dataset!')
        print('Please reserve additional PIDs from the server and try again.')
        print('Exiting program.')
        quit()
        
    umam, umamName = loadFile('UMAM')         			# Loads UMAM template.
    print("\n UMAM:\n" + umam)      				# Prints UMAM.
    print('*' * 30)                 				# Prints a divider.
    
    umdm, umdmName = loadFile('UMDM')        			# Loads UMDM template.
    print("\n UMDM:\n" + umdm)     				# Prints UMDM.
    print('*' * 30)                 				# Prints a divider.
    
    myData = csv.DictReader(dataFile)
    print('Data successfully read.')
    
    i = 0
    for x in myData:
        x['PID'] = pidList[i]            			# Attaches a PID to the dataset.
        outputFiles.append(x['PID'])     			# Append PID to list of output files
        i += 1
        
        if x['XML Type'] == 'UMDM':
            link = '"{0}","{1}","{2}","http://digital.lib.umd.edu/video?pid={2}"'.format(x['Item Control Number'], x['XML Type'], x['PID'])
            summaryList.append(link)                                # Append Control Number, Type, and PID to summary list
            if mets != "":
                print('Creating UMDM for object with {0} parts...'.format(objectParts), end=" ")
                objectParts = 0                                         # reset parts counter
                myFile = createUMDM(tempData, umdm, summedRunTime)      # Create the UMDM
                myFile = myFile.replace('!!!INSERT_METS_HERE!!!', mets) # Insert the METS
                myFile = myFile.replace('!!!TimeStamp!!!', timeStamp)   # update timestamp in the METS
                myFile = stripAnchors(myFile)                           # Strip out anchor points
                print('\nTotal runtime of all parts = {0}.'.format(str(summedRunTime)))
                summedRunTime = 0
                fileStem = tempData['PID'].replace(':', '_').strip()
                print('UMDM = {0}'.format(fileStem))
                writeFile(fileStem, myFile, '.xml')                     # Write the file
                umdmList.append(tempData['PID'])                        # Append UMDM PID to UMDM pidlist
                filesWritten += 1
            objectGroups += 1
            print('\nFILE GROUP {0}: '.format(objectGroups))
            tempData = x                            # Store this dataset for later, after UMAMs are generated
            mets = createMets()                     # Prepare the METS for addition of UMAM info
            
        elif x['XML Type'] == 'UMAM':   	    # Checks whether it's a UMAM row
            link = '"{0}","{1}","{2}"'.format(x['Item Control Number'], x['XML Type'], x['PID'])
            summaryList.append(link)                                # Append Control Number, Type, and PID to summary list
            objectParts += 1
            myFile, convertedRunTime = createUMAM(x, umam)          # If yes, calls function to populate UMAM template
            summedRunTime += convertedRunTime
            print('Writing UMAM...', end=' ')
            fileStem = x['PID'].replace(':', '_').strip()
            print('Part {0}: UMAM = {1}'.format(objectParts, fileStem))
            writeFile(fileStem, myFile, '.xml')                     # writes output to file
            filesWritten += 1
            mets = updateMets(objectParts, mets, x['File Name'], x['PID'])
            
    print('Creating UMDM for object with {0} parts...'.format(objectParts), end=' ')   
    myFile = createUMDM(tempData, umdm, summedRunTime)              # Create the UMDM for the final object
    myFile = myFile.replace('!!!INSERT_METS_HERE!!!', mets)         # Insert the METS in the UMDM
    myFile = myFile.replace('!!!TimeStamp!!!', timeStamp)           # update timestamp in the METS
    myFile = stripAnchors(myFile)                                   # Strip out anchor points
    print('\nTotal runtime of all parts = {0}.'.format(str(round(summedRunTime, 2))))
    fileStem = tempData['PID'].replace(':', '_').strip()            # create pid stem for use in filename
    print('UMDM = {0}'.format(fileStem))
    writeFile(fileStem, myFile, '.xml')                             # Write the file
    umdmList.append(tempData['PID'])                                # Append UMDM PID to list of UMDM files
    
    filesWritten += 1
    
    print('\nWriting pidlist file as pids.txt...')
    f = '\n'.join(outputFiles)
    writeFile('pids', f, '.txt')
    filesWritten += 1
    
    print('Writing summary file as links.txt...')
    l = '\n'.join(summaryList)
    writeFile('links', l, '.txt')
    filesWritten += 1
    
    print('Writing list of UMDM files as UMDMpids.txt...')
    d = '\n'.join(umdmList)
    writeFile('UMDMpids', d, '.txt')
    filesWritten += 1
    
    print('\n' + ('*' * 30))                # Print a divider and summarize output.
    print('\n{0} files written: {1} FOXML files in {2}'.format(filesWritten, filesWritten - 3, objectGroups), end=' ')
    print('groups, plus the summary list of pids, list of UMDM pids, and the links file.')
    print('Thanks for using the XML generator!\n\n')
    
main()

# inputDate = input('enter date: ')
# inputType = input('enter type: ')
# myTag = generateDateTag(inputDate, inputType)
# print(myTag)