# imdb_scraper.py
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin

class IMDbMovieScraper:
    def __init__(self):
        self.base_url = "https://www.imdb.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Category mapping to IMDb URLs
        self.categories = {
            'action': ('Action', '/search/title/?genres=action&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'comedy': ('Comedy', '/search/title/?genres=comedy&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'drama': ('Drama', '/search/title/?genres=drama&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'horror': ('Horror', '/search/title/?genres=horror&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'romance': ('Romance', '/search/title/?genres=romance&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'thriller': ('Thriller', '/search/title/?genres=thriller&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'sci-fi': ('Sci-Fi', '/search/title/?genres=sci-fi&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'fantasy': ('Fantasy', '/search/title/?genres=fantasy&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'adventure': ('Adventure', '/search/title/?genres=adventure&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'crime': ('Crime', '/search/title/?genres=crime&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'animation': ('Animation', '/search/title/?genres=animation&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'family': ('Family', '/search/title/?genres=family&sort=user_rating,desc&title_type=feature&num_votes=25000,'),
            'top250': ('Top 250', '/chart/top/')
        }
    
    def scrape_movies(self, category, limit=50):
        """Scrape movies from IMDb based on category"""
        if category not in self.categories:
            print(f"Category '{category}' not found!")
            return []
            
        category_name, url_path = self.categories[category]
        url = urljoin(self.base_url, url_path)
        
        print(f"🔍 Scraping {category_name} movies from: {url}")
        
        try:
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            movies = []
            
            # Different scraping logic for different page types
            if category == 'top250':
                movies = self._scrape_top250(soup, limit)
            else:
                movies = self._scrape_search_results(soup, limit, category_name)
            
            print(f"✅ Successfully scraped {len(movies)} movies")
            return movies
            
        except requests.RequestException as e:
            print(f"❌ Network error: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Scraping error: {str(e)}")
            return []
    
    def _scrape_top250(self, soup, limit):
        """Scrape Top 250 movies page"""
        movies = []
        
        # Find movie containers
        movie_containers = soup.find_all('li', class_='titleColumn')
        if not movie_containers:
            movie_containers = soup.find_all('td', class_='titleColumn')
        
        print(f"Found {len(movie_containers)} movie containers in Top 250")
        
        for i, container in enumerate(movie_containers[:limit]):
            try:
                # Extract title and IMDb URL
                title_element = container.find('a')
                title = title_element.text.strip() if title_element else "Unknown Title"
                imdb_url = ""
                if title_element and title_element.has_attr('href'):
                    imdb_id = title_element['href'].split('/')[2] if '/title/' in title_element['href'] else ""
                    imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
                
                # Extract year
                year_element = container.find('span', class_='secondaryInfo')
                year = year_element.text.strip('()') if year_element else "N/A"
                
                # Extract rating (from sibling element)
                rating = "N/A"
                rating_container = container.find_parent('tr')
                if rating_container:
                    rating_element = rating_container.find('td', class_='ratingColumn imdbRating')
                    if rating_element:
                        rating_strong = rating_element.find('strong')
                        rating = rating_strong.text.strip() if rating_strong else "N/A"
                
                movies.append({
                    'rank': i + 1,
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'imdb_url': imdb_url
                })
                
            except Exception as e:
                print(f"⚠️ Error processing movie {i+1}: {str(e)}")
                continue
        
        return movies
    
    def _scrape_search_results(self, soup, limit, category_name):
        """Scrape search results pages"""
        movies = []
        
        # Try different selectors for search results
        movie_containers = soup.find_all('div', class_='lister-item mode-advanced')
        if not movie_containers:
            movie_containers = soup.find_all('div', class_='lister-item-content')
        
        print(f"Found {len(movie_containers)} movie containers in search results")
        
        if not movie_containers:
            # Fallback method
            return self._fallback_scraping(soup, limit)
        
        for i, container in enumerate(movie_containers[:limit]):
            try:
                # Extract title and IMDb URL
                title_element = container.find('h3', class_='lister-item-header')
                title = "Unknown Title"
                imdb_url = ""
                if title_element:
                    title_link = title_element.find('a')
                    title = title_link.text.strip() if title_link else "Unknown Title"
                    if title_link and title_link.has_attr('href'):
                        imdb_id = title_link['href'].split('/')[2] if '/title/' in title_link['href'] else ""
                        imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
                
                # Extract year
                year_element = container.find('span', class_='lister-item-year')
                year = year_element.text.strip('()') if year_element else "N/A"
                
                # Extract rating
                rating = "N/A"
                rating_element = container.find('div', class_='ratings-bar')
                if rating_element:
                    rating_strong = rating_element.find('strong')
                    rating = rating_strong.text.strip() if rating_strong else "N/A"
                
                movies.append({
                    'rank': i + 1,
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'imdb_url': imdb_url
                })
                
            except Exception as e:
                print(f"⚠️ Error processing movie {i+1}: {str(e)}")
                continue
        
        return movies
    
    def _fallback_scraping(self, soup, limit):
        """Fallback scraping method using title links"""
        movies = []
        print("🔄 Using fallback scraping method...")
        
        # Find all title links
        title_links = soup.find_all('a', href=lambda x: x and '/title/tt' in x)
        print(f"Found {len(title_links)} title links")
        
        seen_titles = set()
        for i, link in enumerate(title_links[:limit * 2]):  # Get extra to filter duplicates
            try:
                title = link.get_text(strip=True)
                imdb_url = ""
                if link.has_attr('href'):
                    imdb_id = link['href'].split('/')[2] if '/title/' in link['href'] else ""
                    imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
                if title and title not in seen_titles and len(title) > 2:
                    seen_titles.add(title)
                    # Try to find rating in parent elements
                    rating = self._find_nearby_rating(link)
                    movies.append({
                        'rank': len(movies) + 1,
                        'title': title,
                        'year': 'N/A',
                        'rating': rating,
                        'imdb_url': imdb_url
                    })
                    if len(movies) >= limit:
                        break
            except Exception as e:
                continue
        
        return movies
    
    def _find_nearby_rating(self, link):
        """Try to find rating near a title link"""
        rating = "N/A"
        parent = link.find_parent()
        
        # Look through parent elements for ratings
        for _ in range(5):
            if parent:
                # Look for various rating patterns
                rating_elem = parent.find('span', class_='ratingValue')
                if not rating_elem:
                    rating_elem = parent.find('div', class_='ratings-bar')
                if not rating_elem:
                    rating_elem = parent.find('span', string=lambda text: 
                                            text and '.' in str(text) and len(str(text)) < 5)
                
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    # Basic validation for rating format
                    if rating_text and ('.' in rating_text) and len(rating_text) < 6:
                        rating = rating_text
                        break
                
                parent = parent.find_parent()
            else:
                break
        
        return rating

# Test the scraper if run directly
if __name__ == "__main__":
    scraper = IMDbMovieScraper()
    
    print("Testing scraper...")
    test_movies = scraper.scrape_movies('action', limit=5)
    
    if test_movies:
        print(f"\n✅ Test successful! Found {len(test_movies)} movies:")
        for movie in test_movies:
            print(f"{movie['rank']}. {movie['title']} ({movie['year']}) - ⭐ {movie['rating']}")
    else:
        print("❌ Test failed - no movies found")