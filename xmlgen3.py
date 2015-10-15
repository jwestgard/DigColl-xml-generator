#!usr/bin/env python3

############################################################################
#                                                                          #
#                              XMLGEN.PY:                                  #
#                 A script to generate FOXML files for                     #
#               Digital Collections Audio & Video at UMD                   #
#                      Version 3 -- September 2014                         #
#                                                                          #
############################################################################
#                                                                          #
# Recommended command to run this program:                                 #
#                                                                          #
#     python3 xmlgen3.py 2>&1 | tee xmlgen.log                             #
#                                                                          #
# (Using this command prints all input and output to screen and also saves #
# it as a log file).                                                       #
#                                                                          #
# The program assumes that CSV and XML template files are located in the   #
# same directory as the script itself. It also assumes there will be a     #
# subdirectory called output containing another directory called foxml.    #
#                                                                          #
############################################################################


# Import needed modules
import csv
import datetime
import os
import re
import requests
from lxml import etree as etree


# Initiates interaction with the program and records the time and user.
def greeting():
    name = input("\nEnter your name: ")
    print("\nHello " + name + ", welcome to the XML generator!")
    currentTime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print('It is now ' + str(currentTime))
    print("\nThis program is designed to take data from a CSV file,")
    print("and use that data to generate FOXML files for the")
    print("University of Maryland's digital collections repository.")


# Asks the user whether the batch is audio or video objects.
def getMediaType():
    mediaType = input('\nIs this a batch of [A]udio or [V]ideo? ')
    while mediaType not in ('A','V'):
        mediaType = input('Please enter A or V: ')
    if mediaType == "A":
        return "audio"
    elif mediaType == "V":
        return "video"


def getCollection():
    coll = input("\nChoose a collection -- [D]igital Collections or [F]ilms@UM: ")
    while coll not in ('D','F'):
        coll = input('Please enter D or F: ')
    if coll == "D":
        return "umd:3392"
    elif coll == "F":
        return "umd:1158"


# Analyzes the type of datafile and calculates the number of PIDs needed.
def analyzeDataFile(dataFile):
    dataFileSize = len(dataFile)
    print('\nDoes your datafile contain single or multiple rows for each object?')
    dataFileArrangement = input('Please enter S or M: ')
    while dataFileArrangement not in ('S','M'):
        dataFileArrangement = input('Please enter either S for sigle-rowed data, or M for multi-rowed data: ')
    print('\nThe datafile you specified has {0} rows.'.format(dataFileSize))
    if dataFileArrangement == 'S':
        print('Since you have single-rowed objects, you need two PIDs for each row.')
        dataLength = (dataFileSize - 1) * 2
    elif dataFileArrangement == 'M':
        print('Since you have multi-rowed objects, you need one PID for each row.')
        dataLength = dataFileSize - 1
    print('Assuming there is a header row in your datafile, you need {0} PIDs.'.format(dataLength))
    print('Load {0} PIDs from a file or request them from the server?'.format(dataLength))
    return dataLength, dataFileArrangement


# Reads the length of the CSV datafile and guides user in requesting
# necessary number of PIDs from either the stage (for testing) or production server
def getPids(dataLength):
    pidList = []
    pidSource = input('Enter F (file) or S (server): ')
    while (pidSource not in ('F','S')):
        print("ERROR: you must enter either 'F' to load PIDs from a file, " +
              "or 'S' to request them from the server!")
        pidSource = input('Please try again: ')
    if pidSource == 'F':
        pidFileName = input('Enter the name of the PID file: ')
        pidFile = open(pidFileName, 'r').read()
    elif pidSource == 'S':
        pidFile = requestPids(dataLength)
    return pidFile


# Handles the request for PIDs from the server, 
# requesting a specified number of PIDs and saving the resulting XML file.
def requestPids(numPids):                   
    serverChoice = input('Enter S to get PIDs on fedoraStage, P to get PIDs on Production: ')
    while (serverChoice not in ('S', 'P')): # Choose the production or stage server
        serverChoice = input('Error: You must enter S or P: ')
    if serverChoice == 'S':
        url = 'http://fedorastage.lib.umd.edu/fedora/management/getNextPID?numPids='
    elif serverChoice == 'P':
        url = 'http://fedora.lib.umd.edu/fedora/management/getNextPID?numPids='
    url += '{0}&namespace=umd&xml=true'.format(numPids)
    username = input('\nEnter the server username: ')          # prompts user for auth info
    password = input('Enter the server password: ')
    f = requests.get(url, auth=(username, password)).text      # submits request to fedora server
    print("\nRetrieving PIDs from the server...")
    print('\nServer answered with the following XML file:\n')  # print server's response
    print(f)
    print('Saving the PID file as output/pids.xml: ')
    writeFile("pids", f, '.xml')
    return f


