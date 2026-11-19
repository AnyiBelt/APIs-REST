from flask import Flask, request

app = Flask(__name__)

# Global var for users at the beginning we don't have anyone
USER = []

#Route to get users and sent the users
@app.route("/users" , methods=["GET"])
def obtener_usuarios():
    
    #check how many users are in the list
    cantidad_usuarios=len(USER)
    
    if cantidad_usuarios == 0:
        return{'mesage':'No hay usuarios en la base de datos'}, 400
    return{"users": USER}, 200

@app.route("/adduser",methods=["POST"])
def add_user():
    global USERS
    
    new_users=request.get_json().get("users",[])
    for new_user in new_users:
        if 'id' not in new_user or 'nombre' not in new_user:
            return{'mesage':'datos del usuario invalidos'},400
        if any (user ["id"] == new_user['id'] for user in USER):
            return{ 'mesage': f'Usuario con ID {new_user["id"]} ya existe'}, 409
        
    USER.extend(new_users)
    
    return { 'message':'Usuario agregado correctamente',
            'nombres de los usuarios':[user["nombre"] for user in new_users]}        
    
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
    