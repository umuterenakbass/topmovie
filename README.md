# CineFind - IMDb Movie Discovery App

CineFind is a web application that helps users discover top-rated movies by genre using IMDb data. The app features a modern UI, fast movie scraping, random recommendations, and CSV export functionality.

## Features

- Browse movies by genre (Action, Comedy, Drama, etc.)
- Scrapes IMDb for the latest top movies
- View movie details and IMDb ratings
- Click movie titles to open IMDb pages
- Get 3 random movie recommendations
- Export results to CSV
- Responsive and visually appealing design

## Technologies Used

- Python (Flask)
- BeautifulSoup (for web scraping)
- HTML, CSS, JavaScript

## How to Run

1. Install dependencies:
   ```
   pip install flask flask_cors beautifulsoup4 requests
   ```
2. Start the Flask server:
   ```
   python app.py
   ```
3. Open your browser and go to:  
   ```
   http://localhost:5001
   ```

## Project Structure

- `app.py` — Main Flask application
- `imdb_scraper.py` — IMDb scraping logic
- `templates/index.html` — Frontend UI
- `static/style.css` — Stylesheet

## License

MIT
