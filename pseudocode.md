#Pseudocode for XML Generator

1. prompt user to enter names of templates and CSV data files
2. get length of data file (= number of files to be created)
3. request requisite # of PIDs from server
4. parse returned result, extracting list of PIDs
5. iterate through data list, appending one pid to each line
6. iterate through data list creating files as follows
>	a. create truncated UMDM
>   	b. create METS
>   	c. create UMAM (repeat c-e as long as next line is UMAM line)
>	d. append info to METS
>	e. write UMAM
>	f. append METS to UMDM and write file
>	g. repeat a-g to the end of data list
7. Issue results-report to terminal, save log file