# Takes the XML-based PID file provided by Fedora, and parses it to retrieve just the pids,
# loading them into a Python list and returning it.
def parsePids(pidFile):
    pidList = []                                            # create list to hold PIDs
    for line in pidFile.splitlines():                       # for each line in the response
        pid = re.search('<pid>(.*?)</pid>', line)           # search for PID and if found
        if pid:
            pidList.append(pid.group(1))                    # append each PID to list
    resultLength = str(len(pidList))
    print('\nSuccessfully loaded the following {0} PIDs: '.format(resultLength))
    print(pidList)
    return pidList


# Sets the rights scheme to govern access to this batch, based on user input.
def getRightsScheme():
    results = {}
    print("\n[P]ublic = Accessible from anywhere, discoverable via search.")
    print("[R]estricted = Accessible on campus only, not discoverable.")
    print("[C]ampus Only = Accessible on campus only, discoverable via search.")
    print("[M]ediated = Accessible from anywhere, not discoverable.")
    schemeSelection = input("\nEnter the rights scheme to govern access to this batch [P, R, C, or M]: ")
    while schemeSelection not in ["P", "R", "C", "M"]:
        schemeSelection = input("You must enter P, R, C, or M!")
    if schemeSelection == "P":
        results['amInfoStatus'] =           "Complete"
        results['doInfoStatus'] =           "Complete"
        results['adminRightsAccess'] =      "UMDpublic"
    elif schemeSelection == "R":
        results['amInfoStatus'] =           "Complete"
        results['doInfoStatus'] =           "Private"
        results['adminRightsAccess'] =      "UMDfilms00001"
    elif schemeSelection == "C":
        results['amInfoStatus'] =           "Complete"
        results['doInfoStatus'] =           "Complete"
        results['adminRightsAccess'] =      "UMDfilms00001"
    elif schemeSelection == "M":
        results['amInfoStatus'] =           "Complete"
        results['doInfoStatus'] =           "Private"
        results['adminRightsAccess'] =      "UMDfilms00001"
    else:
        print("Sorry, something went wrong with the rights selection!")
        exit
    return results


# Generates the mediaType XML tag, wrapping it around the form XML tag      
def generateMediaTypeTag(mediaType, formType, form):
    return '<mediaType type="{0}"><form type="{1}">{2}</form></mediaType>'.format(mediaType, formType, form)


# Build a block of the various agents elements as a string
def generateAgentsString(**kwargs):
    result = []
    for type, dataCols in kwargs.items():
        if dataCols:
            agentsList = generateAgentElements(dataCols[0], dataCols[1])
            for agent in agentsList:
                result.append('<agent type="{0}">{1}</agent>'.format(type, agent))
    return "\n".join(result)


# Generate list of agents from the data and type columns
def generateAgentElements(agentColumn, agentTypeColumn):
    agents = agentColumn.split(";")
    agentTypes = agentTypeColumn.split(";")
    if len(agents) != len(agentTypes):
        print('Error! Bad agent data in: "{0}" and "{1}"'.format(agentcolumn, agentTypeColumn))
    else:
        result = []
        agentData = zip(agents, agentTypes)
        for a, t in agentData:
            if t == "corpName":
                result.append("<corpName>{0}</corpName>".format(a))
            elif t == "persName":
                result.append("<persName>{0}</persName>".format(a))
        return result


