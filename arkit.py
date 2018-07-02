import json 
import requests 
import os
from time import sleep

'''Baixa trailers no json gerado e adiciona arquivos no formato pedido pela Apple'''

path = './kinemAR/kinemAR/Assets.xcassets/AR Resources.arresourcegroup/'
contents = json.load(open(path + 'Contents.json'))

width_size = 69

def build_ar_reference(filme):
    name = filme.replace('jpg', 'arreferenceimage')
    if not os.path.exists(path + name):
        os.mkdir(path + name)
    full_path = path + name + '/' 
    os.rename('./posters/' + filme, full_path+filme)
    build_movie_content(filme, full_path)

def build_movie_content(filme, full_path):
    d = {"images" :[ {"idiom" : "universal", "filename" : filme} ], 
         "info" : { "version" : 1, "author" : "xcode" }, 
         "properties": { "width" : width_size, "unit" : "centimeters" }
        }

    json.dump(d, open(full_path+'Contents.json', 'w'), indent=2)

def build_contents():
    container = { "info": { "version": 1, "author": "xcode"},
            "resources" : []}
    for p in os.listdir(path): 
        if p.split('.')[-1] == 'arreferenceimage':
            container["resources"].append({"filename":p})
    json.dump(container, open(path+'Contents.json', 'w'), indent=2)

def build_resource_group():
    for filme in os.listdir('./posters'):
        build_ar_reference(filme)
    build_contents()

def download_posters_in(jsonFileAddr):
    if not os.path.exists('posters'):
        os.mkdir('posters')
    with open(jsonFileAddr) as jsonFile:
        l_filmes = json.load(jsonFile)
    for filme in l_filmes:
        cartaz = requests.get(filme['poster'])
        with open('posters/' + filme['title'] + '.jpg', 'wb') as f:
            f.write(cartaz.content)
        sleep(1)

if __name__ == "__main__":
    download_posters_in('filmes.json')
    build_resource_group()
