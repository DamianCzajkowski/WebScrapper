import urllib.request
from bs4 import BeautifulSoup

url = "https://www.x-kom.pl/p/1065634-smartfon-telefon-google-pixel-6a-5g-6-128gb-charcoal.html"

page = urllib.request.urlopen(url)

soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")

price = soup.find("div", {"class": "sc-n4n86h-4 jwVRpW"})
float_price = float(price.next_element[:-3].replace(" ", "").replace(",", "."))
print(float_price)
