import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

plt.style.use('default')
BRIGHT_BG = '#ffffff'

df = pd.read_csv('gutenberg_books_cleaned.csv')

df['Downloads'] = pd.to_numeric(df['Downloads'], errors='coerce').fillna(0)
download_threshold = df['Downloads'].median()
df['Is_Popular'] = (df['Downloads'] > download_threshold).astype(int)

df['Title_Length'] = df['Title'].fillna('').apply(len)
df['Author_Length'] = df['Author'].fillna('').apply(len)
df['Release_Year'] = pd.to_numeric(df['Release_Date'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce').fillna(1900).astype(int)

categorical_cols = ['Genre', 'Language', 'Subject', 'Category_Code', 'Copyright_Status']
for col in categorical_cols:
    df[f'{col}_Code'] = df[col].astype('category').cat.codes

df['EBook_No'] = pd.to_numeric(df['EBook_No'], errors='coerce').fillna(0)
df['Book_ID_Num'] = pd.to_numeric(df['Book_ID'], errors='coerce').fillna(0)

features = [
    'Book_ID_Num', 'EBook_No', 'Release_Year', 'Title_Length', 'Author_Length',
    'Genre_Code', 'Language_Code', 'Subject_Code', 'Category_Code_Code', 'Copyright_Status_Code'
]

X = df[features]
Y = df['Is_Popular']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
model.fit(X_train, Y_train)
acc_score = model.score(X_test, Y_test) * 100
y_pred = model.predict(X_test)

df_valid = df[(df['Release_Year'] >= 1880) & (df['Release_Year'] <= 2025)].copy()

fig1, ax1 = plt.subplots(figsize=(9, 6), facecolor=BRIGHT_BG)
ax1.set_facecolor(BRIGHT_BG)

top_genres = df['Genre'].value_counts().head(6).index.tolist()
df_top = df[df['Genre'].isin(top_genres)]

genre_pop_counts = df_top.groupby(['Genre', 'Is_Popular']).size().unstack(fill_value=0)

x_indices = np.arange(len(top_genres))
width = 0.35

rects1 = ax1.bar(x_indices - width/2, genre_pop_counts[0], width, label='Non-Popular', color='#f59e0b', edgecolor='none')
rects2 = ax1.bar(x_indices + width/2, genre_pop_counts[1], width, label='Popular', color='#2563eb', edgecolor='none')

ax1.set_title('1. Genre Wise Book Count Distribution', fontsize=12, fontweight='bold', pad=15)
ax1.set_xlabel('Genre', fontweight='bold', color='#334155')
ax1.set_ylabel('Book Count', fontweight='bold', color='#334155')
ax1.set_xticks(x_indices)
ax1.set_xticklabels(top_genres, rotation=15, ha='right')
ax1.grid(True, color='#e2e8f0', linestyle=':', axis='y')
ax1.legend(loc='upper right', frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1')

fig2, ax2 = plt.subplots(figsize=(9, 6), facecolor=BRIGHT_BG)
ax2.set_facecolor(BRIGHT_BG)

decade_downloads = df_valid.groupby(pd.cut(df_valid['Release_Year'], bins=8))['Downloads'].mean()
decade_labels = [f"{int(b.left)}-{int(b.right)}" for b in decade_downloads.index]
bar_colors_fig2 = ['#2563eb', '#0d9488', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#0284c7']

bars2 = ax2.bar(decade_labels, decade_downloads.values, color=bar_colors_fig2, width=0.6)

for bar in bars2:
    height = bar.get_height()
    if not np.isnan(height) and height > 0:
        ax2.text(bar.get_x() + bar.get_width()/2., height + 50, f'{int(height)}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e293b')

ax2.set_title('2. Historical Release Year vs Average Downloads', fontsize=12, fontweight='bold', pad=15)
ax2.set_xlabel('Release Year Period', fontweight='bold', color='#334155')
ax2.set_ylabel('Average Downloads', fontweight='bold', color='#334155')
ax2.tick_params(axis='x', rotation=20)
ax2.grid(True, color='#e2e8f0', linestyle=':', axis='y')

fig3, ax3 = plt.subplots(figsize=(9, 6), facecolor=BRIGHT_BG)
ax3.set_facecolor(BRIGHT_BG)

importances = model.feature_importances_
feat_importances = pd.Series(importances, index=features).sort_values(ascending=False).head(6)
total_imp = feat_importances.sum()

tree_colors = ['#e11d48', '#0284c7', '#d97706', '#0d9488', '#7c3aed', '#ea580c']

grid_rects = [
    (0.00, 0.51, 0.32, 0.48),
    (0.34, 0.51, 0.32, 0.48),
    (0.68, 0.51, 0.32, 0.48),
    (0.00, 0.00, 0.32, 0.48),
    (0.34, 0.00, 0.32, 0.48),
    (0.68, 0.00, 0.32, 0.48)
]

for i, (feat, val) in enumerate(feat_importances.items()):
    rx, ry, rw, rh = grid_rects[i]
    pct = (val / total_imp) * 100
    rect_patch = patches.Rectangle((rx, ry), rw, rh, linewidth=2, edgecolor='white', facecolor=tree_colors[i])
    ax3.add_patch(rect_patch)
    ax3.text(rx + rw/2, ry + rh/2, f"{feat}\n{pct:.1f}%", ha='center', va='center', 
             color='white', fontweight='bold', fontsize=10.5, multialignment='center')

ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)
ax3.set_title('3. Feature Importance Analysis', fontsize=12, fontweight='bold', pad=15)
ax3.axis('off')

fig4, ax4 = plt.subplots(figsize=(8, 6), facecolor=BRIGHT_BG)
ax4.set_facecolor(BRIGHT_BG)

cm = confusion_matrix(Y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', cbar=True, ax=ax4,
            annot_kws={'size': 14, 'weight': 'bold'},
            xticklabels=['Non-Popular', 'Popular'],
            yticklabels=['Non-Popular', 'Popular'])

ax4.set_title('4. Detailed Model Confusion Matrix', fontsize=12, fontweight='bold', pad=15)
ax4.set_xlabel('Predicted Label', fontweight='bold', color='#334155')
ax4.set_ylabel('True Label', fontweight='bold', color='#334155')

fig5, ax5 = plt.subplots(figsize=(9, 6), facecolor=BRIGHT_BG)
ax5.set_facecolor(BRIGHT_BG)

max_pop_yr = df_valid.groupby('Release_Year')['Downloads'].mean().idxmax()

cards = [
    {'title': 'Model Accuracy', 'value': f'{acc_score:.1f}%', 'color': '#2563eb', 'rect': (0.05, 0.55, 0.42, 0.38)},
    {'title': 'Total Books Analyzed', 'value': f'{len(df):,}', 'color': '#10b981', 'rect': (0.53, 0.55, 0.42, 0.38)},
    {'title': 'Peak Download Year', 'value': f'{max_pop_yr}', 'color': '#f59e0b', 'rect': (0.05, 0.08, 0.42, 0.38)},
    {'title': 'Median Downloads', 'value': f'{int(download_threshold)}', 'color': '#ef4444', 'rect': (0.53, 0.08, 0.42, 0.38)}
]

for card in cards:
    rx, ry, rw, rh = card['rect']
    card_bg = patches.FancyBboxPatch((rx, ry), rw, rh, boxstyle="round,pad=0.03", 
                                     facecolor=card['color'], edgecolor='none', alpha=0.95)
    ax5.add_patch(card_bg)
    ax5.text(rx + rw/2, ry + rh*0.65, card['title'], ha='center', va='center', 
             color='#ffffff', fontsize=11, fontweight='bold')
    ax5.text(rx + rw/2, ry + rh*0.35, card['value'], ha='center', va='center', 
             color='#ffffff', fontsize=18, fontweight='bold')

ax5.set_xlim(0, 1)
ax5.set_ylim(0, 1)
ax5.set_title('5. Executive Performance Overview', fontsize=12, fontweight='bold', pad=15)
ax5.axis('off')

plt.show()