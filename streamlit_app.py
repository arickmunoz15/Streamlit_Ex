import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Connect to Google Cloud using credentials from Streamlit secrets
try:
    key_dict = json.loads(st.secrets['textkey'])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project=creds.project_id)
    st.write("Successfully connected to Firestore.")
except Exception as e:
    st.error(f"Error connecting to Firestore: {e}")
    st.stop()

# Sidebar for user inputs
sb = st.sidebar

st.title('Films app')

# Fetch Firestore data and convert to DataFrame with detailed error handling
try:
    movies_ref = db.collection(u'movies').stream()
    movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
    mov_df = pd.DataFrame(movies_dict)
    st.write("Successfully fetched data from Firestore.")
except Exception as e:
    st.error(f"Error fetching data from Firestore: {e}")
    st.stop()

# Cache data loading function
@st.cache
def load_data(nrows):
    return mov_df[:nrows]

# Display the dataset
st.header('Dataset')
agree = sb.checkbox('Show all rows of dataset?')
if agree:
    data_lt = st.text('Loading data...')
    data = load_data(len(mov_df))
    data_lt.text('Done (using st.cache)')
    st.dataframe(data)
else:
    nro = sb.text_input('How many lines do we load?', '10')
    if nro.isdigit():
        data = load_data(int(nro))
        st.dataframe(data)
    else:
        st.error("Please enter a valid number of rows.")

# Cache function for loading data by title or director
@st.cache
def load_data_bytitle(ttl, typee=True):
    if typee:
        dataf = mov_df[mov_df['name'].str.contains(ttl, case=False)]
    else:
        dataf = mov_df[mov_df['director'].str.contains(ttl, case=False)]
    count_row = dataf.shape[0]
    st.write(f'Total films that match: {count_row}')
    return dataf

# Search by film title
fname = sb.text_input('Name of the film to search:')
if fname:
    dfi = load_data_bytitle(fname)
    st.dataframe(dfi)

# Filter by director
seldir = sb.selectbox('Select Director', mov_df['director'].unique())
btnfltr = sb.button('Filter by director')
if btnfltr:
    dfi = load_data_bytitle(seldir, typee=False)
    st.dataframe(dfi)

# Divider
sb.markdown('____')

# Input new film details
sb.header('Enter the new film')
iname = sb.text_input('Name')
icom = sb.text_input('Company')
idir = sb.text_input('Director')
igen = sb.text_input('Genre')
submit = sb.button("Create new film")

st.write(f"Name: {iname}")
st.write(f"Company: {icom}")
st.write(f"Director: {idir}")
st.write(f"Genre: {igen}")

# Create new film entry in Firestore with detailed error handling
if iname and icom and idir and igen and submit:
    try:
        doc_ref = db.collection("movies").document(iname)
        doc_ref.set({
            'company': icom,
            'director': idir,
            'genre': igen,
            'name': iname
        })
        sb.write("Successfully entered new film.")
    except Exception as e:
        st.error(f"Error adding new film to Firestore: {e}")
