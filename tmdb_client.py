import requests
import json
import os

API_KEY = "d8475f462df4b0b62d65d5016fca82d9"
BASE_URL = "https://api.themoviedb.org/3"

SESSION_FILE = "session_id.txt"
RATED_MOVIES_FILE = "rated_movies.json"

def get_session_id():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as file:
            session_id = file.read().strip()
            print("Sessão carregada com sucesso!")
            return session_id

    request_token = create_request_token()
    if request_token:
        print("Autorize o token no navegador e pressione Enter para continuar:")
        print(f"https://www.themoviedb.org/authenticate/{request_token}")
        input()
        session_id = create_session(request_token)
        if session_id:
            with open(SESSION_FILE, 'w') as file:
                file.write(session_id)
            return session_id
    return None

def save_rated_movie(movie_id, movie_title, rating):
    rated_movies = load_rated_movies()
    rated_movies[movie_id] = {"title": movie_title, "rating": rating}
    with open(RATED_MOVIES_FILE, 'w') as file:
        json.dump(rated_movies, file)

def load_rated_movies():
    if os.path.exists(RATED_MOVIES_FILE):
        with open(RATED_MOVIES_FILE, 'r') as file:
            return json.load(file)
    return {}

def show_rated_movies():
    rated_movies = load_rated_movies()
    if rated_movies:
        print("\nFilmes já avaliados:")
        for movie_id, details in rated_movies.items():
            print(f"Título: {details['title']}, Nota: {details['rating']}")
    else:
        print("\nNenhum filme avaliado ainda.")

def get_movie_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for video in data['results']:
            if video['site'] == "YouTube" and video['type'] == "Trailer":
                trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                return trailer_url
    return "Trailer não disponível."

def search_movie(movie_title):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": movie_title,
        "language": "pt-BR"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("\nResultados da busca:")
        for index, movie in enumerate(data['results'], start=1):
            print(f"{index}. Título: {movie['title']}")
            print("   Data de lançamento:", movie['release_date'])
            print("   Descrição:", movie['overview'])
            trailer_url = get_movie_trailer(movie['id'])
            print("   Trailer:", trailer_url)
            print("-" * 40)
        return data['results']
    else:
        print("Erro ao buscar dados:", response.status_code)
        return None

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": "pt-BR"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print("\nFilmes populares:")
        for movie in data['results']:
            print("Título:", movie['title'])
            print("Data de lançamento:", movie['release_date'])
            trailer_url = get_movie_trailer(movie['id'])
            print("Trailer:", trailer_url)
            print("-" * 40)
    else:
        print("Erro ao buscar dados:", response.status_code)

def create_request_token():
    url = f"{BASE_URL}/authentication/token/new"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200:
        print("Request Token obtido com sucesso!")
        return data["request_token"]
    else:
        print("Erro ao obter Request Token:", response.status_code)
        return None

def create_session(request_token):
    url = f"{BASE_URL}/authentication/session/new"
    params = {"api_key": API_KEY}
    payload = {"request_token": request_token}
    response = requests.post(url, params=params, json=payload)
    data = response.json()
    if response.status_code == 200:
        print("Sessão criada com sucesso!")
        return data["session_id"]
    else:
        print("Erro ao criar sessão:", response.status_code)
        return None

def rate_movie(movie_id, movie_title, rating):
    session_id = get_session_id()
    if not session_id:
        print("Erro: Sessão não encontrada.")
        return

    url = f"{BASE_URL}/movie/{movie_id}/rating"
    params = {"api_key": API_KEY, "session_id": session_id}
    payload = {"value": rating}
    response = requests.post(url, params=params, json=payload)
    if response.status_code == 201:
        print("Avaliação enviada com sucesso!\n")
        save_rated_movie(movie_id, movie_title, rating)
    else:
        print("Erro ao avaliar o filme:", response.status_code)

def main():
    while True:
        print("Bem-vindo ao cliente TMDB!")
        print("Escolha uma opção:")
        print("1. Buscar filme por título")
        print("2. Ver filmes populares")
        print("3. Avaliar um filme")
        print("4. Ver filmes avaliados")

        choice = input("Digite o número da sua escolha: ")

        if choice == "1":
            movie_title = input("Digite o título do filme que deseja buscar: ")
            search_movie(movie_title)
        elif choice == "2":
            get_popular_movies()
        elif choice == "3":
            movie_title = input("Digite o título do filme que deseja avaliar: ")
            movies = search_movie(movie_title)
            if movies:
                try:
                    movie_choice = int(input("Escolha o número do filme que deseja avaliar: "))
                    selected_movie = movies[movie_choice - 1]
                    rating = float(input("Digite a nota que deseja dar ao filme (de 0.5 a 10.0): "))
                    rate_movie(selected_movie['id'], selected_movie['title'], rating)
                except (IndexError, ValueError):
                    print("Escolha inválida. Tente novamente.")
        elif choice == "4":
            show_rated_movies()
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
