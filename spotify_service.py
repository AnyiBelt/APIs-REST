import requests

# Llamamos el cliente de spotify
SPOTIFY_CLIENT_ID = "c8399ac35efd438db08d7f313436506c"
SPOTIFY_CLIENT_SECRET = "c64889d2ed9a4682ad9df24c86353bf6"

# Funciones  de spotify api

def obtener_token_spotify():
    url="https://accounts.spotify.com/api/token"
    auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    data={"grant_type":"client_credentials"}
    
    respuesta=requests.post(url , auth=auth, data=data)
    if respuesta.status_code == 200:
        return respuesta.json().get("access_token")
    return None

def buscar_cancion(nombre_cancion):
    """Busca cancion en la api real de spotify"""
    token=obtener_token_spotify()
    if not token:
        return None, "No se pudo obtener token de Spotify"
    
    url="https://api.spotify.com/v1/search" 
    params = { 
        "q": nombre_cancion, 
        "type": "track", 
        "limit": 1 
    }
    headers = {'Authorization': f"Bearer {token}"}
    
    
    respuesta= requests.get(url, headers=headers,params=params)
    if respuesta.status_code !=200:
            return None,"Error al consultar la API de Spotify"
    
    items= respuesta.json().get("tracks",{}).get("items",[])
    if not items:
        return None, f"no se encontro nombre de la cancion '{nombre_cancion}' en spotify'"
    
    
    track=items[0]
    cancion_info={
        "nombre": track["name"],
        "artista": track["artists"][0]["name"],
        "album": track["album"]["name"],
        "link_spotify":track["external_urls"]["spotify"]
    }
    return cancion_info, None
