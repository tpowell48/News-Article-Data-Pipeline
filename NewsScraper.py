from bs4 import BeautifulSoup as bs
import requests
import re

url = "https://news.google.com/"

response = requests.get(url) #GET request to URL

#Check if request is successful
if response.status_code == 200:
    soup = bs(response.content, "html.parser") #Parse HTML content

    headlines = soup.find_all('a', class_ = 'gPFEn')
    
    for headline in headlines:
        print(headline.text.strip())

else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
