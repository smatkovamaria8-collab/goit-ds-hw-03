import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

url = 'https://quotes.toscrape.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

quotes = soup.find_all('span', class_='text')
authors = soup.find_all('small', class_='author')
tags = soup.find_all('div', class_='tags')

quotes_data = []

for i in range(0, len(quotes)):
    tags_text = tags[i].find_all('a', class_='tag')
    tag = list()
    for tag_one in tags_text:
        tag.append(tag_one.text)

    quotes_data.append(
        {"tags" : tag,
         "author": authors[i].text,
         "quote": quotes[i].text}
         )


with open("qoutes.json", "w", encoding="utf-8") as j_file:
    json.dump(quotes_data, j_file, indent= 4, ensure_ascii=False)

authors_data = []

quote_details = soup.find_all("div", attrs={"class" : "quote"})

for quote in quote_details:

    author_url = f"{url}{quote.find('a')['href']}"
    request = requests.get(author_url)
    soup_author = BeautifulSoup(request.text, 'lxml')
    fullname = soup_author.find("h3", class_="author-title")
    born_date = soup_author.find("span", class_="author-born-date")
    born_location = soup_author.find("span", class_="author-born-location")
    description = soup_author.find("div", class_ = "author-description")

    existing_authors = [i["fullname"] for i in authors_data]
    if fullname.text not in existing_authors:
        authors_data.append({
            "fullname":fullname.text,
            "born_date": born_date.text,
            "born_location": born_location.text,
            "description": description.text.strip()
        })

with open("authors.json", "w", encoding="utf-8") as j_file:
    json.dump(authors_data, j_file, indent= 4, ensure_ascii=False)



uri = "mongodb+srv://maryshey1313:password@cluster0.rfwim81.mongodb.net/?appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db1 = client.authors
db2 = client.quotes

with open("authors.json", "r", encoding="utf-8") as f:
    authors_from_file = json.load(f)

with open("qoutes.json", "r", encoding="utf-8") as f:
    quotes_from_file = json.load(f)

authors_many = db1.authors.insert_many(authors_from_file)
quotes_many = db2.quotes.insert_many(quotes_from_file)
