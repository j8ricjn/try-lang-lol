from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "opm_secret_key" 

users_list = []
CSV_FILE = 'Filipino Musiclist.csv'

def get_data():
    try:
        # Load all columns from your CSV
        df = pd.read_csv(CSV_FILE).fillna("N/A")
        artists = sorted(df['Artist'].unique().tolist())
        genres = sorted(df['Genre'].unique().tolist())
        years = sorted(df['Release Year'].unique().tolist())
        all_songs = sorted(df['Song'].unique().tolist())
        return df, artists, genres, years, all_songs
    except:
        return pd.DataFrame(), [], [], [], []

@app.route('/')
def index():
    _, artists, genres, years, all_songs = get_data()
    if 'current_user' not in session:
        session['current_user'] = "Guest"
        session['current_user_genres'] = []

    return render_template('index.html', 
                           artists=artists, genres=genres, 
                           years=years, all_songs=all_songs, 
                           users=users_list, 
                           current_user=session.get('current_user'))

@app.route('/switch_user/<int:user_id>')
def switch_user(user_id):
    for user in users_list:
        if user['id'] == user_id:
            session['current_user'] = user['name']
            session['current_user_genres'] = user['fav_genres']
            flash(f"Switched to {user['name']}!")
            break
    return redirect(url_for('index'))

@app.route('/save_user', methods=['POST'])
def save_user():
    user_id = request.form.get('user_id') 
    name = request.form.get('username').strip()
    fav_genres = request.form.getlist('fav_genres')

    for user in users_list:
        if user['name'].lower() == name.lower() and str(user['id']) != user_id:
            flash("User name already exists!") 
            return redirect(url_for('index'))

    if user_id: 
        for user in users_list:
            if user['id'] == int(user_id):
                user['name'] = name
                user['fav_genres'] = fav_genres
                if session.get('current_user') == name:
                    session['current_user_genres'] = fav_genres
    else:
        new_id = len(users_list) + 1
        users_list.append({'id': new_id, 'name': name, 'fav_genres': fav_genres})
    
    return redirect(url_for('index'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    global users_list
    deleted_user = next((u for u in users_list if u['id'] == user_id), None)
    if deleted_user:
        if session.get('current_user') == deleted_user['name']:
            session['current_user'] = "Guest"
            session['current_user_genres'] = []
        users_list = [u for u in users_list if u['id'] != user_id]
    return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict():
    user_artist = request.form.get('artist')
    user_genre = request.form.get('genre')
    user_year = request.form.get('year') 

    df, artists, genres, years, all_songs = get_data()
    matches = df.copy()

    # Apply filters based on selection
    if user_year and user_year != "Any":
        matches = matches[matches['Release Year'].astype(str) == user_year]
    
    if user_artist and user_artist != "Any":
        matches = matches[matches['Artist'] == user_artist]
        
    if user_genre and user_genre != "Any":
        matches = matches[matches['Genre'].str.contains(user_genre, case=False, na=False)]

    recommendations = []
    message = None

    # Logic for handling limited results with cool commentary
    if len(matches) >= 5:
        recommendations = matches.sample(n=5).to_dict(orient='records')
        message = "Solid picks! We recommend checking these out to match your vibe."
    elif len(matches) > 0:
        # If there are some songs but fewer than 5 (Apologizing without saying sorry)
        recommendations = matches.to_dict(orient='records')
        message = "We hand-picked these exclusive tracks just for you! We recommend these:"
    else:
        # If no songs match at all
        message = "Your music taste is so unique that we couldn't find anything!"

    current_user = session.get('current_user')

    return render_template('index.html', 
                           recommendations=recommendations, 
                           results_message=message,
                           artists=artists, 
                           genres=genres, 
                           years=years, 
                           all_songs=all_songs,
                           users=users_list,
                           current_user=current_user,
                           selected_artist=user_artist, 
                           selected_genre=user_genre, 
                           selected_year=user_year)

if __name__ == '__main__':
    app.run(debug=True)
