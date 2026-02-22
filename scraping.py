from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

url = 'https://quotes.toscrape.com/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
next_page_links = [soup]



def next_link(soup):
    try:
        next_page_lk=soup.find("nav").find("li", class_="next").find("a")['href']
        next_page_link = urljoin(url, next_page_lk)
        response = requests.get(next_page_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            next_page_links.append(soup)
            next_link(soup)
        return []
    except AttributeError:
        print("This page does not have next page")

next_link(soup)

quotes_data = []

for link_soup in next_page_links:
    quotes = link_soup.find_all('span', class_='text')
    authors = link_soup.find_all('small', class_='author')
    tags = link_soup.find_all('div', class_='tags')


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


with open("quotes.json", "w", encoding="utf-8") as j_file:
    json.dump(quotes_data, j_file, indent= 4, ensure_ascii=False)

authors_data = []
existing_authors = set()

for link_soup in next_page_links:
    quote_details = link_soup.find_all("div", attrs={"class" : "quote"})

    for quote in quote_details:

        about_link = quote.find('a', string='(about)')
        if not about_link:
            continue
        author_url = urljoin(url, about_link['href'])

        request = requests.get(author_url)
        if request.status_code == 200:
            soup_author = BeautifulSoup(request.text, 'lxml')
            fullname = soup_author.find("h3", class_="author-title")
            if not fullname:
                continue
            born_date = soup_author.find("span", class_="author-born-date")
            born_location = soup_author.find("span", class_="author-born-location")
            description = soup_author.find("div", class_ = "author-description")

            if fullname.text not in existing_authors:
                existing_authors.add(fullname.text)
                authors_data.append({
                    "fullname":fullname.text,
                    "born_date": born_date.text,
                    "born_location": born_location.text,
                    "description": description.text.strip()
                })


with open("authors.json", "w", encoding="utf-8") as j_file:
    json.dump(authors_data, j_file, indent= 4, ensure_ascii=False)



uri = "mongodb+srv://username:password@cluster0.rfwim81.mongodb.net/?appName=Cluster0"
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

with open("quotes.json", "r", encoding="utf-8") as f:
    quotes_from_file = json.load(f)

authors_many = db1.authors.insert_many(authors_from_file)
quotes_many = db2.quotes.insert_many(quotes_from_file)
