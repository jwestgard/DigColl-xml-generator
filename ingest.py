# A dummy function to initiate interaction with the program.
def greeting():
    import datetime
    name = input("Enter your name: ")
    print("\nHello " + name + ", welcome to the XML generator!")
    currentTime = datetime.datetime.utcnow()
    print('It is now ' + str(currentTime))       # prints the current time

# Prompt the user to enter the name of the UMAM or UMDM template to be imported for populating
# with the data from the CSV file.
def loadTemplate(fileType):
    templatename = input("\nEnter the name of the %s template: " % (fileType))
    template = open(templatename, "r").read()
    return(template)

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
    hrsMinSec = []
    hrsMinSec = inputTime.split(':')
    minutes = int(hrsMinSec[0]) * 60
    minutes += int(hrsMinSec[1])
    minutes += int(hrsMinSec[2]) / 60
    print('\nTime Conversion: ' + str(hrsMinSec) + ' = ' + str(round(minutes, 2)))
    return round(minutes, 2)

def createUMAM(data, template):       # performs series of find and replace operations to
    import datetime                            # generate UMDM file from the template.
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

def createUMDM(data, template):         # performs series of find and replace operations to
    import datetime                              # generate UMDM file from the template.
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
        
def main():
    import csv, datetime                            # import needed modules
    greeting()                                             # a dummy greeting to get the program started
    datafile = input("\nEnter the name of the data file: ")             # Prompts the user to enter the   
    with open(datafile, mode='r', encoding='utf-8') as inputfile:   # name of a CSV data file (must be in 
        myData = csv.DictReader(inputfile)                                    # same directory); loads data from file
        umam = loadTemplate('UMAM')         # loads UMAM template by calling function
        print("\n UMAM:\n" + umam)            # prints UMAM
        print('*' * 30)                                    # prints a divider
        umdm = loadTemplate('UMDM')         # loads UMDM template by calling function
        print("\n UMDM:\n")                          # prints UMDM
        print(umdm)
        print('*' * 30)                                   # prints a divider
        i = 0                                                # initialize a counter for the rows of orignal data and output files
        for x in myData:                              # for each line in original data
            i += 1                                          # increment the counter
            print('\n' + ('*' * 30))
            print("\nDATASET " + str(i) + " :\n")   # prints the dataset (key/value pairs)
            print(x)
            if x['XML_Type'] == 'UMAM':                                        # checks whether it's a UMAM row
                outputFile = createUMAM(x, umam)                         # if yes, calls function to populate UMAM template
                writeFile(x['File Name'].strip(), 'umam', outputFile)   # writes output to file
            elif x['XML_Type'] == 'UMDM':                                      # checks whether it's a UMDM row
                outputFile = createUMDM(x, umdm)                        # if yes, calls function to populate UMDM template
                writeFile(x['Item Control Number'].strip(), 'umdm', outputFile)   # writes output to file
    print('\n' + ('*' * 30))                                                                                        # prints a divider
    print('\n%s files written. Thanks for using the XML generator!\n\n' % (i))      # summarizes total output

main()
