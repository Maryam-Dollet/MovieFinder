# -*- coding: utf-8 -*-

import streamlit as st 
from streamlit_option_menu import option_menu 
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image

def closeFilms2(film_name, df, cols):

    #copy the datarame to do operations on it
    dataf = df.copy()

    #get the film in question
    film = dataf.loc[dataf['name'] == film_name]


    #get distances from our film
    dataf["dist"] = 0
    for c in cols:
        dataf["tempDist"] = dataf[c].apply(lambda x : (x-film[c])**2)
        dataf["dist"] += dataf["tempDist"]
    dataf["dist"] = dataf["dist"].apply(lambda x : np.sqrt(x))


    #get ride of tempDist column
    dataf.drop(columns=["tempDist"], inplace=True)

    #sort dataf
    dataf = dataf.sort_values("dist")

    return dataf

def closeFilms(film_name, df, r=0.5, cols=["0","1","2","3","4","5","6","7","8","9"]):

    
    dataf = df.copy()
    
    i = dataf.loc[dataf['name'] == film_name]

    
    dataf["dist"] = 0
    for c in cols:
        
        dataf["tempDist"] = dataf[c].apply(lambda x : (x-i[c])**2)
        dataf["dist"] += dataf["tempDist"]

    dataf["dist"] = dataf["dist"].apply(lambda x : np.sqrt(x))
    
    dataf.drop(columns=["tempDist"], inplace=True)
    
    dataf = dataf[dataf["dist"]<r]
    dataf = dataf.sort_values("dist")

    return dataf

def displayFilms(df, size):
    st.markdown(f'The first {size} films')
    for i in range(size):
                title = df['name'][i]
                year = df['year'][i]
                genre = df['genre'][i]
                film_desc = df['text-muted'][i]
                genre = str(genre).replace("'","")
                genre = genre.replace('[',"")
                genre = genre.replace(']',"")
                st.markdown(FILM_HTML_TEMPLATE.format(str(title),str(year),genre ), unsafe_allow_html=True)

                with st.expander('Description'):
                    st.write(film_desc)

FILM_HTML_TEMPLATE = """
<div>
<h4>{}</h4>
<h5>{}</h5>
<h6> Genres : {}</h6>
</div>
"""

with st.sidebar:
    selected = option_menu(
        menu_title = "Main Menu",
        options = ["Home","Movie Finder","About"]
    )

if selected == "Home":
    st.snow()
    st.title('Home')
    col1, col2 = st.columns(2)

    with col1:
        image = Image.open('logo.jpg')
        st.image(image)
    with col2:
        st.subheader("Welcome to Movie Finder ! ")
        st.markdown("Searching for the details of a movies ? ")
        st.markdown("Don’t know what to watch tonight ? ")
        st.markdown("Find all the movies that are like your favorite ones in one click !")

