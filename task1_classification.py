import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

plt.style.use('dark_background')
BG_COLOR = '#030b1e'

def apply_3d_style(ax):
    ax.set_facecolor(BG_COLOR)
    ax.xaxis.pane.set_edgecolor('#00f0ff')
    ax.yaxis.pane.set_edgecolor('#00f0ff')
    ax.zaxis.pane.set_edgecolor('#00f0ff')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(True, color='#0a2540', linestyle='--', alpha=0.7)

df = pd.read_csv('gutenberg_books_cleaned.csv')

df['Downloads'] = pd.to_numeric(df['Downloads'], errors='coerce').fillna(0)
download_threshold = df['Downloads'].median()
df['Is_Popular'] = (df['Downloads'] > download_threshold).astype(int)

df['Title_Length'] = df['Title'].fillna('').apply(len)
df['Author_Length'] = df['Author'].fillna('').apply(len)
df['Release_Year'] = df['Release_Date'].astype(str).str.extract(r'(\d{4})').fillna(1900).astype(int)

categorical_cols = ['Genre', 'Language', 'Subject', 'Category_Code', 'Copyright_Status']
for col in categorical_cols:
    df[f'{col}_Code'] = df[col].astype('category').cat.codes

df['EBook_No'] = pd.to_numeric(df['EBook_No'], errors='coerce').fillna(0)
df['Book_ID_Num'] = pd.to_numeric(df['Book_ID'], errors='coerce').fillna(0)

features = [
    'Book_ID_Num', 'EBook_No', 'Release_Year', 'Title_Length', 'Author_Length',
    'Genre_Code', 'Language_Code', 'Subject_Code', 'Category_Code_Code', 'Copyright_Status_Code'
]
feature_names_readable = [
    'Book ID', 'EBook No', 'Release Year', 'Title Length', 'Author Length',
    'Genre', 'Language', 'Subject', 'Category Code', 'Copyright Status'
]

X = df[features]
Y = df['Is_Popular']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
model = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
model.fit(X_train, Y_train)
predictions = model.predict(X_test)

fig1 = plt.figure(figsize=(9, 6), facecolor=BG_COLOR)
ax1 = fig1.add_subplot(111, projection='3d')
apply_3d_style(ax1)

top_genres = df['Genre'].value_counts().head(7).index
df_top = df[df['Genre'].isin(top_genres)]
genre_pop = df_top.groupby(['Genre', 'Is_Popular']).size().unstack().fillna(0)

x = np.arange(len(top_genres))
ax1.plot(x, np.zeros_like(x), genre_pop[1], color='#00f0ff', linewidth=3.5, label='Popular Category', marker='o')
ax1.plot(x, np.ones_like(x) * 2, genre_pop[0], color='#ff007f', linewidth=3.5, label='Non-Popular Category', marker='s')

ax1.set_xticks(x)
ax1.set_xticklabels(top_genres, rotation=25, ha='right', color='#e0f7fa', fontsize=8)
ax1.set_yticks([0, 2])
ax1.set_yticklabels(['Popular', 'Non-Popular'], color='#e0f7fa', fontsize=8)
ax1.set_zlabel('Book Count', color='#80f7ff', fontweight='bold')
ax1.view_init(elev=22, azim=-50)
ax1.set_title('Figure 1: 3D Ribbon Genre Distribution', color='#00f0ff', fontsize=11, fontweight='bold')
ax1.legend(facecolor='#021024', edgecolor='#00f0ff', labelcolor='#ffffff')

fig2 = plt.figure(figsize=(9, 6), facecolor=BG_COLOR)
ax2 = fig2.add_subplot(111, projection='3d')
apply_3d_style(ax2)

df_valid_years = df[(df['Release_Year'] >= 1880) & (df['Release_Year'] <= 2025)]
yearly_downloads = df_valid_years.groupby('Release_Year')['Downloads'].mean().reset_index()

