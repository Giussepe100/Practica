from flask import Flask, render_template, request,redirect,url_for,session
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd



    

#leo el archivo csv de peliculas 
ruta_archivo='Practica/app/movie_dataset.csv'
org_movies=pd.read_csv(ruta_archivo)
#leo el archivo csv de usuarios
ruta_archivo1='Practica/app/usuarios.csv'
usuarios=pd.read_csv(ruta_archivo1)
#ruta archivo csv usuarios_peliculas.csv
ruta_archivo2='Practica/app/usuarios_peliculas.csv'
peliculas_historial=pd.read_csv(ruta_archivo2)
#se mantienen las columnas importantes 
movies = org_movies[[ 'genres','homepage','vote_average','cast','director','title']]


movies.fillna('',inplace=True)
#movies.loc[:,:]=movies.loc[:,:].fillna('')
#creo una columna llamada funciones combinadas
movies['combined_features'] = movies['genres'] +' '+ movies['homepage']+' '+ str(movies['vote_average']) +' '+ movies['cast']+' '+ movies['director']+' '+movies['title']
movies.iloc[0]['combined_features']
    
cv = CountVectorizer()
count_matrix = cv.fit_transform(movies['combined_features'])

count_matrix

cs = cosine_similarity(count_matrix)
cs.shape
#FUNCIONES
def get_movie_name_from_index(index):
    return org_movies[org_movies['index']==index]['title'].values[0]

def get_index_from_movie_name(name):
    resultado= org_movies[org_movies['title']==name]['index']
    if resultado.empty:
        return 0
    else:
        return org_movies[org_movies['title']==name]['index'].values[0]
    
    
#mostrar informacion de una pelicula
def get_information_pelicula(name):
    return org_movies.loc[movies['title']==name]#busca el nombre de la pelicula y y devuelve toda su fila 
#buscar usuario
def buscar_usuario(username, contrasena):
    usuario = usuarios[usuarios['username'] == username]  # Verifica nombres de usuario coincidentes
    contrasena = usuario[usuario['contrasena'] == contrasena]  # Verifica contraseñas coincidentes dentro de nombres de usuario coincidentes
    if contrasena.empty:
        return 0  # Usuario no encontrado
    else:
        #return usuario
        return usuario['user_id'].values[0]  # Usuario encontrado
        
       
         
#FuncionRegistrarUsuario
def registrar_usuario(nombre_archivo, nuevo_usuario):
    try:
        #df=pd.read_csv(nombre_archivo)
        global usuarios
    except FileNotFoundError:
        usuarios1=pd.DataFrame(columns=['user_id','username','email','contrasena'])

    #obtengo el  ultimo Id
    if usuarios.empty:
        nuevo_id=1
    else:
        usuarios['user_id']=pd.to_numeric(usuarios['user_id'],errors='coerce')
        ultimo_id=usuarios['user_id'].max()
        if pd.isna(ultimo_id):
            nuevo_id=1
        else:
            nuevo_id=int(ultimo_id)+1
    
    #Agrego el nuevo usuario al Dataframe
    nuevo_usuario['user_id']=nuevo_id
    usuarios=pd.concat([usuarios,pd.DataFrame([nuevo_usuario])],ignore_index=True)
    #Escribo el Data frame actualizado al archivo CSV
    usuarios.to_csv(nombre_archivo, index=False)

#FUNCION BUSCAR TIPO DE PELICULA 
def BuscarTipoPelicula(tipoPelicula):
    peliculasEncontradas = org_movies[org_movies['genres'].apply(lambda x: isinstance(x, str) and tipoPelicula in x.split())]['title'].tolist()
    if not peliculasEncontradas:
        return peliculasEncontradas
    else:
        return peliculasEncontradas[:5]


def BuscarPorIdUser(user_id):
    global usuarios
    row=usuarios[usuarios['user_id']==user_id]
    return row.to_dict('records')[0]

def ActualizarDatosUsuario(user_id,new_data):
    global usuarios
    global ruta_archivo1
    #verifico si el usuario existe 
    idx=usuarios[usuarios['user_id']==user_id].index
    if len(idx)>0:
        usuarios.loc[idx,'username']=new_data['username']
        usuarios.loc[idx,'email']=new_data['email']
        usuarios.loc[idx,'contrasena']=new_data['contrasena']
        usuarios.to_csv(ruta_archivo1,index=False)
        return "Datos del usuario actualizado con exito "
    else:
        return "Usuario no encontrado"

def MostrarDirectoresXTipoPelicula(tipoPelicula):
    global org_movies
    
    ResultadoPelicula= org_movies[org_movies['genres'].apply(lambda x: isinstance(x, str) and tipoPelicula in x.split())]['director'].tolist()
    if not ResultadoPelicula:
        return ResultadoPelicula
    else:
        return ResultadoPelicula[:5]
#wdd dddsf ddd d ddS
def get_pelicula_trabajado_director(nombredirector):
    #filtrar el dataframe por el nombre del director 
    global org_movies
    peliculas=org_movies[org_movies['director'].str.contains(nombredirector,case=False,na=False)]

    if peliculas.empty:
        return "No se ha encontrado peliculas"
    else:
        nombres_peliculas=peliculas['title'].tolist()
        return nombres_peliculas[:5]
    
