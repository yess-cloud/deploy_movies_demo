import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar credenciales y conectar a Firestore
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-project-demo")

st.header("Netflix App")

@st.cache_data
def load_all_data():
    docs = db.collection("movies").stream()
    data = [doc.to_dict() for doc in docs]
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

# Cargar datos al inicio
data = load_all_data()

# Sidebar con checkbox para mostrar todos los filmes
sidebar = st.sidebar
agree = sidebar.checkbox("Mostrar todos los filmes")
if agree:
    st.subheader("Todos los filmes")
    if not data.empty:
        st.dataframe(data[['name', 'genre', 'director', 'company']])
    else:
        st.info("No hay filmes para mostrar.")

# Búsqueda por título
sidebar.subheader("Buscar filmes por título")
myname = sidebar.text_input('Título del filme')
search_button = sidebar.button("Buscar filmes")

if search_button:
    if myname:
        if not data.empty:
            filtered_data_byname = data[data['name'].str.contains(myname, case=False, na=False)]
            count_row = filtered_data_byname.shape[0]
            st.write(f"Total de filmes mostrados: {count_row}")
            if not filtered_data_byname.empty:
                st.dataframe(filtered_data_byname[['name', 'genre', 'director', 'company']])
            else:
                st.info("No se encontraron filmes con ese título.")
        else:
            st.info("No hay datos para buscar.")
    else:
        st.warning("Por favor, ingresa un título para buscar.")

# Filtrar por director
sidebar.subheader("Filtrar por director")
if not data.empty:
    selected_director = sidebar.selectbox("Seleccionar director:", data['director'].unique())
    btnFilterbyDirector = sidebar.button('Filtrar director')

    if btnFilterbyDirector:
        filtered_data_bydirector = data[data['director'] == selected_director]
        count_row = filtered_data_bydirector.shape[0]
        st.write(f"Total de filmes: {count_row}")
        st.dataframe(filtered_data_bydirector[['name', 'genre', 'director', 'company']])
else:
    st.info("No hay datos para filtrar por director.")

# Insertar nuevo filme
sidebar.subheader("Insertar nuevo filme")
name = sidebar.text_input("Nombre del filme")
company = sidebar.text_input("Compañía")
director = sidebar.text_input("Director")
genre = sidebar.text_input("Género")


submit = sidebar.button("Crear nuevo filme")

if submit:
    if name and company and genre and director:
        st.write("Agregando filme a Firestore...")
        doc_ref = db.collection("movies").document(name)
        doc_ref.set({
            "name": name,
            "company": company,
            "genre": genre,
            "director": director
        })
        st.success(f"El filme '{name}' ha sido agregado correctamente.")
        
        # Recargar datos para actualizar la tabla y búsquedas
        data = load_all_data()
    else:
        st.warning("Por favor, completa todos los campos para crear un nuevo filme.")
