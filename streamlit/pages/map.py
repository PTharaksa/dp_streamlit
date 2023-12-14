import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import altair as alt
import folium
from streamlit-folium import st_folium
import os

filename = 'st_AEC.xlsx'

def load_data(file):
    data = load_workbook(file)
    sheet_ranges = data['Sheet1']
    df = pd.DataFrame(sheet_ranges.values)
    df.columns = df.iloc[0]
    df = df[1:]
    dfn = df.convert_dtypes()
    dfn['year'] = dfn['year'].astype(str)
    return dfn

st.set_page_config(
    page_title="Asian",
    layout='wide',
    initial_sidebar_state='auto',
)

st.title('Map')

dfn = load_data(filename)
st.subheader('Select the selectbox to alter the map')
st.selectbox('Select the indicator:', dfn.columns[2:], key='indicator')

m_data = dfn[['Country Name','year', st.session_state.indicator]]
latest_data = m_data['year'].max()
m_data = m_data[m_data['year'] == latest_data]
m_data['Country Name'].replace(to_replace=r'Lao PDR', value='Laos', regex=True, inplace=True)
m_data['Country Name'].replace(to_replace=r'Brunei Darussalam', value='Brunei', regex=True, inplace=True)
layer_map = m_data[['Country Name', st.session_state.indicator]]
world_map =os.path.join('world-countries.json')
m = folium.Map(location=[20,100], zoom_start=4)
cp = folium.Choropleth(
    geo_data=world_map,
    name="choropleth",
    data=layer_map,
    columns=["Country Name", st.session_state.indicator],
    key_on="feature.properties.name",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
)
cp.geojson.add_to(m)


#display data
layer_map_indexed = layer_map.set_index('Country Name')

cp.geojson.add_child(
  folium.features.GeoJsonTooltip(['name'], labels=False)
)
st_data = st_folium(m, width=1000)


if st_data['last_active_drawing']:
  st.header(st_data['last_active_drawing']['properties']['name'])
  st.write(str(st.session_state.indicator) + ' [2021]')
  st.subheader(str(layer_map_indexed.loc[st_data['last_active_drawing']['properties']['name'], str(st.session_state.indicator)]))
else:
  st.warning('Click on colored area for the detail')
