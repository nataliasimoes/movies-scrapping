import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from textblob import TextBlob
from datetime import datetime


data_atual = datetime.now()
data_formatada = data_atual.strftime("%d_%m")

# Natal Shopping
link_natal_shopping = f"https://www.natalshopping.com.br/cinema#data_{data_formatada}"

# Cinemark - Midway Mall
link_midway = f"https://www.cinemark.com.br/natal/cinemas"

# Natal Praia Shopping
link_natal_praia = f"https://www.adorocinema.com/programacao/cinema-F0331/d-3/"



# Natal Shopping Scraping
# Dicionário para armazenar os filmes em cartaz, cada filme contem o título, gêneros e a imagem

movies_natal_shopping = []

response_natal_shopping = requests.get(link_natal_shopping)


if response_natal_shopping.status_code == 200: 
    html_content = response_natal_shopping.content
    soup = BeautifulSoup(html_content, 'html.parser')
    div_movies_natal_shopping = soup.find('ul', class_='tab cinemaSecoesList')
    movies_natal_shopping_list = div_movies_natal_shopping.find_all('li', class_='filme noDot')

    for movie in movies_natal_shopping_list:
        try:
            movie_img_div = movie.find('div', class_='imgLazyLoad')
            movie_img = movie_img_div['data-img']
            movie_content = movie.find('div', class_='wrapContent')
            movie_title = movie_content.find('h3').get_text(strip=True)
            movie_tags_div = movie_content.find('div', class_='tags')
            generos_li = movie_tags_div.find_all('li', class_='genero')
            movie_generos = [genero.text.strip() for genero in generos_li]
            movie_duration = movie_tags_div.find('li', class_='time noDot').text.strip()
            movie_times_div = movie.find(class_='secoes clear')
            movie_times = movie_times_div.find_all('a')
            movie_times = [time.text.strip() for time in movie_times]
            # Add movie to list
            movies_natal_shopping.append({
                'title': movie_title,
                'generos': movie_generos,
                'img': movie_img,
                'duration': movie_duration,
                'times': movie_times
            })
        except:
            print("Error getting movie data")
            continue
else:
    print("Error connecting to the website, status: " + str(response_natal_shopping.status_code)) 
    movies_natal_shopping = []

print("Movies Natal Shopping")
print(movies_natal_shopping)
print("")
print("-----------------------------------------")

# Cinemark - Midway Mall Scraping
# Dicionário para armazenar os filmes em cartaz, cada filme contem o título e os horários

movies_midway = []

response_midway = requests.get(link_midway)

if response_midway.status_code == 200: 
    html_content = response_midway.content
    soup = BeautifulSoup(html_content, 'html.parser')
    div_movies_active = soup.find('div', class_='tabs-content')
    div_movies_midway = div_movies_active.find('div', class_='active')
    movies_midway_list = div_movies_midway.find_all('div', class_='theater')

    for movie in movies_midway_list:
        try:
            movie_title_div = movie.find('div', class_='theater-header')
            movie_title = movie_title_div.find('h3').get_text(strip=True)
            movie_times_ul = movie.find('ul', class_='times-options')
            movie_times = movie_times_ul.find_all('span')
            movie_times = [time.text.strip() for time in movie_times]
            movies_midway.append({
                'title': movie_title,
                'times': movie_times
            })
        except:
            print("Error getting movie data")
            continue

print("Movies Midway")
print(movies_midway)
print("")
print("-----------------------------------------")

# Natal Praia Shopping Scraping
# Dicionário para armazenar os filmes em cartaz, cada filme contem o título, gêneros e a imagem

movies_natal_praia = []

response_natal_praia = requests.get(link_natal_praia)

if response_natal_praia.status_code == 200:
    html_content = response_natal_praia.content
    soup = BeautifulSoup(html_content, 'html.parser')
    div_movies_natal_praia = soup.find('div', class_='showtimes-list-holder')
    movies_natal_praia_list = div_movies_natal_praia.find_all('div', class_='movie-card-theater')
    
    for movie in movies_natal_praia_list:
        try: 
            movie_title = movie.find('h2', class_='meta-title').get_text(strip=True)
            movie_img = movie.find('img')
            # Em algumas páginas o atributo src não está completo, então é necessário verificar se começa com https
            if movie_img  and movie_img['src'].startswith('https'):
                movie_img = movie_img['src']
            else:
                movie_img = movie_img['data-src']
            movie_times = movie.find_all('span', class_='showtimes-hour-item-value')
            movie_times = [time.text.strip() for time in movie_times]
            movies_natal_praia.append({
                'title': movie_title,
                'img': movie_img,
                'times': movie_times
            })
        except:
            print("Error getting movie data")
            continue

print("Movies Natal Praia")  
print(movies_natal_praia)
print("")
print("-----------------------------------------")
        
    

        
