myDate = input('Enter a date: ')
myDateType = input('Enter the type of date: ')
if myDateType == 'range':
    elements = myDate.split('-')
    print(len(elements))
    if len(elements) == 2:
        beginDate = elements[0]
        endDate = elements[1]
    elif len(elements) == 6:
        beginDate = elements[2]
        endDate = elements[5]
    myTag = '<date certainty="{0}" era="ad" from="{1}" to="{2}">{3}</date>'.format(myDateType, beginDate, endDate, myDate)
    print(myTag)
else:
    print("You didn't enter a range!")