X_years = yearly_downloads['Release_Year'].values
Z_downloads = yearly_downloads['Downloads'].values
Y_depth = np.linspace(0, 4, 15)

X_grid, Y_grid = np.meshgrid(X_years, Y_depth)
Z_grid = np.tile(Z_downloads, (len(Y_depth), 1))

surf = ax2.plot_surface(X_grid, Y_grid, Z_grid, cmap='cool', edgecolor='none', alpha=0.85)
ax2.set_xlabel('Release Year', color='#80f7ff', fontweight='bold')
ax2.set_zlabel('Avg Downloads', color='#80f7ff', fontweight='bold')
ax2.view_init(elev=28, azim=-55)
ax2.set_title('Figure 2: 3D Surface Release Timeline', color='#00f0ff', fontsize=11, fontweight='bold')

fig3 = plt.figure(figsize=(9, 6), facecolor=BG_COLOR)
ax3 = fig3.add_subplot(111, projection='3d')
apply_3d_style(ax3)

importances = pd.Series(model.feature_importances_, index=feature_names_readable).sort_values(ascending=True)

y_pos = np.arange(len(importances))
x_pos = np.zeros(len(importances))
z_pos = np.zeros(len(importances))

dx = importances.values * 100
dy = np.ones(len(importances)) * 0.5
dz = np.ones(len(importances)) * 0.8

ax3.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, color='#00f0ff', edgecolor='#030b1e', alpha=0.85)

for i, (val, name) in enumerate(zip(dx, importances.index)):
    ax3.text(val + 1, i, 0.5, f'{val:.1f}%', color='#00f0ff', fontweight='bold', fontsize=8)

ax3.set_yticks(y_pos + 0.25)
ax3.set_yticklabels(importances.index, color='#e0f7fa', fontsize=8)
ax3.set_xlabel('Importance (%)', color='#80f7ff', fontweight='bold')
ax3.view_init(elev=20, azim=-45)
ax3.set_title('Figure 3: 3D Isometric Feature Importance Pillars', color='#00f0ff', fontsize=11, fontweight='bold')

fig4 = plt.figure(figsize=(9, 6), facecolor=BG_COLOR)
ax4 = fig4.add_subplot(111, projection='3d')
apply_3d_style(ax4)

cm = confusion_matrix(Y_test, predictions)
tn, fp, fn, tp = cm.ravel()

xpos = [0, 1, 0, 1]
ypos = [0, 0, 1, 1]
zpos = [0, 0, 0, 0]

dx = [0.5, 0.5, 0.5, 0.5]
dy = [0.5, 0.5, 0.5, 0.5]
dz = [tn, fp, fn, tp]

bar_colors = ['#00f0ff', '#ff0055', '#ff9900', '#00ff88']
ax4.bar3d(xpos, ypos, zpos, dx, dy, dz, color=bar_colors, edgecolor='#030b1e', alpha=0.85)

labels = [f"TN: {tn}", f"FP: {fp}", f"FN: {fn}", f"TP: {tp}"]
for i in range(4):
    ax4.text(xpos[i]+0.1, ypos[i]+0.1, dz[i]+5, labels[i], color='#ffffff', fontweight='bold', fontsize=9)

ax4.set_xticks([0.25, 1.25])
ax4.set_xticklabels(['Actual Non-Pop', 'Actual Pop'], color='#e0f7fa', fontsize=8)
ax4.set_yticks([0.25, 1.25])
ax4.set_yticklabels(['Pred Non-Pop', 'Pred Pop'], color='#e0f7fa', fontsize=8)
ax4.set_zlabel('Sample Count', color='#80f7ff', fontweight='bold')
ax4.view_init(elev=22, azim=-48)
ax4.set_title('Figure 4: 3D Block Towers - Confusion Matrix', color='#00f0ff', fontsize=11, fontweight='bold')

# Ekbare Shob Graph Open Korar Jonno Single plt.show()
plt.show()