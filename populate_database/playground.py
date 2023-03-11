import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

response = urllib.request.urlopen(
    'https://www.fashionnova.com/products/aint-got-nothing-to-lose-skinny-jean-black-wash')
content = response.read().decode("UTF-8")
file = open("index.html", "w")
file.write(content)
file.close()
bs = BeautifulSoup(content, 'html.parser')

print(bs)
print(bs.string)
