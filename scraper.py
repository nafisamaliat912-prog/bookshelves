import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


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
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("Scraping started... Target: 2000+ books with Genre.")

for genre_name, search_keyword in genres.items():
    print(f"\nScraping Genre: {genre_name}...")
    
   
    for page in range(1, 21):
        start_index = (page - 1) * 25 + 1
        url = f"https://www.gutenberg.org/ebooks/search/?query={search_keyword}&start_index={start_index}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            book_items = soup.find_all('li', class_='booklink')
            
            if not book_items:
                break

            for book in book_items:
                title_tag = book.find('span', class_='title')
                title = title_tag.text.strip() if title_tag else "N/A"

                author_tag = book.find('span', class_='subtitle')
                author = author_tag.text.strip() if author_tag else "Unknown / Various"

                extra_tag = book.find('span', class_='extra')
                downloads = extra_tag.text.strip() if extra_tag else "N/A"

                link_tag = book.find('a', class_='link')
                book_link = "https://www.gutenberg.org" + link_tag['href'] if link_tag else "N/A"

                books_data.append({
                    'Title': title,
                    'Author': author,
                    'Genre': genre_name,
                    'Downloads': downloads,
                    'Book_URL': book_link
                })
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"Total raw books collected so far: {len(books_data)}")
    
    
    if len(books_data) >= 3000:
        break

    time.sleep(0.5)


df = pd.DataFrame(books_data)
df = df.drop_duplicates(subset=['Title', 'Author'])

print(f"\n==========================================")
print(f"Final Total Unique Rows: {len(df)}")
print(f"==========================================")


df.to_csv('gutenberg_books_with_genre.csv', index=False, encoding='utf-8-sig')
print("Successfully saved as 'gutenberg_books_with_genre.csv'!")