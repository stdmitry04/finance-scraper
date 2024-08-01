from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dateutil import parser
import config
import db_manager

def convert_timestamp(timestamp_str):
    # Remove timezone abbreviation if present
    timestamp_str = timestamp_str.split('•')[0].strip()  
    try:
        dt = parser.parse(timestamp_str)
        return dt.strftime("%Y-%m-%d")
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None

def scrape_techcrunch(company_name):
    base_url = "https://techcrunch.com/"
    page_number = 1
    articles = []

    while page_number < 20:
        url = f"{base_url}page/{page_number}/?s={company_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to load page {url}")

        soup = BeautifulSoup(response.text, "html.parser")

        page_not_found = soup.find('h1', class_='wp-block-heading')
        if page_not_found and 'Page Not Found' in page_not_found.get_text(strip=True):
            break

        page_articles = []
        article_elements = soup.find_all('li', class_='wp-block-post')

        if not article_elements:
            break

        for li in article_elements:
            title_tag = li.find('h2', class_='wp-block-post-title')
            if title_tag:
                link_tag = title_tag.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag['href']

                    time_tag = li.find('time')
                    timestamp = time_tag.get_text(strip=True) if time_tag else 'No timestamp available'
                    formatted_date = convert_timestamp(timestamp) if timestamp != 'No timestamp available' else 'No date available'

                    if formatted_date != 'No date available':
                        page_articles.append({
                            'company': company_name,
                            'title': title,
                            'link': link,
                            'timestamp': formatted_date
                        })

        if not page_articles:
            break

        articles.extend(page_articles)
        page_number += 1

    return articles  # Return a list of dictionaries instead of a DataFrame

def main():
    company_name = input("Enter the company name: ").strip()
    
    # Scrape the articles
    articles = scrape_techcrunch(company_name)
    
    # Save the articles to MongoDB
    db_manager.save_articles('news', articles)
    print(f"Successfully saved {len(articles)} articles to the database.")

if __name__ == "__main__":
    main()
