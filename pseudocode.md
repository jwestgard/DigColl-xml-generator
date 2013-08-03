#Pseudocode for XML Generator

1. prompt user to enter names of templates and CSV data files
2. get length of data file (= number of files to be created)
3. request requisite # of PIDs from server
4. parse returned result, extracting list of PIDs
5. iterate through data list, appending one pid to each line
6. iterate through data list creating files as follows:
7.     a. create truncated UMDM
8.     b. create METS
9.     c. create UMAM (repeat c-e as long as next line is UMAM line)
10.     d. append info to METS
11.     e. write UMAM
12.     f. append METS to UMDM and write file
13.     g. repeat a-g to the end of data list
7. Issue results-report to terminal, save log file
