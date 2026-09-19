import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv('gutenberg_books_cleaned.csv')

df['Downloads'] = pd.to_numeric(df['Downloads'], errors='coerce').fillna(0)

avg_downloads = df['Downloads'].mean()

df['Is_Popular'] = (df['Downloads'] > avg_downloads).astype(int)
df['Genre_Code'] = df['Genre'].astype('category').cat.codes
df['Language_Code'] = df['Language'].astype('category').cat.codes
df['Subject_Code'] = df['Subject'].astype('category').cat.codes
df['Category_Code_Num'] = df['Category_Code'].astype('category').cat.codes

X = df[['Genre_Code', 'Language_Code', 'Subject_Code', 'Category_Code_Num']]
y = df['Is_Popular']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=6, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print('----------------------------------------')
print(f"Task 1: Classification Model Finished")
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print('----------------------------------------')
print("\nClassification Report:")
print(classification_report(y_test, predictions))