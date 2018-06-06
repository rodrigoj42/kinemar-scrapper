from bs4 import BeautifulSoup
from time import sleep
import requests
import json

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
        print d_filme['originalName']
        sleep(1)
        nome = filme.find(attrs={"class":"card-title"}).text
        d_filmes[nome] = d_filme

    return d_filmes

if __name__ == "__main__":
    filmes_em_cartaz = main(parameter='em-cartaz')
    json.dump(filmes_em_cartaz, open('emcartaz.json', 'w'))
    filmes_em_breve  = main(parameter='em-breve')
    json.dump(filmes_em_breve, open('embreve.json', 'w'))
