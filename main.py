import requests
from bs4 import BeautifulSoup
import json


def obter_links_musicas(playlist_url):
    # Enviar uma requisição para a página da playlist
    print(f"Buscando na playlist: {playlist_url}")
    response = requests.get(playlist_url)

    if response.status_code != 200:
        print(f"Erro ao acessar a playlist. Status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Procurar pelas músicas dentro da lista
    links = []
    for a_tag in soup.find_all('a', class_='songList-table-songName'):
        # Extrair o link correto da música
        musica_url = a_tag.get('href')
        if musica_url:
            musica_url = f"https://www.letras.mus.br{musica_url}"
            links.append(musica_url)

    print(f"Encontrados {len(links)} links de músicas.")
    return links


def obter_dados_musica(musica_url, id_musica):
    # Enviar requisição para a página da música
    print(f"{id_musica} - Buscando dados da música: {musica_url}")
    response = requests.get(musica_url)

    if response.status_code != 200:
        print(f"Erro ao acessar a música. Status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrair título da música, o cantor, a letra e o compositor
    titulo = soup.find('h1', class_='textStyle-primary')
    cantor = soup.find('h2', class_='textStyle-secondary')
    letra_div = soup.find('div', class_='lyric-original')

    if not titulo or not cantor or not letra_div:
        print(f"Falha ao extrair dados da música {musica_url}.")
        return None

    titulo = titulo.text.strip().title()
    cantor = cantor.text.strip().title()

    # Processar a letra da música para adicionar quebras de linha
    letra = ""
    for p_tag in letra_div.find_all('p'):  # Encontra todos os parágrafos
        paragrafo = p_tag.get_text(separator="\n", strip=True)  # Extrai o texto, separando com '\n'
        letra += paragrafo + "\n\n"  # Adiciona uma quebra de linha extra entre estrofes

    # Substituir <br> por quebras de linha
    letra = letra.replace("<br>", "\n")

    compositor = obtercompositor(soup)

    musica = {
        'id': id_musica,
        'titulo': titulo,
        'cantor': cantor,
        'letra': letra.strip(),  # Remove possíveis quebras extras no final
        'compositor': compositor,
        'categoria': 'None'  # Ajuste conforme necessário para o seu app
    }

    return musica

def obtercompositor(soup):
    compositor_div = soup.find('div', class_='lyric-info-composition')
    if compositor_div:
        compositor = compositor_div.text.strip().replace("Composição: ", "").split(".")[0]
        return compositor
    return None

def salvar_em_json(musicas, arquivo='musicas.json'):
    # Salvar as músicas extraídas em um arquivo JSON
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(musicas, f, ensure_ascii=False, indent=4)


def main():
    playlist_url = input("Digite o link da playlist: ")
    links_musicas = obter_links_musicas(playlist_url)

    musicas = []
    for i, musica_url in enumerate(links_musicas, 1):  # Inicia o ID da música em 1 e incrementa
        musica = obter_dados_musica(musica_url, i)
        if musica:
            musicas.append(musica)

    if musicas:
        salvar_em_json(musicas)
        print(f'{len(musicas)} músicas foram salvas em musicas.json.')
    else:
        print("Nenhuma música foi salva.")


if __name__ == "__main__":
    main()
