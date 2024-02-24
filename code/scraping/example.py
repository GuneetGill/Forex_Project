from bs4 import BeautifulSoup

#this file is just showing different elements of beatifual soup library
#just different examples
#use beautifal soup to grab different elements from html webpage

#we have html in file so we open it
with open("index.html", "r") as f:
    data = f.read()

#print(data)

#give it data we loaded by file and then use parser which process HTML files
soup = BeautifulSoup(data, 'html.parser')

print(soup)

#if we want to get hold of each div we use select and then what we want to select
divs = list(soup.select("div"))

print(len(divs), "divs found")

#how many divs? loop tho all of them
for d in divs:
   print("\n --> ")
   print(d)

#get the elements and print it onto screen 
print(divs[0].get_text())
print(divs[1].get_text())


pps = divs[1].select("p")

print(len(pps), "ps found")
for p in pps:
   print(p.get_text())

#seleect everything with that class daily
dailies = soup.select(".daily")
for p in dailies:
   print("daily:", p)


ourp = dailies[1]

print(ourp)
print(ourp.get_text())
print(ourp.attrs['data-value'])


