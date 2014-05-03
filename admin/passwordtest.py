def fetchWebpage(url):
    import requests
    page = requests.get(url)
    return page

p = fetchWebpage('http://www.cnn.com')
print(p.content)
import sys
print(sys.version)