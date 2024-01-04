import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from textblob import TextBlob
from datetime import datetime
from googletrans import Translator

#App
app = Dash(__name__)

def traduzir_para_ingles(texto):
    translator = Translator()
    traducao = translator.translate(texto, src='pt', dest='en')
    return traducao.text

def calcular_polaridade(frase):
    text_eng = traduzir_para_ingles(frase)
    blob = TextBlob(text_eng)
    polaridade = float(f"{blob.sentiment.polarity:.2f}")
    return polaridade

data_atual = datetime.now()
data_formatada = data_atual.strftime("%d_%m")

# Natal Shopping
link_natal_shopping = f"https://www.natalshopping.com.br/cinema#data_{data_formatada}"

# Cinemark - Midway Mall
link_midway = f"https://www.cinemark.com.br/natal/cinemas"

# Natal Praia Shopping
link_natal_praia = f"https://www.adorocinema.com/programacao/cinema-F0331/"

# Array com os horários
horarios = []

# Natal Shopping Scraping
# Dicionário para armazenar os filmes em cartaz, cada filme contem o título, gêneros, imagem, duração e horário

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
            movie_description = movie_content.find('p', class_='sinopse').get_text(strip=True)
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
                'description': movie_description,
                'generos': movie_generos,
                'img': movie_img,
                'duration': movie_duration,
                'times': movie_times
            })
            horarios.append(movie_times)
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
            horarios.append(movie_times)
        except:
            print("Error getting movie data")
            continue

print("Movies Midway")
print(movies_midway)
print("")
print("-----------------------------------------")

# Natal Praia Shopping Scraping
# Dicionário para armazenar os filmes em cartaz, cada filme contem o título, horário e a imagem

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
            movie_description = movie.find('div', class_='content-txt').get_text(strip=True)
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
                'description': movie_description,
                'img': movie_img,
                'times': movie_times
            })
            horarios.append(movie_times)
        except:
            print("Error getting movie data")
            continue

print("Movies Natal Praia")  
print(movies_natal_praia)
print("")
print("-----------------------------------------")
          
horarios_aplanados = [horario for sublist in horarios for horario in sublist]
# GRAFICOS
# Contagem de ocorrências de cada horário
contagem_horarios = {horario: horarios_aplanados.count(horario) for horario in set(horarios_aplanados)}

# Criar gráfico de pizza
fig1 = px.pie(
    values=list(contagem_horarios.values()),
    names=list(contagem_horarios.keys()),
    title='Distribuição de Horários',
    hole=0.2  # Define o tamanho do buraco no meio do gráfico (0.4 = 40%)
)

#------------------------------------Dashboard-----------------------------------------

