from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import io

OMDB_API_KEY = open('omdb.cfg').read().strip('\n')

def find_extra_info(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    try: trailer_url = find_trailer(soup)
    except: trailer_url = None
    return trailer_url, find_original_name(soup), find_content_rating(soup)

def find_content_rating(soup):
    contentRating = soup.find(attrs={"itemprop":"contentRating"})
    return contentRating.text

def find_trailer(soup):
    trailer = soup.find(attrs={'class':'video-iframe js-video-iframe'})
    t_url = trailer['data-src']
    trailerUrl = 'http:' + t_url[:t_url.find('?')]
    return trailerUrl

def find_original_name(soup):
    coluna = soup.find(attrs={'class':'column-md-2'})
    bloco  = coluna.find(attrs={'class':'d-block'})
    originalName = bloco.next.next
    originalName = originalName[:originalName.find('\r')]
    return originalName

def omdb(originalName, director):
    p_name = '+'.join(originalName.lower().split()).strip('the+')
    url = 'http://www.omdbapi.com/'
    p_url = url + '?t=%s&apikey=%s' % (p_name, OMDB_API_KEY)
    answer = requests.get(p_url).content
    movie_not_found = {'Response':'False', 'Error':'Movie not found!'}

    try: 
        movie_data = json.loads(answer)

        movie_director = movie_data["Director"].upper().replace(" ","")
        director = director.upper().replace(" ","")

        for key in movie_data.keys():
            try:
                movie_data[key] = movie_data[key].strip()
            except:
                pass
        
        if (director == movie_director):
            return movie_data
        return movie_not_found

    except: 
        return movie_not_found

def build_dict(old_dict):
    n = {}
    n['title'] = old_dict['nome']
    n['movieOutline'] =  old_dict['description'].strip('\n')
    n['director'] = old_dict['director']
    n['ticket'] = old_dict['ticket']
    n['countryOfOrigin'] = old_dict['countryOfOrigin']
    n['contentRating'] = old_dict['contentRating']
    n['originalTitle'] = old_dict['originalName']
    n['trailer'] = old_dict['trailer']
    n['poster'] = old_dict['image']
    try:
        n['production'] = old_dict['omdb']['Production']
        n['ratings'] = old_dict['omdb']['Ratings']
        for i in range(len(n['ratings'])):
            d = {}
            if n['ratings'][i]['Source'] == "Internet Movie Database":
                d['source'] = 'IMDb'
            else:
                d['source'] = n['ratings'][i]['Source']
            d['value'] = n['ratings'][i]['Value']
            n['ratings'][i] = d
        n['writer'] = old_dict['omdb']['Writer']
        n['actors'] = old_dict['omdb']['Actors']
        n['website'] = old_dict['omdb']['Website']
        n['genre'] = old_dict['omdb']['Genre']
        n['language'] = old_dict['omdb']['Language']
        n['runtime'] = old_dict['omdb']['Runtime']
        n['imdbID'] = old_dict['omdb']['imdbID']
        n['year'] = old_dict['omdb']['Year']
    except:
        pass
    return n


def main(parameter=''):

    url = 'https://www.ingresso.com/rio-de-janeiro/home/filmes/' + parameter
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    filmes = soup.find_all(attrs={'class':'card ing-small'})
    d_filmes = []

    for filme in filmes:

        d_filme = {}

        atributos = filme.find_all("meta")
        for atributo in atributos:
            descricao = atributo['itemprop']
            d_filme[descricao] = atributo['content']

        compra = filme.find(attrs={"class":"d-block"})
        
        d_filme['ticket'] = 'https://www.ingresso.com' + compra['href']
        d_filme['trailer'], d_filme['originalName'], d_filme['contentRating'] = find_extra_info(d_filme['ticket'])
        d_filme['omdb'] = omdb(d_filme['originalName'], d_filme['director'])

        for key in d_filme.keys():
            try: d_filme[key] = d_filme[key].strip(' ')
            except: pass

        sleep(1)
        
        d_filme['nome'] = filme.find(attrs={"class":"card-title"}).text.strip(' ')

        if requests.get(d_filme['image']).content == 'File not found."':
            pass
        else: 
            d_filmes.append(build_dict(d_filme))
        #return d_filmes # para uso em testes! 

    return d_filmes

if __name__ == "__main__":
    filmes_em_cartaz = main(parameter='em-cartaz')
    filmes_em_breve  = main(parameter='em-breve')
    filmes = filmes_em_cartaz + filmes_em_breve
    json.dump(filmes, open('filmes.json', 'w'), indent=4) # , ensure_ascii=False)
