#Pseudocode for XML Generator

1. prompt user to enter names of templates and CSV data files
2. get length of data file (= number of files to be created)
3. request requisite # of PIDs from server
4. parse returned result, extracting list of PIDs
5. iterate through data list, appending one pid to each line
6. iterate through data list creating files as follows
	1. create truncated UMDM
    2. create METS
    3. create UMAM (repeat c-e as long as next line is UMAM line)
	4. append info to METS
	5. write UMAM
	6. append METS to UMDM and write file
	7. repeat a-g to the end of data list
7. Issue results report to terminal