if selected == "Movie Finder":
    st.title('Movie Finder WebApp')
    st.write('This is our database')

    df = pd.read_csv("all_films.csv",sep=";")
    

    genres = []
    for i in range(df.shape[0]):
        sti = df['genre'].loc[i]
        sti = sti.replace(" ", "")
        sti = sti.replace('[',"")
        sti = sti.replace(']',"")
        sti = sti.replace("'", "")
        sti = sti.split(",")
        genres.append(sti)

    s = set()
    for i in range(len(genres)):
        for j in range(len(genres[i])):
            s.add(genres[i][j])
    s = list(s)


    with st.sidebar:
        st.header("Search your Films !")
        filter = st.multiselect("By Genre", s)
        
        if len(filter) != 0:
            is_in = []
            for i in range(len(df)):
                if all(elem in df['genre'][i] for elem in filter):
                    is_in.append(1)
                else:
                    is_in.append(0)
            df['is_in'] = is_in

        st.write("By writing the film title :")

        with st.form(key = 'searchform'):
            nav1,nav2 = st.columns([2,1])

            with nav1:
                search_term = st.text_input('Film Name')
            with nav2:
                st.text("")
                st.text("")
                search_submit = st.form_submit_button()
        
        st.header("Our recommendations for you")
        st.write("Write a Film Name and we will choose the right film for you !")

        r = st.slider(label = 'R slider',min_value=0.00, max_value=2.00, step=0.01, value=1.00)
        st.write("Slider value :",r)
        
        with st.form(key = 'searchform2'):
            nav1,nav2 = st.columns([2,1])

            with nav1:
                search_term2 = st.text_input('Film Name')
            with nav2:
                st.text("")
                st.text("")
                search_submit2 = st.form_submit_button()
    

    st.write(df)

    data = pd.read_csv('data_famd_web.csv', sep =';')
    data.drop_duplicates(["name"], inplace=True)
    st.write("Database with Distances")
    st.write(data)

    st.write('FAMD 3D plot')

    choices = st.multiselect("Display variables", data.columns[-10:], default=['0','1','2','3'])

    if (len(choices)<4):
        choices = data.columns[-10:-10+4]
        nx, ny, nz = choices[0], choices[1], choices[2] 
        ncol = choices[3]
    else:
        nx, ny, nz = choices[0], choices[1], choices[2] 
        ncol = choices[3]

    fig = px.scatter_3d(data, x=nx, y=ny, z=nz, color=ncol,
            hover_data={'name': True, 'runtime': ':.1f', 'year':True, f'{nx}':False, f'{ny}':False, f'{nz}':False, f'{ncol}':False},
            hover_name='name',)

    fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="LightSteelBlue"
        )

    st.plotly_chart(fig)

    if len(filter) != 0:
        try:
            st.title('Research by genre')
            genre_results = df[df['is_in']== 1]
            genre_results = genre_results.reset_index()
            num_genre_results = len(genre_results)
            st.write(genre_results)
            st.subheader("{} results".format(num_genre_results))
            if genre_results != 0:
                displayFilms(df_result, len(df_result))
            else:
                st.markdown("No results")

        except:
            st.error('No results')

    if search_submit:
        st.success("You searched for {}".format(search_term))
        df_result = df.loc[df['name'].str.contains(search_term, case=False)]
        df_result = df_result.reset_index(drop=True)
        num_df_result = len(df_result)
        st.title(f"Results for {search_term}")
        st.write(df_result)
        st.subheader("{} results".format(num_df_result))
        if df_result != 0:
            displayFilms(df_result, len(df_result))
        else:
            st.markdown("No results")
        
    
    if search_submit2:
        df_result2 = df.loc[df['name'].str.contains(search_term2, case=False)]
        df_result2 = df_result2.reset_index()
        num_df_result2 = len(df_result2)
        st.success("You searched for {}".format(df_result2['name'][0]))
        #cf = closeFilms(df_result2['name'][0],data, r=1)
        cf2 = closeFilms2(df_result2['name'][0], data, data.keys()[-10:])
        
        #cf = cf.reset_index()
        cf2 = cf2.reset_index(drop=True)
        cf2 = cf2[cf2["dist"]<r]
        st.write(cf2)
        #cf = cf.drop(columns=["Unnamed: 0"])
        #r = st.slider(label = 'R slider',min_value=0.00, max_value=2.00, step=0.01, value=1.00)
        
        #st.write(cf.head(10))

        #fig = px.scatter_3d(cf.head(10), x='4', y='1', z='2', color='3')

        #fig.update_layout(
        #    margin=dict(l=0, r=0, t=0, b=0),
        #    paper_bgcolor="LightSteelBlue"
        #)

        #st.plotly_chart(fig)
        #st.write("Slider value :",r)
        # nx, ny, ncol = '1', '2', '3' #valeur bouton 1, valeur bouton 2, valeur bouton 3
        # nz = '2'
        fig2D = px.scatter(cf2, x=nx, y=ny, color=ncol)

        fig2D.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="LightSteelBlue",
            xaxis=dict(
                title={
                    'text':f"Axe n° {nx}"},
                titlefont_size=16,
                tickfont_size=14
            ),
            yaxis=dict(
                title={
                    'text':f"Axe n° {ny}"},
                titlefont_size=16,
                tickfont_size=14
            ),
            title={
                "text":f"Films en rapport avec {df_result2['name'][0]}"
            }
        )
        
        name = df_result2["name"][0]
        fig3D = px.scatter_3d(
            data_frame=cf2,
            x=nx,
            y=ny,
            z=nz,
            color=ncol,
            opacity=0.7,
            # color_discrete_map={'Europe': 'black', 'Africa': 'yellow'},
            # symbol='Year',            # symbol used for bubble
            # symbol_map={"2005": "square-open", "2010": 3},
            # size='resized_pop',       # size of bubble
            # size_max=50,              # set the maximum mark size when using size
            # log_x=True,  # you can also set log_y and log_z as a log scale
            # range_z=[9,13],           # you can also set range of range_y and range_x
            # template='ggplot2',         # 'ggplot2', 'seaborn', 'simple_white', 'plotly',
                                        # 'plotly_white', 'plotly_dark', 'presentation',
                                        # 'xgridoff', 'ygridoff', 'gridon', 'none'
            title=f'Films en rapport avec {name}',
            # labels={'name':'name'},
            hover_data={'name': True, 'runtime': ':.1f', 'year':True, f'{nx}':False, f'{ny}':False, f'{nz}':False, f'{ncol}':False},
            hover_name='name',        # values appear in bold in the hover tooltip
            # height=700,                 # height of graph in pixels
            # animation_frame='year',   # assign marks to animation frames
            # range_x=[500,100000],
            # range_z=[0,14],
            # range_y=[5,100]
        )
        fig3D.update_traces(marker_coloraxis=None)
        

        st.plotly_chart(fig2D)
        st.plotly_chart(fig3D)
        st.subheader("{} results".format(len(cf2)))
        if len(cf2) != 0:
            if len(cf2) > 50:
                displayFilms(cf2, 50)
            if len(cf2) < 50:
                displayFilms(cf2, len(cf2))
        else:
            st.markdown("No results")
  
if selected == "About":
    st.title("About us")
    st.markdown("We are a group of 4 students from ESILV who developed this project for all the movie lovers like us 😉.")