# Generates the specific XML tags based on dating information stored in the myDate dictionary
# previously returned by the parseDate function.
def generateDateTag(inputDate, inputAttribute, centuryData):
    dateTagList = generateCenturyTags(centuryData)  # start result list with century tag(s)
    centuryList = []
    myDate = parseDate(inputDate, inputAttribute)
    if myDate['Type'] == 'range':
        print(myDate['Value'])
        elements = myDate['Value'].split('-')   # split the date into its parts
        if len(elements) == 2:                  # if there are two parts, use those as begin/end years
            beginDate = elements[0]
            endDate = elements[1]
        elif len(elements) == 6:    # if there are 6 parts, use index 0 and 4 as begin/end years
            beginDate = elements[0] # i.e. we assume YYYY-MM-DD-YYYY-MM-DD format for exact date ranges
            endDate = elements[4]
        myTag = '<date certainty="{0}" era="ad" from="{1}" to="{2}">{3}</date>'.format(myDate['Certainty'],
                                                                                       beginDate, endDate,
                                                                                       myDate['Value'])
        dateTagList.append(myTag)
    elif myDate['Number'] == 'multiple':
        for i in myDate['Value']:
            myTag = '<date certainty="{0}" era="ad">{1}</date>'.format(myDate['Certainty'], i.strip())
            dateTagList.append(myTag)
    else:
        myTag = '<date certainty="{0}" era="ad">{1}</date>'.format(myDate['Certainty'], myDate['Value'])
        dateTagList.append(myTag)
    return '\n'.join(dateTagList)


# This function parses the date attributes stored in a particular column of the input data.
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


# generate the sorted century tag(s) from the input data in the century column
def generateCenturyTags(inputCentury):
    result = []
    myList = sorted(inputCentury.split(';'))
    for i in myList:
        result.append('<century certainty="exact" era="ad">{0}</century>'.format(i.strip()))
    return result


# generate browse terms from the subject field of the data
def generateBrowseTerms(inputSubjects):
    result = []
    myList = inputSubjects.split(';')
    for i in myList:
        result.append('<subject type="browse">{0}</subject>'.format(i.strip()))
    return '\n'.join(result)


# generate subject terms from the three subject columns of the data
def generateTopicalSubjects(**kwargs):
    result = []
    for key, value in kwargs.items():
        if value[0]:
            for subj in value[0].split(';'):
                scheme = value[1].strip()
                if key == 'pers':
                    element = '<persName>{0}</persName>'.format(subj.strip())
                    type = 'topical'
                elif key == 'corp':
                    element = '<corpName>{0}</corpName>'.format(subj.strip())
                    type = 'topical'
                elif key == 'top':
                    element = subj.strip()
                    type = 'topical'
                elif key == 'geog':
                    element = '<geogName>{0}</geogName>'.format(subj.strip())
                    type = 'geographical'
                if scheme != '':
                    subj_elem = '<subject scheme="{0}" type="{1}">{2}</subject>'.format(scheme, type, element)
                else:
                    subj_elem = '<subject type="{0}">{1}</subject>'.format(type, element)
            result.append(subj_elem)
    return '\n'.join(result)
 

# generate block os XML relating to archival location
def generateArchivalLocation(collection, **kwargs):
    result = ['<title type="main">{0}</title>'.format(collection)]
    for key, value in kwargs.items():
        if value != '':
            result.append('<bibScope type="{0}">{1}</bibScope>'.format(key, value))
    return '\n'.join(result)


# Prompts the user to enter the name of the UMAM or UMDM template or PID file and
# read that file, returning the contents.
def loadFile(fileType):
    if fileType in ['umam','umdm']:
        sourceFile = "templates/{}.xml".format(fileType)
        f = open(sourceFile, 'r').read()
    else:
        sourceFile = input("\nEnter the name of the {0} file: ".format(fileType))
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
    # filter out blank lines and lines containing only spaces from XML
    cleaned = os.linesep.join([line for line in content.splitlines() if line.strip()])
    f.write(cleaned)
    f.close()


# Select time format for runtime conversions (either minutes as decimal or ISO)
def timeFormatSelection():
    choice = input('Enter the output time format ([I] for ISO, or [M] for minutes): ')
    while choice not in ['I', 'i', 'M', 'm']:
        choice = input('You must enter either H or M!')
    if choice == "M" or choice == "m":
        # When passed a string in the format 'HH:MM:SS', returns the decimal value in minutes,
        # rounded to two decimal places.
        timeUnits = "minutes"
        nullTimeCounter = 0
        def convertTime(inputTime):
            hrsMinSec = inputTime.split(':')    # otherwise, split the string at the colon
            minutes = int(hrsMinSec[0]) * 60    # multiply the first value by 60
            minutes += int(hrsMinSec[1])        # add the second value
            minutes += int(hrsMinSec[2]) / 60   # add the third value divided by 60
            return round(minutes, 2)  # return the resulting decimal rounded to two places
    elif choice == "I" or choice == "i":
        # Convert the input time to a timedelta and return it
        timeUnits = "hh:mm:ss"
        nullTimeCounter = datetime.timedelta(0)
        def convertTime(inputTime):
            hh, mm, ss = map(int, inputTime.split(":"))
            result = datetime.timedelta(hours=hh, minutes=mm, seconds=ss)
            return result
    else:
        print("Something went wrong with the time format selection!")
        exit
    return nullTimeCounter, convertTime, timeUnits


