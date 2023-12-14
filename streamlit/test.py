import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import altair as alt
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(
  page_title='Asian',
  layout='wide',
  initial_sidebar_state='expanded'
)

st.title('Asian 🌏')


#load excel file
wb = load_workbook(filename='st_AEC.xlsx')
sheet_ranges = wb['Sheet1']
df = pd.DataFrame(sheet_ranges.values)

#set dataframe header
df.columns = df.iloc[0]
df = df[1:]

#convert year (int64) into string
dfn = df.convert_dtypes()
dfn['year'] = dfn['year'].astype(str)

#select box for each country
st.sidebar.multiselect('Select the country:', dfn['Country Name'].unique(), key='country', max_selections=5)

#select box for indicator
st.sidebar.selectbox('Select the indicator:', dfn.columns[2:], key='indicator')

#year filtered
st.sidebar.slider('Select the range of years:', 1995, 2021, (2007,2010), key='year')

tab1, tab2 = st.tabs(['Line Graph', 'Dataframe'])

#line graph function
result = []
for country in st.session_state.country:
  if country in dfn['Country Name'].unique():
    result.append(dfn[dfn['Country Name'] == country])
  else:
    st.write('There is no data in selected country.')
  
if len(st.session_state.country) > 1:
    concat_df = pd.concat(result)
    if st.session_state.indicator in dfn.columns[2:]:
      if st.session_state.year[0] <= st.session_state.year[1]:
        concat_df = concat_df[
                (concat_df['year'] >= str(st.session_state.year[0])) &
                (concat_df['year'] <= str(st.session_state.year[1]))
            ]
        concat_df = concat_df[['Country Name', 'year', st.session_state.indicator]]
        tab2.write(concat_df)
        lines = (
          alt.Chart(concat_df, title=f"line graph for {st.session_state.indicator}")
          .mark_line()
          .encode(
              x='year',
              y=st.session_state.indicator,
              color='Country Name',
          )
        ).interactive()
        tab1.altair_chart(lines, theme='streamlit', use_container_width=True)
elif len(st.session_state.country) == 1:
    df_result = dfn[dfn['Country Name'] == country]
    if st.session_state.indicator in dfn.columns[2:]:
       if st.session_state.year[0] <= st.session_state.year[1]:
        df_result = df_result[
                (df_result['year'] >= str(st.session_state.year[0])) &
                (df_result['year'] <= str(st.session_state.year[1]))
            ]
        df_result = df_result[['Country Name', 'year', st.session_state.indicator]]
        tab2.write(df_result)
        lines = (
          alt.Chart(df_result, title= f"line graph for {st.session_state.indicator}")
          .mark_line()
          .encode(
            x='year',
            y=st.session_state.indicator,
            color='Country Name',
          )
        ).interactive()
        tab1.altair_chart(lines, theme='streamlit', use_container_width=True)
else:
   st.warning('Please select at least one country.')

st.divider()

#map
st.subheader('Select the selectbox to alter the map')
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
    legend_name= str(st.session_state.indicator) + " 2021",
)
cp.geojson.add_to(m)


#display data
layer_map_indexed = layer_map.set_index('Country Name')

cp.geojson.add_child(
  folium.features.GeoJsonTooltip(['name'], labels=False)
)
st_data = st_folium(m, width=725)


if st_data['last_active_drawing']:
  st.header(st_data['last_active_drawing']['properties']['name'])
  st.write(str(st.session_state.indicator) + ' [2021]')
  st.subheader(str(layer_map_indexed.loc[st_data['last_active_drawing']['properties']['name'], str(st.session_state.indicator)]))
else:
  st.warning('Click on colored area for the detail')