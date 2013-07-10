DigColl-xml-generator
=====================

Python script to generate Fedora XML files from template files and CSV data, developed for Digital Collections work at University of Maryland Libraries.  

For testing purposes, you can use the included umam.xml (University of Maryland Administrative Metadata) and umdm.xml (University of Maryland Descriptive Metadata) as XML templates, batch1.csv as the data file, and pids1.txt as the PID file (the program will prompt you to specify those files).

The program assumes that the XML templates and data files will be in the same working directory as the python script. It also assumes that there will be a sub-directory called 'output' for the resulting XML files.
