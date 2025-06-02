from httpx import get
import requests
from bs4 import BeautifulSoup
from googlesearch import search


def internet_search(query):
    """
    Searches the internet for a query.
    Returns top 5 results.
    Args:
        query (str): The query to search for.
    """
    urls = search(query, num_results=5)
    urls_detailed = []

    for url in urls:
        info = fetch_url_info(url)
        if info:
            urls_detailed.append(info)

    return urls_detailed

def read_website(url):
    """
    Reads and returns the body of the website at the given url.
    Args:
        url (str): The url of the website to read.
    Returns:
        str: The body of the website.
        None: If the request fails.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.body
        body_text = body.get_text(strip=True)
        return body_text        
    else:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None
    
    
def fetch_url_info(url):
    """
    Fetches the description and title of the website at the given url.
    Args:
        url (str): The url of the website to read.
    
    Returns:
        dict: A dictionary containing the url, title and description of the website.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers,timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text if soup.find('title') else 'No title found'
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else 'No description found'
            return {"url": url, 'title': title, 'description': description}
        else:
            return None
    except Exception as e:
        return None

def weather(city):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            country = data['nearest_area'][0]['country'][0]['value']
            region = data['nearest_area'][0]['region'][0]['value']
            description = current['weatherDesc'][0]['value']
            temperature = current['temp_C']
            humidity = current['humidity']
            wind_speed = current['windspeedKmph']
            feels_like = current['FeelsLikeC']
            return {
                "description": description,
                "temperature_C": temperature,
                "feels_like_C": feels_like,
                "humidity_percent": humidity,
                "wind_kmph": wind_speed,
                "country": country,
                "region": region
            }
        else:
            return {"error": "Could not fetch weather data."}
    except Exception as e:
        return {"error": str(e)}