def generateTechnicalMetaString(data, mediaType, convertTime):
    # create root element and tree object
    root = etree.Element('technical')
    tech_meta = etree.ElementTree(root)
    # technical/format/fileName
    etree.SubElement(root, 'fileName').text = data['FileName']
    # create format element to hold mimeType and compression subelements
    format = etree.SubElement(root, 'format')
    # create media {audio,video} and duration subelement
    media = etree.SubElement(root, mediaType)
    etree.SubElement(media, 'duration').text = str(convertTime(data['DurationDerivatives']))
    if mediaType == 'audio':
        etree.SubElement(format, 'mimeType').text = "audio/mpeg"
        etree.SubElement(format, 'compression').text = "lossy"
        etree.SubElement(media, 'channels').text = data['TrackFormat']
        # create sound container element specific to audio objects
        sound = etree.SubElement(media, 'audioTrack')
    elif mediaType == 'video':
        etree.SubElement(format, 'mimeType').text = "video/x-m4v"
        etree.SubElement(format, 'compression').text = "lossy"
        # create sound container element specific to video objects
        sound = etree.SubElement(media, 'videoSound')
        # create top-level video elements
        if 'Color' in data and data['Color']:
            etree.SubElement(media, 'color').text = data['Color']
        if 'DataRate' in data and data['DataRate']:
            dataRate = etree.SubElement(media, 'dataRate')
            d = data['DataRate'].split(" ")
            dataRate.text = d[0]
            dataRate.set('rate', d[1])
        if 'FrameRate' in data and data['FrameRate']:
            frame = etree.SubElement(media, 'frame')
            frame.text = data['FrameRate']
            frame.set('rate', 'second')
        # create video format element and subelements
        if 'ScanSignal' in data or 'VideoStandard' in data:
            videoFormat = etree.SubElement(media, 'videoFormat')
            if data['ScanSignal']:
                etree.SubElement(videoFormat, 'scanSignal').text = data['ScanSignal']
            if data['VideoStandard']:
                etree.SubElement(videoFormat, 'videoStandard').text = data['VideoStandard']
        # create videoResolution and subelement only if all three are present
        if all (k in data for k in ('AspectRatio','HorizontalPixels','VerticalPixels')):
            videoRes = etree.SubElement(media, 'videoResolution')
            etree.SubElement(videoRes, 'aspectRatio').text = data['AspectRatio']
            etree.SubElement(videoRes, 'horizontalPixels').text = data['HorizontalPixels']
            etree.SubElement(videoRes, 'verticalPixels').text = data['VerticalPixels']
    # populate the sound container element
    if 'Mono/Stereo' in data and data['Mono/Stereo']:
        etree.SubElement(sound, 'soundField').text = data['Mono/Stereo']
    if 'Language' in data and data['Language']:
        etree.SubElement(sound, 'language').text = data['Language']
    return etree.tostring(tech_meta, pretty_print=True)


# Performs series of find and replace operations to generate UMAM file from the template.
def createUMAM(data, batch, pid):
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # create technical metadata section
    techMeta = generateTechnicalMetaString(data, batch['mediaType'], 
        batch['convertTime']).decode('utf-8')
    
    # initialize the output starting with the specified template file
    outputfile = batch['umam']
    # create mapping of the metadata onto the UMAM XML template file
    umamMap = {
                '!!!PID!!!' :                   pid,
                '!!!ContentModel!!!' :          'UMD_VIDEO',
                '!!!Status!!!' :                batch['rightsScheme']['amInfoStatus'],
                '!!!FileName!!!' :              data['FileName'],
                '!!!DateDigitized!!!' :         data['DateDigitized'],
                '!!!DigitizedByDept!!!' :       data['DigitizedByDept'],
                '!!!ExtRefDescription!!!' :     'Sharestream',
                '!!!SharestreamURL!!!' :        data['SharestreamURLs'],
                '!!!DigitizedByPers!!!' :       data['DigitizedByPers'],
                '!!!DigitizationNotes!!!' :     data['DigitizationNotes'],
                '!!!AccessRights!!!' :          batch['rightsScheme']['adminRightsAccess'],
                '!!!TimeStamp!!!' :             timeStamp,
                '!!!TechMeta!!!' :              techMeta
    }
    # Carry out a find and replace for each line of the data mapping
    # and convert ampersands in data into XML entities in the process
    for k, v in umamMap.items():
        outputfile = outputfile.replace(k, v.replace('&', '&amp;'))
    return outputfile


