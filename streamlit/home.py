pip install openpyxl
import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import altair as alt
from streamlit_folium import st_folium
import re

filename = 'st_AEC.xlsx'
country_list = ['Indonesia', 'Philippines', 'Thailand', 'Vietnam', 'Myanmar']
ticker = '⚠️'
annotation_list = [('1998', 'Asian economic crisis'),
              ('2020', 'Spreading of COVID-19')]

def load_data(file):
    data = load_workbook(file)
    sheet_ranges = data['Sheet1']
    df = pd.DataFrame(sheet_ranges.values)
    df.columns = df.iloc[0]
    df = df[1:]
    dfn = df.convert_dtypes()
    dfn['year'] = dfn['year'].astype(str)
    return dfn

def line_plot(dfn, column):
    column_title = re.search(r'([A-Za-z]+\s*([a-z]*\s*)+\,*\s*[a-z0-9]*\+*\,*\s*[a-z]*)', column)
    hover = alt.selection_single(
        fields=["year"],
        nearest=True,
        on="mouseover",
        empty="none",
    )
    lines = (
        alt.Chart(dfn, height=500, title=f"{column_title.group(0)}")
        .mark_line()
        .encode(
            x='year',
            y= column, 
            color='Country Name',
            )
    )
    points = lines.transform_filter(hover).mark_circle(size=65)
    tooltips = (
                alt.Chart(dfn)
                .mark_rule()
                .encode(
                    x="year",
                    y=column,
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("year", title="Year"),
                        alt.Tooltip(column, title=f"{column}"),
                    ],
                )
                .add_selection(hover)
            )
    return (lines + points + tooltips).interactive()

def annotation(annote_frame):
    annote_frame.loc[annote_frame['year'] == '1998', 'y'] = -13
    annote_frame.loc[annote_frame['year'] == '2020', 'y'] = -9.5
    annote_layer = (
        alt.Chart(annote_frame)
        .mark_text(size=15, text=ticker, align="center")
        .encode(
            x='year',
            y=alt.Y('y:Q'),
            tooltip=['event'],
        )
        .interactive()
    )
    return annote_layer

def bar_chart(dfn):
    bars = (
        alt.Chart(dfn, title='Population in 2021')
        .mark_bar()
        .encode(
        x = alt.X('Country Name', sort='-y'),
        y = 'Population, total',
        color='Country Name',
    )
    .properties(
        width=550,
    )
    .interactive()
)
    return bars

st.set_page_config(
    page_title="Asian",
    layout='wide',
    initial_sidebar_state='auto',
)
st.title('Asian')
st.markdown('This site provided by the information of 10 countries. There are 3 things you would like to know:')
st.markdown('1) The bar chart is provided in order to look through the population in every countries in 2021')
st.markdown('2) Provided GDP growth line graph of 5 most crowded countries.')
st.markdown('3) And to be more specific, you can choose the above 5 countries up to 3 countries for further detail.')
dfn = load_data(filename)
with st.expander('Click to view the dataframe'):
    st.write(dfn)

df_2021 = dfn[dfn['year'] =='2021']
st.subheader('Top 5 most populated countries.')
st.altair_chart(bar_chart(df_2021), use_container_width=True)

frame = dfn[dfn['Country Name'].isin(country_list)]

#convert into dataframe with year and event columns 
annote = pd.DataFrame(annotation_list, columns=['year', 'event'])
chart = (line_plot(frame, 'GDP growth (annual %)'))
annotation_layer = annotation(annote)
st.subheader('GDP growth of Top 5 most populated countries.')
st.altair_chart((chart + annotation_layer).interactive(), use_container_width=True)

st.subheader('Select at least one country.')
st.multiselect('Select the country:', frame['Country Name'].unique(), key='country', max_selections=3)
st.slider('Select the range of years:', 1995, 2021, (2007,2010), key='year')

result = []
for country in st.session_state.country:
  if country in dfn['Country Name'].unique():
    result.append(dfn[dfn['Country Name'] == country])
  else:
    st.write('There is no data in selected country.')

c1 = st.container()
col1,_,col2 = st.columns((3.9, 0.2, 3.9))
with c1:
    with col1:
        if len(st.session_state.country) > 1:
            concat_df = pd.concat(result)
            if st.session_state.year[0] <= st.session_state.year[1]:
                concat_df = concat_df[
                (concat_df['year'] >= str(st.session_state.year[0])) &
                (concat_df['year'] <= str(st.session_state.year[1]))
            ]
            st.altair_chart(line_plot(concat_df, 'Birth rate, crude (per 1,000 people)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Service exports (BoP, current US$)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Employment to population ratio, 15+, total (%) (modeled ILO estimate)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'CO2 emissions from manufacturing industries and construction (% of total fuel combustion)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Urban population growth (annual %)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Access to electricity, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'People using at least basic drinking water services, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'People using at least basic sanitation services, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Employment to population ratio, 15+, female (%) (modeled ILO estimate)'), use_container_width=True)
        elif len(st.session_state.country) == 1:
            df_result = dfn[dfn['Country Name'] == country]
            if st.session_state.year[0] <= st.session_state.year[1]:
                df_result = df_result[
                (df_result['year'] >= str(st.session_state.year[0])) &
                (df_result['year'] <= str(st.session_state.year[1]))
            ]
            st.altair_chart(line_plot(df_result, 'Birth rate, crude (per 1,000 people)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Service exports (BoP, current US$)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Employment to population ratio, 15+, total (%) (modeled ILO estimate)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'CO2 emissions from manufacturing industries and construction (% of total fuel combustion)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Urban population growth (annual %)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Access to electricity, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'People using at least basic drinking water services, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'People using at least basic sanitation services, urban (% of urban population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Employment to population ratio, 15+, female (%) (modeled ILO estimate)'), use_container_width=True)
        else:
            st.warning('Please select at least one country.')
    with col2:
        if len(st.session_state.country) > 1:
            concat_df = pd.concat(result)
            if st.session_state.year[0] <= st.session_state.year[1]:
                concat_df = concat_df[
                (concat_df['year'] >= str(st.session_state.year[0])) &
                (concat_df['year'] <= str(st.session_state.year[1]))
            ]
            st.altair_chart(line_plot(concat_df, 'Death rate, crude (per 1,000 people)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Goods exports (BoP, current US$)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Current education expenditure, total (% of total expenditure in public institutions)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Travel services (% of service exports, BoP)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Rural population growth (annual %)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Access to electricity, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'People using at least basic drinking water services, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'People using at least basic sanitation services, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(concat_df, 'Employment to population ratio, 15+, male (%) (modeled ILO estimate)'), use_container_width=True)
        elif len(st.session_state.country) == 1:
            df_result = dfn[dfn['Country Name'] == country]
            if st.session_state.year[0] <= st.session_state.year[1]:
                df_result = df_result[
                (df_result['year'] >= str(st.session_state.year[0])) &
                (df_result['year'] <= str(st.session_state.year[1]))
            ]
            st.altair_chart(line_plot(df_result, 'Death rate, crude (per 1,000 people)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Goods exports (BoP, current US$)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Current education expenditure, total (% of total expenditure in public institutions)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Travel services (% of service exports, BoP)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Rural population growth (annual %)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Access to electricity, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'People using at least basic drinking water services, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'People using at least basic sanitation services, rural (% of rural population)'), use_container_width=True)
            st.altair_chart(line_plot(df_result, 'Employment to population ratio, 15+, male (%) (modeled ILO estimate)'), use_container_width=True)
        else:
            ""

