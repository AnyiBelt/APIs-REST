import requests
from flask import Flask, request

app = Flask(__name__)

# Llamamos el cliente de spotify
SPOTIFY_CLIENT_ID = "c8399ac35efd438db08d7f313436506c"
SPOTIFY_CLIENT_SECRET = "c64889d2ed9a4682ad9df24c86353bf6"

# Variable global de usuarios que no esta iniciañizada he iremos llenando con el metodo post
USER = []

# Funciones axuliares de spotify api

def obtener_token_spotify():
    url="https://accounts.spotify.com/api/token"
    auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    data={"grant_type":"client_credentials"}
    
    respuesta=requests.post(url,auth=auth,data=data)
    if respuesta.status_code == 200:
        return respuesta.json().get("access_token")
    return None

@app.route("/buscar-cancion/<nombre>",methods=["GET"])
def buscar_cancion(nombre):
    """Busca cancion en la api real de spotify"""
    token=obtener_token_spotify()
    if not token:
        return{"message":"No se pudo obtener token de Spotify"},500
    
    url=f"https://api.spotify.com/v1/search?q={nombre}&type=track&limit=1"
    headers={'Authorization':f"Bearer {token}"}
    
    respuesta= requests.get(url, headers=headers)
    return respuesta.json(), respuesta.status_code

#Ruta para saber si hay usuarios en la base de datos
@app.route("/users" , methods=["GET"])
def obtener_usuarios():
    
    #check how many users are in the list
    cantidad_usuarios=len(USER)
    
    if cantidad_usuarios == 0:
        return{'message':'No hay usuarios en la base de datos'}, 400
    return{"users": USER}, 200

#Ruta para agregar usuarios
@app.route("/adduser",methods=["POST"])
def add_user():
    global USER
    
    new_users=request.get_json().get("users",[])
    for new_user in new_users:
        if 'id' not in new_user or 'nombre' not in new_user:
            return{'message':'datos del usuario invalidos'},400
        if any (user ["id"] == new_user['id'] for user in USER):
            return{ 'message': f'Usuario con ID {new_user["id"]} ya existe'}, 409
        
    USER.extend(new_users)
    
    return { 'message':'Usuario agregado correctamente',
            'nombres de los usuarios':[user["nombre"] for user in new_users]}, 201

@app.route("/users/<int:user_id>/canciones", methods=["POST"])
def agregar_cancion_favorita(user_id):
    global USER
    
    #leer el JSON que nos envia postman
    datos=request.get_json()
    nombre_cancion=datos.get("cancion") if datos else None
    
    if not nombre_cancion:
        return{
            "message":"Debes proporcionar el nombre de la canción en el JSON"
            },400
    
    #verificamos si hay usuarios en el array para agregar canciones
    usuario_encontrado=None
    for user in USER:
        if user["id"]==user_id:
            usuario_encontrado=user
            break;
    if not usuario_encontrado:
        return{ "message": f"el usuario con id {user_id} no existe en la base de datos"}, 400
    
    #Buscar la cancion en Spotify
    token = obtener_token_spotify()
    if not token: 
        return { 
                "message":"No se pudo conectar con Spotify"
                }, 500
    url_spotify=f"https://api.spotify.com/v1/search?q={nombre_cancion}&type=track&limit=1"
    headers={'Authorization':f"Bearer {token}"}
    respuesta_spotify= requests.get(url_spotify, headers=headers)
    
    if respuesta_spotify.status_code !=200:
        return { 
                "message":"Error al consultar la API de Spotify"
                },500
    
    items= respuesta_spotify.json().get("tracks",{}).get("items",[])
    if not items:
        return {
            "message":f"no se encontro nombre de la cancion '{nombre_cancion} en spotify'"
        }, 400

    
    #Extraemos solo los datos limpios que nos interesan de Spotify
    track=items[0]
    cancion_info={
        "nombre": track["name"],
        "artista": track["artists"][0]["name"],
        "album": track["album"]["name"],
        "link_spotify":track["external_urls"]["spotify"]
    }
    
    #buscar el usuario por ID en nuestra lista de usuarios
    for user in USER:
        if user['id'] == user_id:
            #Si el usuario no tiene un espacio en su array para canciones se lo agregamos como una lista vacia
            if "canciones_favoritas" not in user:
                user["canciones_favoritas"] = []
            
            #agregamos la cancion a la lista del usuario
            user["canciones_favoritas"].append(cancion_info)
            
            return{
                "message": f"se ha agregado la cancion: '{nombre_cancion}' con exito al usuario: '{user['nombre']}'"
            }, 200
    return {"message":"usuario no encontrado"},400
    
@app.route("/deleteusers" , methods=["DELETE"])
def delete_user():
    global USER
    # extraer datos enviado al json
    datos=request.get_json()
    user_id= datos.get("id") if datos else None
    
    #se valida el id
    if user_id is None:
        return{ 'message': "No a ingresado un ID para eliminar usuario, porfavor ingresa el 'id' del usuario a eliminar"},400
    
    #Se recorre la lista con el id obtenido en el Json
    for posicion, user in enumerate(USER):
        if user["id"] == user_id:
            usuario_eliminado=USER.pop(posicion)
            return{
                'message': f"Usuario '{usuario_eliminado['nombre']}' con ID {usuario_eliminado['id']} ha sido eliminado correctamente",
                'user_deleted': usuario_eliminado
            }, 200
    return {'message': f'No se encontró ningun usuario con el ID {user_id}'},400

@app.route("/users/<int:id>" , methods=["PUT"])
def update_user(id):
    global USER
    datos = request.get_json()
    for user in USER:
        if user["id"] == id:
            user.update(datos) 
            return{'message':"Usuario actualizado correctamente","user":user}, 200
    
    return { 'message':"Usuario no encontrado"}, 404

if __name__ == "__main__":
    app.run(debug=True)
    