# Performs series of find and replace operations to generate UMDM file from the template.
def createUMDM(data, batch, summedRunTime, mets):
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # Initialize the output starting with the specified template file
    outputfile = batch['umdm']
    # Strip out trailing quotation marks from Dimensions field
    if data['Dimensions'].endswith('"'):
        data['Dimensions'] = data['Dimensions'][0:-1]
    # Generate Agents (Creator, Contributor, Provider)
    agentsString = generateAgentsString(    creator=(data['Creator'], data['CreatorType']),
                                            contributor=(data['Contributor'], data['ContributorType']),
                                            provider=(data['Provider/Publisher'], data['Provider/PublisherType'])
                                            )
    # Generate dating tags  
    dateTagString = generateDateTag(data['DateCreated'], data['DateAttribute'], data['Century'])
    # Generate browse terms
    browseTermsString = generateBrowseTerms(data['RepositoryBrowse'])
    # Generate topical subjects
    topicalSubjects = generateTopicalSubjects(  pers=(data['PersonalSubject'], data['PersonalScheme']),
                                                corp=(data['CorpSubject'], data['CorpScheme']),
                                                top=(data['TopicalSubject'], data['TopicalScheme']),
                                                geog=(data['GeographicalSubject'], data['GeographicalScheme'])
                                                )
    # Generate MediaType XML Tags
    mediaTypeString = generateMediaTypeTag(data['MediaType'], data['FormType'], data['Form'])
    # Generate Archival Location Information Tags
    archivalLocation = generateArchivalLocation(collection=data['ArchivalCollection'],
                                                series=data['Series'],
                                                subseries=data['Subseries'],
                                                box=data['Box'],
                                                item=data['Item'],
                                                accession=data['Accession'] 
                                                )
    # Insert the RELS-METS section compiled from the UMAM files
    outputfile = outputfile.replace('!!!INSERT_METS_HERE!!!', mets)     # Insert the METS
    outputfile = stripAnchors(outputfile)                               # Strip out anchor points
    # XML tags with which to wrap the CSV data
    XMLtags = {
            '!!!ContentModel!!!' :     {    'open' : '<type>',
                                            'close' : '</type>'    },
            '!!!Status!!!' : {              'open' : '<status>',
                                            'close' : '</status>' },
            '!!!Title!!!' : {               'open' : '<title type="main">',
                                            'close' : '</title>' },
            '!!!AlternateTitle!!!' : {      'open' : '<title type="alternate">',
                                            'close' : '</title>'},
            '!!!Identifier!!!' : {          'open' : '<identifier>',
                                            'close' : '</identifier>'},
            '!!!Description/Summary!!!' : { 'open' : '<description type="summary">',
                                            'close' : '</description>'},
            '!!!Rights!!!' : {              'open' : '<rights type="access">',
                                            'close' : '</rights>'},
            '!!!CopyrightHolder!!!' : {     'open' : '<rights type="copyrightowner">',
                                            'close' : '</rights>'},
            '!!!Continent!!!' : {           'open' : '<geogName type="continent">',
                                            'close' : '</geogName>'},
            '!!!Country!!!' : {             'open' : '<geogName type="country">',
                                            'close' : '</geogName>'},
            '!!!Region/State!!!' : {        'open' : '<geogName type="region">',
                                            'close' : '</geogName>'},
            '!!!Settlement/City!!!' : {     'open' : '<geogName type="settlement">',
                                            'close' : '</geogName>'},
            '!!!Repository!!!' : {          'open' : '<repository><corpName>',
                                            'close' : '</corpName></repository>'},
            '!!!Dimensions!!!' : {          'open' : '<size units="in">',
                                            'close' : '</size>'},
            '!!!DurationMasters!!!' : {     'open' : '<extent units="{0}">'.format(batch['timeUnits']),
                                            'close' : '</extent>'},
            '!!!Format!!!' : {              'open' : '<format>',
                                            'close' : '</format>'},
            '!!!ArchivalLocation!!!' : {    'open' : '<bibRef>',
                                            'close' : '</bibRef>'},
            '!!!Language!!!' : {            'open' : '<language>',
                                            'close' : '</language>'},
            '!!!Rights!!!' : {              'open' : '<rights>',
                                            'close' : '</rights>'}
            }

    # Create mapping of the metadata onto the UMDM XML template file
    umdmMap = {
                '!!!PID!!!' :                   data['PID'],
                '!!!ContentModel!!!' :          'UMD_VIDEO',
                '!!!Status!!!' :                batch['rightsScheme']['doInfoStatus'],
                '!!!Title!!!' :                 data['Title'],
                '!!!AlternateTitle!!!' :        data['AlternateTitle'],
                '!!!Agents!!!' :                agentsString,
                '!!!Identifier!!!' :            data['Identifier'],
                '!!!Description/Summary!!!' :   data['Description/Summary'],
                '!!!Rights!!!' :                data['Rights'],
                '!!!CopyrightHolder!!!' :       data['CopyrightHolder'],
                '!!!MediaType/Form!!!' :        mediaTypeString,
                '!!!Continent!!!' :             data['Continent'],
                '!!!Country!!!' :               data['Country'],
                '!!!Region/State!!!' :          data['Region/State'],
                '!!!Settlement/City!!!' :       data['Settlement/City'],
                '!!!InsertDateHere!!!' :        dateTagString,
                '!!!Language!!!' :              data['Language'],
                '!!!Dimensions!!!' :            data['Dimensions'],
                '!!!DurationMasters!!!' :       str(summedRunTime),
                '!!!Format!!!' :                data['Format'],
                '!!!RepositoryBrowse!!!' :      browseTermsString,
                '!!!Repository!!!' :            data['Department'],
                '!!!TopicalSubjects!!!' :       topicalSubjects,
                '!!!ArchivalLocation!!!' :      archivalLocation,
                '!!!CollectionPID!!!' :         batch['collectionPID'],
                '!!!TimeStamp!!!' :             timeStamp,
                '!!!TopicalSubjects!!!' :       topicalSubjects
    }

    # Carry out a find and replace for each line of the data mapping
    # and convert ampersands to XML entities in the process
    for k, v in umdmMap.items():
        if k in XMLtags.keys(): # If there is an XML tag available
            if v != '':         # and if the data point is not empty
                # wrap the data point with the XML tag and insert it in the template
                myTag = XMLtags[k]['open'] + v.replace('&', '&amp;') + XMLtags[k]['close']
                outputfile = outputfile.replace(k, myTag)
            else: # if the data is empty, get rid of the anchor point
                outputfile = outputfile.replace(k, '')
        else: # but if there is no xml tag available, simply replace anchor with value
            outputfile = outputfile.replace(k, v.replace('&', '&amp;'))
    return outputfile


