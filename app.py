# app.py
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from imdb_scraper import IMDbMovieScraper
import random
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize scraper
scraper = IMDbMovieScraper()

# Cache for storing scraped movies
movie_cache = {}
scraping_status = {}

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/movies/<category>')
def get_movies(category):
    """API endpoint to get movies by category"""
    
    # Check if already cached
    if category in movie_cache:
        return jsonify({
            'status': 'success',
            'movies': movie_cache[category],
            'count': len(movie_cache[category])
        })
    
    # Check if scraping is in progress
    if category in scraping_status and scraping_status[category] == 'scraping':
        return jsonify({
            'status': 'scraping',
            'message': 'Scraping in progress...'
        })
    
    # Start scraping
    scraping_status[category] = 'scraping'
    
    def scrape_movies_background():
        try:
            print(f"Starting to scrape {category} movies...")
            movies = scraper.scrape_movies(category, limit=50)
            movie_cache[category] = movies
            scraping_status[category] = 'completed'
            print(f"Completed scraping {len(movies)} {category} movies")
        except Exception as e:
            print(f"Error scraping {category}: {str(e)}")
            scraping_status[category] = 'error'
    
    # Start background thread
    thread = threading.Thread(target=scrape_movies_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'scraping',
        'message': 'Started scraping movies...'
    })

@app.route('/api/movies/<category>/status')
def get_scraping_status(category):
    """Check the status of movie scraping"""
    status = scraping_status.get(category, 'not_started')
    
    if status == 'completed' and category in movie_cache:
        return jsonify({
            'status': 'completed',
            'movies': movie_cache[category],
            'count': len(movie_cache[category])
        })
    elif status == 'scraping':
        return jsonify({
            'status': 'scraping',
            'message': 'Still scraping movies...'
        })
    elif status == 'error':
        return jsonify({
            'status': 'error',
            'message': 'Error occurred while scraping'
        })
    else:
        return jsonify({
            'status': 'not_started'
        })

@app.route('/api/movies/<category>/random')
def get_random_movies(category):
    """Get random movie recommendations"""
    if category not in movie_cache:
        return jsonify({'error': 'No movies available for this category'})
    
    movies = movie_cache[category]
    if len(movies) < 3:
        return jsonify({'movies': movies})
    
    random_movies = random.sample(movies, 3)
    return jsonify({'movies': random_movies})

@app.route('/api/export/<category>')
def export_movies(category):
    """Export movies as CSV data"""
    if category not in movie_cache:
        return jsonify({'error': 'No movies available for this category'})
    
    movies = movie_cache[category]
    
    # Generate CSV content
    csv_content = "Rank,Title,Year,IMDb Rating,Category\n"
    for movie in movies:
        title = movie['title'].replace('"', '""')  # Escape quotes
        csv_content += f'{movie["rank"]},"{title}",{movie["year"]},{movie["rating"]},{category}\n'
    
    return jsonify({
        'csv_content': csv_content,
        'filename': f'imdb_{category}_movies.csv'
    })

if __name__ == '__main__':
    print("🎬 Starting CineFind Movie Scraper...")
    print("🌐 Open your browser to: http://localhost:5001")
    print("📡 API endpoints available at: http://localhost:5001/api/")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
