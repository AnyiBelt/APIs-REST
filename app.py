from flask import Flask, request
from spotify_service import buscar_cancion

app = Flask(__name__)

# Variable global de usuarios que no esta iniciañizada he iremos llenando con el metodo post
USER = []

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
            break
    if not usuario_encontrado:
        return{ "message": f"el usuario con id {user_id} no existe en la base de datos"}, 404
    
    #Buscar la cancion en Spotify
    cancion_info, error = buscar_cancion(nombre_cancion)
    if error:
        return{"message":error},404

    #buscar el usuario por ID en nuestra lista de usuarios
    if "canciones_favoritas" not in usuario_encontrado:
        #agregamos la cancion a la lista del usuario
        usuario_encontrado["canciones_favoritas"]=[]
        
    usuario_encontrado["canciones_favoritas"].append(cancion_info)
            
    return{
        "message": f"se ha agregado la cancion: '{nombre_cancion}' con exito al usuario: '{usuario_encontrado['nombre']}'",
        "user":usuario_encontrado
    }, 200
    
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
    