# Initiates a new METS snippet for use in a UMDM file
def createMets():
    metsFile = open('templates/mets.xml', 'r').read()
    return(metsFile)


# Updates a METS record with UMAM info
def updateMets(partNumber, mets, fileName, pid):
    id = str(partNumber + 1)   # first item(s) are collection PIDs
    metsSnipA = open('templates/metsA.xml', 'r').read() + '!!!Anchor-A!!!'
    metsSnipB = open('templates/metsB.xml', 'r').read() + '!!!Anchor-B!!!'
    metsSnipC = open('templates/metsC.xml', 'r').read() + '!!!Anchor-C!!!'
    mets = mets.replace('!!!Anchor-A!!!', metsSnipA)
    mets = mets.replace('!!!Anchor-B!!!', metsSnipB)
    mets = mets.replace('!!!Anchor-C!!!', metsSnipC)
    mets = mets.replace('!!!FileName!!!', fileName)
    mets = mets.replace('!!!ID!!!', id)
    mets = mets.replace('!!!PID!!!', pid)
    mets = mets.replace('!!!Order!!!', str(partNumber))
    return mets


# Strips out the anchor points used in creating the METS 
def stripAnchors(target):
    f = re.sub(r"\n\s*!!!Anchor-[ABC]!!!", "", target)
    return f


