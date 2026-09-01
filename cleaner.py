import pandas as pd

df=pd.read_csv('gutenberg_books_with_genre.csv')
print(f"Original total rows: {len(df)}")

df = df.dropna()

df =df[~df['Title'].str.strip().str.lower().isin(['n/a', 'none', ''])]
df =df[~df['Author'].str.strip().str.lower().isin(['n/a', 'unknown', 'unkknown / various', 'various', 'none', ''])]
df =df[~df['Downloads'].str.strip().str.lower().isin(['n/a', 'none', ''])]

df['Title'] = df['Title'].str.strip()
df['Author'] = df['Author'].str.strip()

df['title_lower']=df['Title'].str.lower()
df=df.drop_duplicates(subset=['title_lower'], keep='first')
df=df.drop(columns=['title_lower'])

df['Downloads']=df['Downloads'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
print(f"Cleaned dataset total unique rows: {len(df)}")

df.to_csv('gutenberg_books_cleaned.csv', index=False, encoding='utf-8-sig')
print(f"Successfully saved as 'gutenberg_books_cleaned.csv'!")