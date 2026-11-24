from flask import Flask, request
from spotify_service import buscar_cancion

app = Flask(__name__)

# Variable global de usuarios que no esta inicializada he iremos llenando con el metodo post
USER = []

#Ruta para saber si hay usuarios en la base de datos
@app.route("/users" , methods=["GET"])
def obtener_usuarios():
    
    #Chequea cuantos usuarios hay dentro de l array USER
    cantidad_usuarios=len(USER)
    
    #Si no hay usuarios devuelve error y si si hay devuelve array USER
    if cantidad_usuarios == 0:
        return{'message':'No hay usuarios en la base de datos'}, 400
    return{"users": USER}, 200

#Ruta para agregar usuarios
@app.route("/adduser",methods=["POST"])
def add_user():
    global USER
    
    #Obtiene el usuario del metodo POST
    new_users=request.get_json().get("users",[])
    
    # se recorre el array de usuarios
    for new_user in new_users:
        # confirma si las claves id y el nombre fueron agradas si no envia error
        if 'id' not in new_user or 'nombre' not in new_user:
            return{'message':'datos del usuario invalidos'},400
        #si no fue encontrado dentro de los usuarios envia error
        if any (user ["id"] == new_user['id'] for user in USER):
            return{ 'message': f'Usuario con ID {new_user["id"]} ya existe'}, 409
    
    #Si se pasa la validación se agrega al usuario     
    USER.extend(new_users)
    
    return { 'message':'Usuario agregado correctamente',
            'nombres de los usuarios':[user["nombre"] for user in new_users]}, 201

#Ruta para agregar cancion al usuario
@app.route("/users/<int:user_id>/canciones", methods=["POST"])
def agregar_cancion_favorita(user_id):
    global USER
    
    #Se obtienen los datos del post
    datos=request.get_json()
    nombre_cancion=datos.get("cancion") if datos else None
    
    #si no se envia nombre responde con un codigo de error
    if not nombre_cancion:
        return{
            "message":"Debes proporcionar el nombre de la canción en el JSON"
            },400
    
    #verificamos si hay usuarios en el array para agregar canciones
    usuario_encontrado=None
    for user in USER:
        #Se verifica si el id del usuario existe
        if user["id"]==user_id:
            usuario_encontrado=user
            break
    #si no encuentra el usuario responde con un error
    if not usuario_encontrado:
        return{ "message": f"el usuario con id {user_id} no existe en la base de datos"}, 404
    
    #Buscar la cancion en Spotify
    cancion_info, error = buscar_cancion(nombre_cancion)
    if error:
        if "token" in error or "API" in error: return {"message": error}, 500
        return {"message": error}, 404

    #Si el usuario aún no tiene la lista 'canciones\_favoritas', se la creamos vacía
    if "canciones_favoritas" not in usuario_encontrado:
        usuario_encontrado["canciones_favoritas"]=[]
        
    #Verificar si la canción Ya existe dentro de los favoritos del usuario 
    cancion_existente = any(
        c["nombre"].lower() == cancion_info["nombre"].lower()
        for c in usuario_encontrado["canciones_favoritas"] )
    
    if cancion_existente: 
        return {"message": f"La canción '{cancion_info['nombre']}' ya está en tus favoritos"}, 400
    
    #se agrega cancion al usuario
    usuario_encontrado["canciones_favoritas"].append(cancion_info)
            
    return{
        "message": f"se ha agregado la cancion: '{nombre_cancion}' con exito al usuario: '{usuario_encontrado['nombre']}'",
        "user":usuario_encontrado
    }, 200

#Ruta para eliminar usuario
@app.route("/deleteusers" , methods=["DELETE"])
def delete_user():
    global USER
    # obtener informacion por el metodo
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

#Ruta para agregar información al usuario
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
    