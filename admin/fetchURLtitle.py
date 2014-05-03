def fetchWebpage(url):
    import urllib.request
    data = str(urllib.request.urlopen(url).read())
    return data

def extractTitle(data):
    import re
    r = re.compile('<title>(.*?)</title>')
    m = r.search(data)
    if m:
        return m.group(1)
    else:
        print('Error: Not found')

target = input('Enter the URL from which you would like to extract the title:')
webpage = fetchWebpage(target)
result = extractTitle(webpage)
print(result)

