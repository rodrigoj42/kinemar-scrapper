from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import io

OMDB_API_KEY = open('omdb.cfg').read().strip('\n')

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def find_extra_info(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    try: trailer_url = find_trailer(soup)
    except: trailer_url = None
    return trailer_url, find_original_name(soup)

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
    p_name = '+'.join(originalName.lower().split())
    url = 'http://www.omdbapi.com/'
    p_url = url + '?t=%s&apikey=%s' % (p_name, OMDB_API_KEY)
    answer = requests.get(p_url).content
    movie_not_found = {'Response':'False', 'Error':'Movie not found!'}

    try: 
        movie_data = json.loads(answer)

        movie_director = movie_data["Director"].upper().replace(" ","")
        director = director.upper().replace(" ","")

        for key in movie_data.keys():
            movie_data[key] = movie_data[key].strip()
        
        if (director == movie_director):
            return movie_data
        return movie_not_found

    except: 
        return movie_not_found

def main(parameter=''):

    url = 'https://www.ingresso.com/rio-de-janeiro/home/filmes/' + parameter
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    filmes = soup.find_all(attrs={'class':'card ing-small'})
    d_filmes = {}

    for filme in filmes:

        d_filme = {}

        atributos = filme.find_all("meta")
        for atributo in atributos:
            descricao = atributo['itemprop']
            d_filme[descricao] = atributo['content']

        compra = filme.find(attrs={"class":"d-block"})
        
        d_filme['ticket'] = 'https://www.ingresso.com' + compra['href']
        d_filme['trailer'], d_filme['originalName'] = find_extra_info(d_filme['ticket'])
        d_filme['omdb'] = omdb(d_filme['originalName'], d_filme['director'])

        for key in d_filme.keys():
            try: d_filme[key] = d_filme[key].strip(' ')
            except: pass

        sleep(1)
        
        nome = filme.find(attrs={"class":"card-title"}).text.strip('\n')
        print nome
        d_filmes[nome] = d_filme

    return d_filmes

if __name__ == "__main__":
    filmes_em_cartaz = main(parameter='em-cartaz')
    filmes_em_breve  = main(parameter='em-breve')
    filmes = merge_two_dicts(filmes_em_breve, filmes_em_cartaz)
    json.dump(filmes, open('filmes.json', 'w'), indent=4) # , ensure_ascii=False)
