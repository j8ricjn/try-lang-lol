from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_csv('Filipino Musiclist.csv')
    artists = sorted(df['Artist'].unique().tolist())
    genres = sorted([g for g in df['Genre'].unique() if pd.notna(g)])
    years = sorted(df['Release Year'].dropna().unique().astype(int).tolist())
    return render_template('index.html', artists=artists, genres=genres, years=years)

@app.route('/predict', methods=['POST'])
def predict():
    user_artist = request.form.get('artist')
    user_genre = request.form.get('genre')
    user_year = request.form.get('year') 

    df = pd.read_csv('Filipino Musiclist.csv')
    matches = df.copy()

    # 1. Filter by Year
    if user_year and user_year != "Any":
        matches = matches[matches['Release Year'] == int(user_year)]

    # 2. Filter by Artist
    if user_artist and user_artist != "Any":
        artist_matches = matches[matches['Artist'] == user_artist]
        if not artist_matches.empty:
            matches = artist_matches
    
    # 3. STRICT Genre Filter
    if user_genre and user_genre != "Any":
        selected_genres = [g.strip() for g in user_genre.split('/')]
        matches = matches[matches['Genre'].isin(selected_genres) | (matches['Genre'] == user_genre)]

    # Fallback logic
    if matches.empty and user_year != "Any":
        matches = df[df['Release Year'] == int(user_year)]
    elif matches.empty:
        matches = df
    
    # Get 3 recommendations
    num_to_get = min(len(matches), 3)
    recommendations = matches.sample(n=num_to_get).to_dict(orient='records')

    # Lists for dropdowns
    artists = sorted(df['Artist'].unique().tolist())
    genres = sorted([g for g in df['Genre'].unique() if pd.notna(g)])
    years = sorted(df['Release Year'].dropna().unique().astype(int).tolist())

    return render_template('index.html', 
                           recommendations=recommendations, 
                           artists=artists,
                           genres=genres,
                           years=years,
                           # PASSING THESE BACK TO THE HTML
                           selected_artist=user_artist,
                           selected_genre=user_genre,
                           selected_year=user_year)

if __name__ == '__main__':
    app.run(debug=True)