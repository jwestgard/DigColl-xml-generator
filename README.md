DigColl-xml-generator
=====================

Python script to generate Fedora XML files from template files and CSV data, developed for Digital Collections work at University of Maryland Libraries.  

For testing purposes, you can use the included umam.xml (University of Maryland Administrative Metadata) and umdm.xml (University of Maryland Descriptive Metadata) as XML templates, batch1.csv as the data file, and pids1.txt as the PID file (the program will prompt you to specify those files).

The program assumes that the XML templates and data files will be in the same working directory as the python script. It also assumes that there will be a sub-directory called 'output' for the resulting XML files.

============
__UPDATE 2013-09-12:__ The whole script has been revised as xmlgen2.py.  The revised version attempts to accommodate audio or video objects coming from any collection, and therefore the program no longer assumes that modifiable metadata elements are hardcoded in the XML templates. In addition, a succinct mapping of all metadata elements has been implemented as two python dictionaries, for easier updating in the future.

============
__UPDATE 2014-09-23:__ Another major revision has been undertaken, including aligning the metadata column headings expected by the script more closely with standards and practices throughout the libraries, allowing for the expression of object duration in units other than minutes (by first converting input times to timedelta objects), and integrating more comprehensive handling of topical subjects and browse terms.  This version is xmlgen3.py.
