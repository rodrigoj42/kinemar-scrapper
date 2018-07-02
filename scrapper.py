from bs4 import BeautifulSoup
import json
import requests

OMDB_API_KEY = open('omdb.cfg').read().strip('\n')

def main(parameter=''):
    url = 'https://api-content.ingresso.com/v0/templates/'
    page = requests.get(url+parameter).content
    filmes = json.loads(page)
    for i in range(len(filmes)):
        filme = filmes[i]
        filmes[i]['omdb'] = omdb_search(filme)
        filmes[i]['RT'] = get_rt_data(filme['originalTitle'])
    return build_final_json(filmes)

def omdb_search(filme):
    title = filme['originalTitle'].strip('The').strip('\n').strip(' ')
    p_title = '+'.join(title.lower().split())
    url = 'http://www.omdbapi.com/'
    p_url = url + '?t=%s&apikey=%s' % (p_title, OMDB_API_KEY)
    try:
        answer = requests.get(p_url).content
        omdb_data = json.loads(answer)
        if match(omdb_data['Director'], filme['director']):
            return omdb_data
        else:
            return None
    except:
        pass
    return None

def match(a, b):
    a = a.lower().replace(' ','')
    b = b.lower().replace(' ','')
    return a == b
    
def get_rt_data(originalName):
    try:
        rtname = '_'.join(originalName.lower().split())
        url = 'https://www.rottentomatoes.com/m/'
        page = requests.get(url + rtname).content
        soup = BeautifulSoup(page, 'html.parser')
        critics  = soup.find(attrs={'class':'meter-value superPageFontColor'}).text
        audience = soup.find(attrs={'class':'meter media'}).find(attrs={'class':'superPageFontColor'}).text
        return critics, audience
    except:
        return None

def build_final_json(filmes):
    formatados = []
    for filme in filmes:
        formatado = {}
        formatado['poster'] = get_poster(filme)
        if not formatado['poster']:
            continue

        formatado['movieID'] = filme['id']
        formatado['title'] = filme['title']
        formatado['originalTitle'] = filme['originalTitle']
        formatado['movieOutline'] = filme['synopsis']
        formatado['director'] = filme['director']
        formatado['ticket'] = filme['siteURL']
        formatado['contentRating'] = filme['contentRating']
        formatado['isPlaying'] = filme['isPlaying']
        formatado['runtime'] = filme['duration']
        try:
            formatado['premiereYear'] = filme['premiereDate']['year']
            formatado['premiereDate'] = filme['premiereDate']['dayAndMonth']
        except:
            pass
        try:
            formatado['production'] = filme['omdb']['Production']
            formatado['countryOfOrigin'] = filme['omdb']['Production']
            formatado['writer'] = filme['omdb']['Writer']
            formatado['actors'] = filme['omdb']['Actors']
            formatado['website'] = filme['omdb']['Website']
            formatado['language'] = filme['omdb']['Language']
            formatado['imdbID'] = filme['omdb']['imdbID']
        except:
            pass
        formatado['genre'] = get_genre(filme)
        formatado['trailer'] = get_trailer_id(filme)
        formatado['rating'] = build_ratings(filme)
        for k in formatado:
            try:
                formatado[k] = formatado[k].strip('\n').strip(' ')
            except: 
                pass
        formatados.append(formatado)
    return formatados

def get_poster(filme):
    for poster in filme['images']:
        if poster['type'] == "PosterPortrait":
            return poster['url']
    return None

def build_ratings(filme):
    try:
        critics, audience = filme['RT']
        for rating in filme['omdb']['Ratings']:
            if rating['Source'] == 'Internet Movie Database':
                imdb = rating['Value']
            if rating['Source'] == 'Metacritic':
                metacritic = rating['Value']
        ratings = [ {'source':'Rotten Tomatoes Audience','value':audience}, \
        {'source':'Rotten Tomatoes Critics','value':critics}, \
        {'source':'Metacritic','value':metacritic}, \
        {'source':'IMDb','value':imdb} ]
        return ratings
    except:
        return []

def get_genre(filme):
    genres = filme['genres']
    return ', '.join(genres)

def get_trailer_id(filme):
    try:
        url = filme['trailers'][0]['embeddedUrl']
        trailerID = url.split()[-1]
        return trailerID
    except:
        return None

if __name__ == '__main__':
    em_cartaz = main('nowplaying')
    em_breve = main('soon')
    filmes = em_cartaz + em_breve
    json.dump(filmes, open('filmes.json', 'w'), indent=4)
