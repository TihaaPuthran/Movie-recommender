from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests

app = Flask(__name__)

# Load movie data and similarity matrix
movies = pd.read_csv("data/tmdb_5000_movies.csv")
similarity = pickle.load(open("artifacts/similarity.pkl", "rb"))

# Your TMDb API key
TMDB_API_KEY = "1a920218832eb05c82a6950e6d6790f3"

# Function to fetch poster from TMDb
def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    data = requests.get(url).json()
    results = data.get('results')
    if results:
        poster_path = results[0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, 
key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        movie_title = movies.iloc[i[0]].title
        poster_url = fetch_poster(movie_title)
        recommended_movies.append((movie_title, poster_url))
    return recommended_movies

@app.route('/')
def home():
    movie_list = movies['title'].values
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def recommend_movie():
    movie_name = request.form.get('movie')
    recommendations = recommend(movie_name)
    return render_template(
        'index.html',
        movie_list=movies['title'].values,
        recommendations=recommendations,
        selected_movie=movie_name
    )

if __name__ == "__main__":
    app.run(debug=True)

