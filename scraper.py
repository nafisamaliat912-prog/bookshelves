import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

genres = {
    'Fiction': 'fiction',
    'History': 'history',
    'Science & Tech': 'science',
    'Mystery & Detective': 'mystery',
    'Adventure': 'adventure',
    'Poetry': 'poetry',
    'Romance': 'romance',
    'Children Story': 'children'
}

books_data = []

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

print("Robust Cloudscraper Deep Scraping started...")

for genre_name, search_keyword in genres.items():
    print(f"\nScraping Genre: {genre_name}...")
    
    for page in range(1, 16):
        start_index = (page - 1) * 25 + 1
        url = f"https://www.gutenberg.org/ebooks/search/?query={search_keyword}&start_index={start_index}"
        
        
        response = None
        for attempt in range(3):
            try:
                response = scraper.get(url, timeout=25)
                if response.status_code == 200:
                    break
            except Exception:
                time.sleep(3) 
                
        if not response or response.status_code != 200:
            print(f"Skipping page {page} due to connection issue.")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        book_items = soup.find_all('li', class_='booklink')
        
        if not book_items:
            break

        for book in book_items:
            title_tag = book.find('span', class_='title')
            title = title_tag.text.strip() if title_tag else "N/A"

            author_tag = book.find('span', class_='subtitle')
            author = author_tag.text.strip() if author_tag else "N/A"

            extra_tag = book.find('span', class_='extra')
            downloads = extra_tag.text.strip() if extra_tag else "N/A"

            link_tag = book.find('a', class_='link')
            book_link = "https://www.gutenberg.org" + link_tag['href'] if link_tag else "N/A"
            book_id = link_tag['href'].split('/')[-1] if link_tag else "N/A"

            language, locc, subject, release_date, copyright_status, ebook_no, author_years = ["N/A"] * 7

            if book_link != "N/A":
                try:
                    detail_res = scraper.get(book_link, timeout=10)
                    if detail_res.status_code == 200:
                        detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                        bibrec = detail_soup.find('table', class_='bibrec')
                        
                        if bibrec:
                            for row in bibrec.find_all('tr'):
                                th = row.find('th')
                                td = row.find('td')
                                if th and td:
                                    label = th.text.strip()
                                    val = td.text.strip()

                                    if 'Language' in label:
                                        language = val
                                    elif 'Locc' in label or 'Category' in label:
                                        locc = val
                                    elif 'Subject' in label:
                                        subject = val.replace('\n', ' ')
                                    elif 'Release Date' in label:
                                        release_date = val
                                    elif 'Copyright Status' in label:
                                        copyright_status = val
                                    elif 'EBook-No.' in label:
                                        ebook_no = val
                                    elif 'Author' in label:
                                        years_match = re.search(r'\d{4}-\d{4}', val)
                                        if years_match:
                                            author_years = years_match.group(0)
                    time.sleep(0.15)
                except Exception:
                    pass

            books_data.append({
                'Book_ID': book_id,
                'Title': title,
                'Author': author,
                'Author_Years': author_years,
                'Genre': genre_name,
                'Language': language,
                'Subject': subject,
                'Category_Code': locc,
                'Release_Date': release_date,
                'Copyright_Status': copyright_status,
                'Downloads': downloads,
                'EBook_No': ebook_no,
                'Book_URL': book_link
            })

    print(f"Collected {len(books_data)} books so far...")
    if len(books_data) >= 2200:
        break

df = pd.DataFrame(books_data)
df.to_csv('gutenberg_expanded_raw.csv', index=False, encoding='utf-8-sig')
print(f"Scraping finished! Total books scraped: {len(df)}. Saved as 'gutenberg_expanded_raw.csv'")