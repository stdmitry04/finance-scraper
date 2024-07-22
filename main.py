import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient

def scrape_techcrunch(company_name):
    url = f"https://techcrunch.com/search/{company_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # make request
    response = requests.get(url, headers)

    # check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url}")
    
    # parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # list to hold articles data
    articles = []

    # find all list items representing articles
    for li in soup.find_all('li', class_='wp-block-post'):
        # Extract title and link
        title_tag = li.find('h2', class_='wp-block-post-title')
        if title_tag:
            link_tag = title_tag.find('a')
            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag['href']
                
                # Extract time
                time_tag = li.find('time')
                if time_tag:
                    timestamp = time_tag.get_text(strip=True)
                else:
                    timestamp = 'No timestamp available'
                
                articles.append({'title': title, 'link': link, 'timestamp': timestamp})

    return pd.DataFrame(articles)

if __name__ == "__main__":
    company_name = str(input())
    news_df = scrape_techcrunch(company_name)
    news_df.to_csv(f"{company_name}_news.csv", index=False)
    print(news_df)