app.layout = html.Div([
    html.H1(
        children="Dashboard"
    ),
    html.H2(
        children="Tema escolhido"
    ),
    html.P(
        className='texto',
        children='Raspagem de dados'
    ),
    html.H2(
        children="Explicação do Problema"
    ),
    html.P(
        className='texto',
        children='Em um mercado é normal e comum a existência de concorrência, isso é saudável para o mercado. No mercado de cinema isso não é diferente, e por ser um mercado com novos produtos (filmes) regularmente, decidimos usar a raspagem de dados para coletar informações sobre os filmes em cartaz em alguns cinemas de natal.'
    ),
    html.P(
        className='texto',
        children='A raspagem de dados é uma técnica computacional para extração de informações a partir de fontes públicas como sites, um serviço online ou um aplicativo por exemplo. Ao requisitar o conteúdo da fonte, esse documento passa por um processo que tem como objetivo achar um padrão específico de dados e após este processo estes dados são transformados no formato de dado desejado, em nosso trabalho usamos a biblioteca do Python: BeautifulSoup para extrair e encontrar os dados e depois armazenamos as informações de cada cinema como objetos json.'
    ),
    html.H2(
        children="Apresentação da técnica desenvolvida"
    ),
    html.P(
        className='texto',
        children='Para apresentar os dados será utilizada a biblioteca Dash do Python. O Dash é a estrutura low-code original para criar rapidamente aplicativos de dados em Python. Com eal é possível criar um layout que poderá ajudar na analise dos dados coletados através da raspagem.'
    ),
    html.Hr(),
    html.Div(
        className='session-one',
        children=[
            html.H3(children='Natal Shopping'),
            html.Div(
                className='movie-cards',
                children=[
                    html.Div(
                        className='card',
                        children=[
                            html.Img(src=movie['img']),
                            html.P(className='movie-title',children=movie['title']),
                            html.P(className='movie-polaridade', children=[
                                'Polaridade: ',
                                calcular_polaridade(movie['description'])
                            ]),
                            html.P(className='movie-genre',children=[
                                html.Span(className='genre-item', children=genre) for genre in movie['generos']
                            ]),
                            html.P(className='movie-duration',children=movie['duration']),
                            html.P(className='movie-times',children=[
                                html.Span(className='times-item', children=time) for time in movie['times']
                            ]),
                            html.P(className='movie-desc', children=movie['description'])
                        ]
                    ) for movie in movies_natal_shopping[:4]
                ] if movies_natal_shopping else html.P(className='no-movie', children='Não há nehuma programação hoje para este cinema!')
            ) 
        ] 
    ),
    html.Hr(),
    html.Div(
        className='session-two',
        children=[
            html.H3(children='Cinemark - Midway Mall'),
            html.Div(
                className='movie-cards',
                children=[
                    html.Div(
                        className='card',
                        children=[
                            html.P(className='movie-title',children=movie['title']),
                            html.P(className='movie-times',children=[
                                html.Span(className='times-item', children=time) for time in movie['times']
                            ]),
                        ]
                    ) for movie in movies_midway[:4]
                ] if movies_midway else html.P(className='no-movie', children='Não há nehuma programação hoje para este cinema!')
            )
        ]
    ),
    html.Hr(),
    html.Div(
        className='session-three',
        children=[
            html.H3(children='Natal Praia Shopping'),
            html.Div(
                className='movie-cards',
                children=[
                    html.Div(
                        className='card',
                        children=[
                            html.Img(src=movie['img']),
                            html.P(className='movie-title',children=movie['title']),
                            html.P(className='movie-polaridade', children=[
                                'Polaridade: ',
                                calcular_polaridade(movie['description'])
                            ]),
                            html.P(className='movie-times',children=[
                                html.Span(className='times-item', children=time) for time in movie['times']
                            ]),
                            html.P(className='movie-desc', children=movie['description'])
                        ]
                    ) for movie in movies_natal_praia[:4]
                ] if movies_natal_praia else html.P(className='no-movie', children='Não há nehuma programação hoje para este cinema!')
            )
        ]
    ),
    html.H2(
        children='Gráficos e análises'
    ),
    dcc.Graph(
        figure= fig1
    ),
    html.H2(
        children="Conclusão"
    ),
    html.P(
        className='texto',
        children='A partir das análises do gráfico e dos dados dos cinemas organizados de forma a comparar, foi possível concluir quanto a Horário: que existe uma grande variedade de horários e que alguns dos cinemas disponibilizam mais horários para um mesmo filme que os outros. Gênero: nem todos os sites disponibilizam essa informação, o que pode dificultar na em outras possíveis analises. Cartazes/imagens: foi possível ver que os filmes em cartaz aparecem em mais de um cinema e que a maior parte dos filmes é igual nos cinemas analisados, além de que as imagens de cartaz podem ser diferentes para cada um. Por fim, assim como os gênero, a Descrição pode ou não ser disponibilizada por alguns dos cinemas, além de que as descrições ou sinopses podem variar de um site para o outro, e com base na polaridade extraida das descrições, essas podem influênciar em como o filme pode ser visto ou interpretado a partir desta.'
    ),
    html.P(
        className='autors',
        children='Made with ❤️ by André e Natália. 2024'
    )
])

#Rodar o app
if __name__ == '__main__':
    app.run(debug=True)