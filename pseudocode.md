#Pseudocode for XML Generator

1. prompt user to enter names of templates and CSV data files
2. get length of data file (= number of files to be created)
3. request requisite # of PIDs from server
4. parse returned result, extracting list of PIDs
5. iterate through data list, appending one pid to each line
6. iterate through data list creating files as follows:
    * create truncated UMDM
8. create METS
9. create UMAM (repeat 7-9 as long as next line is UMAM line)
10. append info to METS
11. write UMAM
12. append METS to UMDM and write file
13. repeat 7-13 to the end of data list
14. Issue results-report to terminal, save log file
