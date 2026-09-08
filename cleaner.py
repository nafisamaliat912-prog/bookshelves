import pandas as pd
import re

raw_file = 'gutenberg_expanded_raw.csv'
cleaned_file = 'gutenberg_books_cleaned.csv'

try:
    df = pd.read_csv(raw_file, dtype=str)  # সব কলামকে শুরুতে স্ট্রিং হিসেবে পড়ার জন্য
    print(f" Raw dataset loaded successfully. Total rows: {len(df)}")
except FileNotFoundError:
    print(f" Error: '{raw_file}' file not found!")
    exit()

print("\n--- Initial Missing Values ---")
print(df.isnull().sum())

initial_count = len(df)
df.drop_duplicates(subset=['Book_ID'], keep='first', inplace=True)
print(f"\n Removed {initial_count - len(df)} duplicate records based on Book_ID.")

def clean_downloads(val):
    if pd.isna(val) or val in ['N/A', 'nan', 'None', '']:
        return 0
    num = re.sub(r'[^\d]', '', str(val))
    return int(num) if num else 0

df['Downloads'] = df['Downloads'].apply(clean_downloads)

df.fillna('N/A', inplace=True)

string_columns = ['Title', 'Author', 'Author_Years', 'Genre', 'Language', 
                  'Subject', 'Category_Code', 'Release_Date', 'Copyright_Status', 'EBook_No', 'Book_URL']

for col in string_columns:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        df[col] = df[col].replace({'nan': 'N/A', '': 'N/A', 'None': 'N/A'})

expected_columns = [
    'Book_ID', 'Title', 'Author', 'Author_Years', 'Genre', 'Language', 
    'Subject', 'Category_Code', 'Release_Date', 'Copyright_Status', 
    'Downloads', 'EBook_No', 'Book_URL'
]
df = df.reindex(columns=expected_columns)

df.to_csv(cleaned_file, index=False, encoding='utf-8-sig')

print("\n--------------------------------------------------")
print(f" Data cleaning finished successfully!")
print(f" Final cleaned dataset count: {len(df)} rows")
print(f" Cleaned file saved as: '{cleaned_file}'")
print("--------------------------------------------------")

print("\n--- Sample Cleaned Data (First 5 Rows) ---")
print(df[['Book_ID', 'Title', 'Author', 'Genre', 'Downloads', 'Language']].head())