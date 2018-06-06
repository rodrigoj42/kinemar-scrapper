import json 
import requests 

# ISSO TÁ INCOMPLETO/NÃO FUNCIONANDO

contents = json.load(open('Contents.json'))

# posterSize = 68.58x101.6 (cm) 

def build_ar_reference():
    os.system('mkdir %s' % folder_name)
    os.system('cd %s' % folder_name)
    with picture as f:
        f.write(data)
    os.system('cd ..')
    pass

def build_resource_group(lista):
    for i in lista:
        build_ar_reference(i)
    build_contents()

def download_posters(jsonFileAddr):
    filmes = json.load(jsonFileAddr)
    l_filmes = filmes.keys()
    for filme in l_filmes:
        cartaz = request.get(filmes[filme]['image'])
        with open(filme + '.jpg', 'wb') as f:
            f.write(cartaz.content)