def main():
    
    mets = ""           # empty string for compiling METS record
    objectGroups = 0    # counter for UMDM plus UMAM(s) as a group
    objectParts = 0     # counter for the number of UMAM parts for each UMDM
    pidCounter = 0      # counter for coordinating PID list with data lines from CSV
    filesWritten = 0    # counter for file outputs
    umdmList = []       # list for compiling list of UMDM pids
    outputFiles = []    # list for compiling list of all pids written
    summaryList = []    # list for compiling list of PIDs and Object IDs
    batch = {}          # dictionary for batch-related metadata
    
    # Create a timeStamp for these operations
    timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Initiate the program, recording the timestamp and name of user
    greeting()
    
    # Load CSV data
    dataFile, fileName = loadFile('data')
    
    # Parse loaded data and request user input to calculate num of PIDS needed
    pidsNeeded, dataFileArrangement = analyzeDataFile(dataFile)
    
    # Request PIDs from the server OR load PIDs from previously saved file.
    pidFile = getPids(pidsNeeded)
    
    # Parse the XML PID file (either local or from the server) to get list of PIDs
    pidList = parsePids(pidFile)
    
    # Check whether the loaded file has enough PIDs, abort if not enough
    if len(pidList) < pidsNeeded:
        print('Not enough PIDs for your dataset!')
        print('Please reserve additional PIDs from the server and try again.')
        print('Exiting program.')
        quit()
    
    # Get the mediaType and collection from user input
    batch['rightsScheme'] = getRightsScheme()
    batch['mediaType'] = getMediaType()
    batch['collectionPID'] = getCollection()
    batch['nullTimeCounter'], batch['convertTime'], batch['timeUnits'] = timeFormatSelection()
    convertTime = batch['convertTime']
    
    # setup variable to hold sum of constituent UMAM runtimes for UMDM
    summedRunTime = batch['nullTimeCounter']   
    
    # Load the UMAM template and print it to screen  
    batch['umam'], batch['umamName'] = loadFile('umam')
    print("\n UMAM:\n" + batch['umam'])
    print('*' * 30)
    
    # Load the UMDM template and print it to screen
    batch['umdm'], batch['umdmName'] = loadFile('umdm')
    print("\n UMDM:\n" + batch['umdm'])
    print('*' * 30)
    
    # Load the lines of the data file into a csv.DictReader object
    myData = csv.DictReader(dataFile)
    print('Data successfully read.')
    
    # Generate XML for data arranged with multiple lines (UMAM and UMDM) per object
    if dataFileArrangement == 'M':
        
        for x in myData:
            
            # Attach a PID to the line of data.
            x['PID'] = pidList[pidCounter]
            pidCounter += 1
            
            # Attach summary info to summary list, depending on XML type
            if x['XMLType'] == 'UMDM':
                link = '"{0}","{1}","{2}","http://digital.lib.umd.edu/video?pid={2}"'.format(x['Identifier'],
                                                                                             x['XMLType'], x['PID'])
            elif x['XMLType'] == 'UMAM':
                link = '"{0}","{1}","{2}"'.format(x['Identifier'], x['XMLType'], x['PID'])
            summaryList.append(link)
            
            # Check the XML type for each line, and build the FOXML files accordingly
            if x['XMLType'] == 'UMDM':
                
                # If the mets variable is NOT empty, finish the UMDM for the previous group
                if mets != "":
                    myFile = createUMDM(tempData, batch, summedRunTime, mets)
                    fileStem = tempData['PID'].replace(':', '_').strip()    # convert ':' to '_' in PID for use in filename
                    writeFile(fileStem, myFile, '.xml')                     # Write the file
                    
                    # Print summary info to the screen
                    print('Creating UMDM for object with {0} parts...'.format(objectParts), end=" ")
                    print('\nTotal runtime of all parts = {0}.'.format(str(summedRunTime)))
                    print('UMDM = {0}'.format(fileStem))
                    
                    # Append PID to list of all files created and list of UMDM files created
                    umdmList.append(tempData['PID'])
                    outputFiles.append(tempData['PID'])
                    filesWritten += 1
                    
                    # Reset counters
                    objectParts = 0                             # reset parts counter
                    summedRunTime = batch['nullTimeCounter']    # reset runtime sum counter for masters
                
                # Begin a new UMDM group by incrementing the group counter, printing a notice to screen,
                # storing the line of UMDM data for use after UMAMs are complete, and initiating a new METS
                objectGroups += 1
                print('\nFILE GROUP {0}: '.format(objectGroups))
                tempData = x
                mets = createMets()
                
            # If the line is a UMAM line
            elif x['XMLType'] == 'UMAM':
                
                # Create UMAM, convert PID for use as filename, write the file
                myFile = createUMAM(x, batch, x['PID'])
                convertedDerivativeRunTime = convertTime(x['DurationDerivatives'])
                fileStem = x['PID'].replace(':', '_').strip()
                writeFile(fileStem, myFile, '.xml')
                
                # Increment counters
                outputFiles.append(x['PID'])
                summedRunTime += convertedDerivativeRunTime
                objectParts += 1
                filesWritten += 1
                
                # Print summary info to the screen
                print('Writing UMAM...', end=' ')
                print("Converted runtime = {0}".format(convertedDerivativeRunTime))
                print('Part {0}: UMAM = {1}'.format(objectParts, fileStem))
                
                # Update the running METS record for use in finishing the UMDM
                mets = updateMets(objectParts, mets, x['FileName'], x['PID'])
                
        # After iteration complete, finish the last UMDM    
        myFile = createUMDM(tempData, batch, summedRunTime, mets)
        fileStem = tempData['PID'].replace(':', '_').strip()    # convert ':' to '_' in PID for use in filename
        writeFile(fileStem, myFile, '.xml')                     # Write the file
        
        # Print summary info to the screen
        print('Creating UMDM for object with {0} parts...'.format(objectParts), end=" ")
        print('\nTotal runtime of all parts = {0}.'.format(str(summedRunTime)))
        print('UMDM = {0}'.format(fileStem))
                    
        # Append PID to list of all files created and list of UMDM files created
        umdmList.append(tempData['PID'])
        outputFiles.append(tempData['PID'])
        filesWritten += 1
        
    # Generate XML for data arranged with single lines (UMAM plus UMDM) per object
    elif dataFileArrangement == 'S':
        
        # Assign two PIDs to each line
        for x in myData:
            x['umdmPID'] = pidList[pidCounter]
            pidCounter += 1
            x['umamPID'] = pidList[pidCounter]
            pidCounter += 1
            
            # Attach summary info to summary list, once for each file
            link1 = '"{0}","{1}","{2}","http://digital.lib.umd.edu/video?pid={2}"'.format(x['Identifier'],
                                                                                          'UMDM', x['umdmPID'])
            link2 = '"{0}","{1}","{2}"'.format(x['Identifier'],
                                               'UMAM', x['umamPID'])
            summaryList.append(link1)
            summaryList.append(link2)
            
            # Increment the object counter and print feedback to screen
            objectGroups += 1
            print('\nFILE GROUP {0}: '.format(objectGroups))
            
            # Initiate the METS
            mets = createMets()
            
            # Create UMAM, convert PID for use as filename, write the file
            myFile = createUMAM(x, batch, x['umamPID'])
            fileStem = x['umamPID'].replace(':', '_').strip()
            writeFile(fileStem, myFile, '.xml')
            
            # Increment counters
            summedRunTime += convertedDerivativeRunTime
            objectParts += 1
            filesWritten += 1
            
            # Update the running METS record for use in finishing the UMDM
            mets = updateMets(objectParts, mets, x['File Name'], x['umamPID'])
            
            # Print summary info to the screen
            print('Part {0}: UMAM = {1}'.format(objectParts, fileStem))
            print('Writing UMAM...', end=' ')
            
            # Create UMDM
            createUMDM(x, batch, summedRunTime, mets)
            
            # Print summary info to the screen
            print('Creating UMDM for object with {0} parts...'.format(objectParts), end=" ")
            print('\nTotal runtime of all parts = {0}.'.format(str(summedRunTime)))
            print('UMDM = {0}'.format(fileStem))
            
            # Append PID to list of all files created and list of UMDM files created
            umdmList.append(x['umdmPID'])
            outputFiles.append(x['umdmPID'])
            filesWritten += 1
          
            # Reset counters
            objectParts = 0                     # reset parts counter
            summedRunTime = nullTimeCounter       # reset runtime sum counter
            
    # Abort if the value of dataFileArrangement is something else
    else:
        print('Bad dataFileArrangement value!')
        quit()
        
    # Generate summary files
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
    
    # Print a divider and summarize output to the screen.
    print('\n' + ('*' * 30))               
    print('\n{0} files written: {1} FOXML files in {2}'.format(filesWritten, filesWritten - 3,
                                                               objectGroups), end=' ')
    print('groups, plus the summary list of pids, list of UMDM pids, and the links file.')
    print('Thanks for using the XML generator!\n\n')
        
main()
