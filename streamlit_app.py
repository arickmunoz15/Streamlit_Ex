#/content/Streamlit_ex/streamlit_app.py
import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account


import json
#conectar con google 
key_dict = json.loads(st.secrets['textkey'])
creds = service_account.Credentials.from_service_account_info(key_dict)

#conectarme con firebase
#db = firestore.Client.from_service_account_json("keys.json")
db = firestore.Client(credentials=creds, project=creds.project_id)
sbMov = db.collection('movies')

sb = st.sidebar

st.title('Films app')
#pasar los registros de firebase a un df
movies_ref = list(db.collection(u'movies').stream())
movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
mov_df = pd.DataFrame(movies_dict)
##st.dataframe(mov_df)

#read and cache the df
@st.cache
def load_data(nrows):
  data = mov_df[:nrows]
  return data

#Checkbox + header que permita ver todos los films
st.header('Dataset')
agree = sb.checkbox('Show all rows of dataset?')
if agree:
  data_lt = st.text('Loading data...')
  data = load_data(len(mov_df))
  data_lt.text('Done (using st.cache)')
  st.dataframe(data)
else:
  nro = sb.text_input('How many lines do we load?')
  if (nro):
    data = load_data(nro)
    st.dataframe(data)

#Busqueda + boton, filmes por titulo, contains. upper, lower
@st.cache
def load_data_bytitle(ttl, typee= True):
  if typee:
    dataf = mov_df[mov_df['name'].str.contains(ttl, case=False)]
  else:
    dataf = mov_df[mov_df['director'].str.contains(ttl)]

  count_row = dataf.shape[0]
  st.write(f'Total films that match: {count_row}')
  return dataf

fname = sb.text_input('Name of the film to search:')
if (fname):
  dfi = load_data_bytitle(fname)
  st.dataframe(dfi)

#Selectbox + boton (Seleccionar director), filtrar los films hechos por el director
seldir = sb.selectbox('Select Director', mov_df['director'].unique())
btnfltr = sb.button('Filter by dir')

if (btnfltr):
  dfi = load_data_bytitle(seldir, typee=False)
  st.dataframe(dfi)

#sep
sb.markdown('____')

#ingresar nuevo registro
sb.header('Enter the new films')

iname = st.text_input('Name')
icom = st.text_input('Company')
idir = st.text_input('Director')
igen = st.text_input('Genre')

submit = st.button("Create new film")

if iname and icom and idir and igen and submit:
  doc_ref = db.collection("movies").document(iname)
  doc_ref.set({
      'company':icom,
      'director':idir,
      'genre':igen,
      'name':iname
  })
  #company	director	genre	name
  sb.sidebar.write("succesfully enter new oscar movie")


