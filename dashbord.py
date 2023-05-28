# Importing the required libraries

import bs4
import requests
import time
import random as ran
import sys
import pandas as pd

# importing plotly
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

"""Building the function required to scrape the website"""
def scrape_movies_data():
    """Scrape movies data from IMDb's Top 150 movies page and saves it to a CSV file.
        Returns:
        dataframe: a table containe all information about top ranked movies"""
    
    step=0
    
    movie_list = []
    while step<=250:
        url=f"https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={step}&ref_=adv_nxt"
        resp = requests.get(url)
        content = bs4.BeautifulSoup(resp.content, 'html.parser')


        for movie in content.select('.lister-item-content'):
            
            try:

                data = {
                "title":movie.find('a').get_text().strip(),
                "year":movie.select('.lister-item-year')[0].get_text().strip()[1:-1],
                "time(min)":int(movie.select('.runtime')[0].get_text().strip()[0:-3]),
                "genre":movie.select('.genre')[0].get_text().strip(),
                "rating":float(movie.select('.ratings-imdb-rating')[0].get_text().strip()),
                "metascore":int(movie.select('.ratings-metascore')[0].get_text().strip()[0:4]),
                "simple_desc":movie.select('.text-muted')[2].get_text().strip(),
                "votes":int(movie.select('.sort-num_votes-visible')[0].findAll('span')[1].get_text().strip().replace(",", "")),
                "Gross (M$)":float(movie.select('.sort-num_votes-visible')[0].findAll('span')[4].get_text().strip()[1:-1])



            }
            except IndexError:
                continue

            movie_list.append(data)
        step+=50
        
    dataframe = pd.DataFrame(movie_list)
    return dataframe


"""Building the plotting functions"""

def create_stacked_bar_plot(df,keyword='genre'):
    """ This function will create a stacked bar plot where each bar represents a genre,
      and the segments within the bar represent the total gross revenue for each genre or year. 
      The x-axis represents the genres or the year, and the y-axis represents the total gross revenue in millions of dollars.
    This plot allows us to compare and analyze the revenue contribution of different genres(year) in a stacked manner."""
    genre_gross = df.groupby(keyword)['Gross (M$)'].sum().sort_values(ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=genre_gross.index, y=genre_gross,
                         marker=dict(color='rgba(50, 171, 96, 0.6)'),
                         name='Gross Revenue'))

    fig.update_layout(
        title=f'Total Gross Revenue by {keyword}',
        xaxis=dict(title=f'{keyword}'),
        yaxis=dict(title='Total Gross Revenue (M$)'),
        barmode='stack'
    )

    return fig


def create_duration_histogram(df):
    """This function will create a histogram where the x-axis represents the movie durations in minutes,
    and the y-axis represents the frequency or count of movies falling within different duration ranges.
    The nbinsx parameter is used to control the number of bins or bars in the histogram. 
     This plot allow us to easily identify the duration of the most succeed movies 
"""
    durations = df['time(min)']
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(x=durations, nbinsx=20,
                               marker=dict(color='rgba(58, 71, 80, 0.6)'),
                               name='Movie Durations'))

    fig.update_layout(
        title='Distribution of Movie Durations',
        xaxis=dict(title='Duration (minutes)'),
        yaxis=dict(title='Frequency'),
    )

    return fig


def create_year_bar_plot(df):
    average_ratings = df.groupby('year')['rating'].mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=average_ratings.index, y=average_ratings,
                         marker=dict(color='rgba(31, 119, 180, 0.6)'),
                         name='Average Rating'))

    fig.update_layout(
        title='Average Movie Ratings by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Average Rating'),
    )

    return fig


import plotly.graph_objects as go

def create_year_count_bar_plot(df):
    
    """ This function will create a bar plot where each bar represents a year,
    and the height of each bar represents the number of movies released in that year.
    The x-axis represents the years, and the y-axis represents the count of movies.
    This plot allows you to easily identify the year with the most succeed movies and observe 
    any fluctuations or trends in the number of movies over time."""
    
    
    year_counts = df['year'].value_counts().sort_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=year_counts.index, y=year_counts,
                         marker=dict(color='rgba(31, 119, 180, 0.6)'),
                         name='Number of Movies'))

    fig.update_layout(
        title='Number of Movies by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Number of Movies'),
    )

    return fig

def create_gross_scatter_plot(df,keyword='votes'):
    """This function will create a scatter plot where each point represents a movie. 
    The x-axis represents the number of votes (audience engagement), 
    and the y-axis represents the gross revenue (commercial success) in millions of dollars. 
    This plot allows you to visualize the relationship between
    audience engagement and commercial success for the movies in terms of votes and gross revenue."""
    votes = df[keyword]
    gross_revenue = df['Gross (M$)']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=votes, y=gross_revenue,
                             mode='markers',
                             marker=dict(color='rgba(31, 119, 180, 0.6)'),
                             name='Movies'))

    fig.update_layout(
        title=f'Number of {keyword} vs Gross Revenue',
        xaxis=dict(title=f'Number of {keyword}'),
        yaxis=dict(title='Gross Revenue (M$)'),
    )

    return fig

    
# Calling the function
df =scrape_movies_data()

"""Building the app"""
# ---------------------------------------------------------------------------

# Initializing the app
app = dash.Dash(__name__)
server = app.server

# Building the app layout
app.layout = html.Div([
    html.H1("Movies statistic DashBoard", style={"text-align": "center"}),
    html.Br(),
    html.Div([
        html.Br(),
        html.H2("Compare and Analyze the revenue contribution of movies", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_revenue_attribute",
                     options=[
                         dict(label="revenue contribution of different genre", value='genre'),
                         dict(label="revenue contribution of different year", value='year')
                     ],
                     multi=False,
                     value="genre",
                     style={"width": "50%"}
                     ),
        
        dcc.Graph(id="revenue_bar", figure=create_stacked_bar_plot(df))
    ]),
        html.Div([
        html.Br(),
        html.H2("Distribution of the movies duration", style={"text-align": "center"}),
        html.Br(),
      
        dcc.Graph(id="duration_histogram", figure=create_duration_histogram(df))
    ]),
        html.Div([
        html.Br(),
        html.H2("Movies rating by year", style={"text-align": "center"}),
        html.Br(),
      
        dcc.Graph(id="year_barplot", figure=create_year_bar_plot(df))
    ]),
      html.Div([
        html.Br(),
        html.H2("Number of movies realised by year", style={"text-align": "center"}),
        html.Br(),
      
        dcc.Graph(id="year_count", figure=create_year_count_bar_plot(df))
    ]),
     html.Div([
        html.Br(),
        html.H2("scater plot for the correlation", style={"text-align": "center"}),
        html.Br(),
         dcc.Dropdown(id="select_gross_scater",
                     options=[
                         dict(label="scater plot of groos and votes", value='votes'),
                         dict(label="scater plot of groos and metascore", value='metascore')
                     ],
                     multi=False,
                     value="votes",
                     style={"width": "50%"}
                     ),
      
        dcc.Graph(id="gross_scater", figure=create_gross_scatter_plot(df))
    ]),


])

# Defining the application callbacks

@app.callback(
    Output("revenue_bar", "figure"),
    Input("select_revenue_attribute", "value")
)
def update_stacked_bar_plot(value):
    return create_stacked_bar_plot(df, keyword=value)

@app.callback(
    Output("gross_scater", "figure"),
    Input("select_gross_scater", "value")
)
def update_stacked_bar_plot(value):
    return create_gross_scatter_plot(df, keyword=value)


if __name__ == "__main__":
    df = scrape_movies_data()
    app.run_server()