def buscamos_usuarioId_ArchivoCsv(user_id):
    global peliculas_historial
    #filtramos el dataframe por el codigo de la pelicula
    #i Busca las filas que tienen el user_id especifico
    indice_peliculas_vistas = peliculas_historial.loc[peliculas_historial['user_id'] == user_id]
    
    if indice_peliculas_vistas.empty:
        lista_indices_peliculas=[]
    else:
        lista_indices_peliculas = indice_peliculas_vistas['index'].tolist()
    # Obten los índices de esas filas
    
    return lista_indices_peliculas

def get_information_pelicula_ID(idPelicula):
    return org_movies.loc[org_movies['index']==idPelicula]


def AgregarArchivoCSVPeliculavista(nombre_archivo1,nueva_fila_historial):
    global peliculas_historial

    if peliculas_historial.empty:
        CodUsuarioPelicula=1
    else:
        peliculas_historial['CodUsuarioPelicula']=pd.to_numeric(peliculas_historial['CodUsuarioPelicula'],errors='coerce')
        ultimo_id=peliculas_historial['CodUsuarioPelicula'].max()
        if pd.isna(ultimo_id):
            CodUsuarioPelicula=1
        else:
            CodUsuarioPelicula=int(ultimo_id)+1
    
    #Agrego el nuevo usuario al Dataframe
    nueva_fila_historial['CodUsuarioPelicula']=CodUsuarioPelicula
    peliculas_historial=pd.concat([peliculas_historial,pd.DataFrame([nueva_fila_historial])],ignore_index=True)
    #Escribo el Data frame actualizado al archivo CSV
    peliculas_historial.to_csv(nombre_archivo1, index=False)


Lista_peliculas=list(movies['title'])
lista_peliculas_similares=Lista_peliculas[:5]


#Presentando la interfaz en el servidor 

app=Flask(__name__)
app.secret_key="1234clave"

#MOVER ENTRE PÁGINAS
@app.route('/')
def index():
    return render_template("Inicio_Sesion.html")
   

@app.route('/Redirigir' ,methods=['GET','POST'])
def Redirigir():
    global lista_peliculas_similares
    if not lista_peliculas_similares:
       global movies
       Lista_peliculas=list(movies['title'])
       lista_peliculas_similares=Lista_peliculas[:5]
       return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)
    else:
       return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)

@app.route('/IrRegistroUsuario' ,methods=['GET','POST'])
def IrRegistroUsuario():
    return render_template("Registro.html")

@app.route('/RedirigirBusquedaTipoPelicula' ,methods=['GET','POST'])
def RedirigirBusquedaTipoPelicula():
    return render_template("BuscarTipoPelicula.html",lista_peliculas_similares=lista_peliculas_similares)
#---------------------------------------------------------------
#Funciones 

@app.route('/ExtraerNombrePelicula',methods=['GET','POST'])
def ExtraerNombrePelicula():
    if request.method=='POST':
        test_movie_name=request.form['nombrePelicula']
        return redirect(url_for('MostrarPeliculasSimilares',param=test_movie_name))#Redireccionar hasta el suguiente link 
    else:
        return render_template("Recomendacion.html")

@app.route('/MostrarPeliculasSimilares',methods=['GET','POST'])
def MostrarPeliculasSimilares():
    movie_name=request.args.get('param')
    test_movie_index=get_index_from_movie_name(movie_name)
    global lista_peliculas_similares
    lista_peliculas_similares.clear()
    if test_movie_index!=0:
        movie_corrs=cs[test_movie_index]
        movie_corrs=enumerate(movie_corrs)
        sorted_similar_movies=sorted(movie_corrs,key=lambda x:x[1],reverse=True)
        for i in range(5):
            lista_peliculas_similares.append(get_movie_name_from_index(sorted_similar_movies[i][0]))

        return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)
    else:
        return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)
    
@app.route('/ExtraerInformacionPelicula/<string:nombre_pelicula>') 
def  ExtraerInformacionPelicula(nombre_pelicula):
    user=session.get('user')
    user_id=user['user_id']
    fila_pelicula=get_information_pelicula(nombre_pelicula)
    if 'lista_peliculas_vistas' not in session:
        session['lista_peliculas_vistas']=[]
    session['lista_peliculas_vistas'].append(fila_pelicula['title'].iloc[0])
    session.modified=True
    nueva_fila_historial={'index':fila_pelicula['index'].iloc[0],'user_id':user_id}
    global ruta_archivo2
    AgregarArchivoCSVPeliculavista(ruta_archivo2,nueva_fila_historial)
    return render_template("InformacionPelicula.html",fila_pelicula=fila_pelicula)#Lo que le estoy enviando es un dataframe

@app.route('/BuscarUsuario',methods=['GET','POST'])
def BuscarUsuario():
    if request.method=='POST':
        username=request.form['username']
        contrasena=request.form['contrasena']
       
        valor_id_usuario=buscar_usuario(username,contrasena)
        if valor_id_usuario!=0:
            
            session['user']={'username':username,'contrasena':contrasena,'user_id':int(valor_id_usuario)}
            session['lista_peliculas_vistas']=[]
            return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)
        else:
            return render_template("Inicio_Sesion.html",valor_id_usuario=valor_id_usuario)
    else:
        return "error"

@app.route('/RegistrarNuevoUsuario',methods=['GET','POST'])
def RegistrarNuevoUsuario():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        contrasena=request.form['contrasena']
        nuevo_usuario={'username':username,'email':email,'contrasena':contrasena}
        #llamar funcion 
        global ruta_archivo1
        registrar_usuario(ruta_archivo1,nuevo_usuario)
        return render_template("Inicio_Sesion.html")
    else:
        return "error"
###
@app.route('/ExtraerTipoPelicula',methods=['GET','POST'])
def ExtraerTipoPelicula():
    if request.method=='POST':
        global lista_peliculas_similares
        lista_peliculas_similares.clear()
        #voy a buscar
        tipoPelicula=request.form.get('tipoPelicula')
        listaString=BuscarTipoPelicula(tipoPelicula)

        return render_template("BuscarTipoPelicula.html",listaString=listaString,lista_peliculas_similares=lista_peliculas_similares)
    else:
        return "error"
        




@app.route('/ExtraerInformacionUsuario', methods=['GET','POST']) 
def  ExtraerInformacionUsuario():
    user=session.get('user')
    usuario_id=user['user_id']
    user_data=BuscarPorIdUser(usuario_id)
    return render_template("InformacionUsuario.html",user_data=user_data)

@app.route('/logout', methods=['GET','POST']) 
def  logout():
    session.pop('lista_peliculas_vistas',None)
    session.pop('user',None) 
    return render_template("Inicio_Sesion.html")

@app.route('/EditarDatosUsuario', methods=['GET','POST'])
def  EditarDatosUsuario():
    if request.method=='POST':
        #global ruta_archivo1
        user_id=int(request.form['user_id'])
        new_data={
            'username':request.form['username'],
            'email':request.form['email'],
            'contrasena':request.form['contrasena']

        }
        #verifico si el usuario existe
        ActualizarDatosUsuario(user_id,new_data)
        return redirect(url_for('Redirigir'))
    else:
        return "No se encontro el usuario"
    
@app.route('/ExtraerPeliculasDirector', methods=['GET','POST'])
def  ExtraerPeliculasDirector():
        if request.method=='POST':
            tipoPelicula=request.form.get('tipoPelicula')
            lista=MostrarDirectoresXTipoPelicula(tipoPelicula)
            return render_template("BuscarDirectoresXTipoPelicula.html",lista=lista)
        else:
            return "error"
        
@app.route('/RedirigirBusquedaDirectores' ,methods=['GET','POST'])
def RedirigirBusquedaDirectores():
    return render_template("BuscarDirectoresXTipoPelicula.html")

@app.route('/BusquedaPeliculasDirector/<string:nombre_director>') 
def  BusquedaPeliculasDirector(nombre_director):
    #peliculass=get_pelicula_trabajado_director(nombre_director)
    global lista_peliculas_similares
    lista_peliculas_similares.clear()
    lista_peliculas_similares=get_pelicula_trabajado_director(nombre_director)
    return render_template("Recomendacion.html",lista_peliculas_similares=lista_peliculas_similares)

"""Modificar esto """
@app.route('/Ver_Historial_Peliculas_Usuario' ,methods=['GET','POST'])
def Ver_Historial_Peliculas_Usuario():
    
    user=session.get('user')
    usuario_id=user['user_id']
    #miramos si ha  iniciado session 
    if 'lista_indice_finPeliculas' not in session:
        session['lista_indice_finPeliculas']=[]

    if not session['lista_peliculas_vistas']:#si la lista esta vacia 
        session['lista_indice_finPeliculas'] = buscamos_usuarioId_ArchivoCsv(usuario_id)#pasamos los datos
        lista_peliculas_vistas=llenarlistapeliculasVistas()
        return render_template("Historial_Peliculas.html",lista_peliculas_vistas=lista_peliculas_vistas)
    else:
           session['lista_peliculas_vistas'].clear()
           session['lista_indice_finPeliculas'] = buscamos_usuarioId_ArchivoCsv(usuario_id)
           lista_peliculas_vistas=llenarlistapeliculasVistas()

           return render_template("Historial_Peliculas.html",lista_peliculas_vistas=lista_peliculas_vistas)
        
        
@app.route('/llenarlistapeliculasVistas' ,methods=['GET','POST'])
def llenarlistapeliculasVistas():
    if 'lista_peliculas_vistas' not in session:
        session['lista_peliculas_vistas'] = []
    else:
        for x in session['lista_indice_finPeliculas']:
           fila_pelicula_encontrada=get_information_pelicula_ID(x)
           session['lista_peliculas_vistas'].append(fila_pelicula_encontrada['title'].iloc[0])
           session.modified=True
        return session['lista_peliculas_vistas']

if __name__=='__main__':
    app.run(debug=True,port=5000)

