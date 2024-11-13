from dash import dcc, html, dash, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text
import dash_auth

#Defining DB Credentials
USER_NAME = 'postgres'
PASSWORD = 'padder'
PORT = 5432
DATABASE_NAME = 'movies'
HOST = 'localhost'

class PostgresqlDB:
    def __init__(self,user_name,password,host,port,db_name):
        self.user_name = user_name
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.engine = self.create_db_engine()

    def create_db_engine(self):
        try:
            db_uri = 'postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{db_name}'.format(
                      user_name=self.user_name,password=self.password,
                      host=self.host,db_name=self.db_name,port=self.port)
            return create_engine(db_uri)
        except Exception as err:
            raise RuntimeError(f'Failed to establish connection -- {err}') from err

    def execute_dql_commands(self,stmnt,values=None):
        try:
            with self.engine.connect() as conn:
                if values is not None:
                    result = conn.execute(stmnt,values)
                else:
                    result = conn.execute(stmnt)
            return result
        except Exception as err:
            print(f'Failed to execute dql commands -- {err}')
            
db = PostgresqlDB(user_name=USER_NAME,password=PASSWORD,host=HOST,port=PORT,db_name=DATABASE_NAME)
USER_PASS_MAPPING = {"admin":"1234"}

q00 = text('''SELECT * FROM movies LIMIT 50;''')
res00=db.execute_dql_commands(q00)
d00 = []
for i in res00:
    d00.append([i.uid, i.idi, i.imdb_id, i.popularity, i.budget, i.revenue, i.original_title, i.actor_name, i.director_name, i.runtime, i.genres, i.release_date, i.vote_count, i.vote_average, i.release_year, i.budget_adj, i.revenue_adj])
df00=pd.DataFrame(data=d00,columns=['uid', 'idi', 'imdb_id', 'popularity', 'budget', 'revenue', 'original_title', 'actor_name', 'director_name', 'runtime', 'genres', 'release_date', 'vote_count', 'vote_average', 'release_year', 'budget_adj', 'revenue_adj'])

q001 = text('''SELECT DISTINCT(original_title),budget
,budget_adj FROM movies ORDER BY budget DESC LIMIT 15;''')
res001 = db.execute_dql_commands(q001)
d001 = []
v001 = []
r001 = []
for i in res001:
    d001.append(i.original_title)
    v001.append(i.budget)
    r001.append(i.budget_adj)

q002 = text('''SELECT DISTINCT(original_title),revenue
,revenue_adj FROM movies ORDER BY revenue DESC LIMIT 15;''')
res002 = db.execute_dql_commands(q002)
d002 = []
v002 = []
r002 = []
for i in res002:
    d002.append(i.original_title)
    v002.append(i.revenue)
    r002.append(i.revenue_adj)

def create_table():
    fig = go.Figure(data=[go.Table(
        header=dict(values=df00.columns, align='left'),
        cells=dict(values=df00.values.T, align='left'))
    ]
    )
    fig.update_layout(paper_bgcolor="#e5ecf6", margin={"t":2, "l":2, "r":2, "b":0}, height=600)
    return fig

############### DB QURIES FOR TAB 1 #####################
q5 = text('''SELECT DISTINCT(g.genres),m.popularity, m.revenue
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.revenue > 0 AND m.popularity IS NOT NULL
ORDER BY m.popularity DESC;''')
res5 = db.execute_dql_commands(q5)
d5 = []
for i in res5:
    d5.append([i.genres,i.popularity,i.revenue])
df5 = pd.DataFrame(d5,columns=['genre_name','popularity_score','box_office_revenue'])
################################
q1 = text('''SELECT d.director_name, COUNT(m.uid) AS movie_count
FROM directors d
INNER JOIN movie_directors md ON d.director_id = md.director_id
INNER JOIN movie m ON md.movie_id = m.uid
WHERE d.director_name NOT LIKE 'No Info about Director'
GROUP BY d.director_name ORDER BY movie_count DESC LIMIT 5;''')
res1 = db.execute_dql_commands(q1)
r1 = []
v1 = []
for i in res1:
    r1.append(i.director_name)
    v1.append(i.movie_count)
################################
q2 = text('''SELECT m.original_title, (m.revenue / m.budget) AS profit_margin
FROM movie m WHERE m.budget > 0 AND m.revenue > 0
ORDER BY profit_margin DESC LIMIT 5;''')
res2 = db.execute_dql_commands(q2)
v2 = []
r2 = []
for i in res2:
    v2.append(i.original_title)
    r2.append(i.profit_margin)
################################    
q3 = text('''WITH top_grossing_movies AS (
    SELECT uid
    FROM movie
    ORDER BY revenue DESC
    LIMIT 100)
SELECT d.director_name, COUNT(md.movie_id) AS movie_count
FROM directors d
INNER JOIN movie_directors md ON d.director_id = md.director_id
INNER JOIN top_grossing_movies tgm ON md.movie_id = tgm.uid
INNER JOIN movie m ON tgm.uid = m.uid
GROUP BY d.director_name ORDER BY movie_count DESC LIMIT 5;''')
r3 = []
v3 = []
res3 = db.execute_dql_commands(q3)
for i in res3:
    v3.append(i.movie_count)
    r3.append(i.director_name)
################################
q13 = text('''SELECT original_title, ROUND(popularity,3), vote_count, 
       ROUND((popularity / NULLIF(vote_count, 0)),3) AS popularity_to_vote_ratio
FROM movie
ORDER BY popularity_to_vote_ratio DESC
LIMIT 10;''')
res13=db.execute_dql_commands(q13)
d13 = []
v13 = []
r13 = []
for i in res13:
    d13.append(i.original_title)
    v13.append(i.round)
    r13.append(i.vote_count)
    
############### DB QURIES FOR TAB 2 #####################
q4 = text('''WITH sci_fi_movies AS (
    SELECT m.uid
    FROM movie m
    JOIN movie_genres mg ON m.uid = mg.movie_id
    JOIN genres g ON mg.genre_id = g.genre_id
    WHERE g.genres LIKE '%Science Fiction%'
)
SELECT a.actor_name, ROUND(AVG(m.vote_average),2) AS avg_vote
FROM actors a
JOIN movie_actors ma ON a.actor_id = ma.actor_id
JOIN sci_fi_movies sfm ON ma.movie_id = sfm.uid
JOIN movie m ON sfm.uid = m.uid
GROUP BY a.actor_name   ORDER BY avg_vote DESC LIMIT 1;''')
res4 = db.execute_dql_commands(q4)
for i in res4:
    l4 = i.actor_name
    r4 = i.avg_vote
################################
q6 = text('''SELECT g.genres, SUM(m.revenue) AS Total_Revenue
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id 
JOIN genres g ON mg.genre_id = g.genre_id
GROUP BY g.genres
ORDER BY Total_Revenue DESC LIMIT 9;''')
res6 = db.execute_dql_commands(q6)
r6 = []
v6 = []
for i in res6:
    r6.append(i.genres)
    v6.append(i.total_revenue)
################################
q9 = text('''SELECT original_title, release_date, popularity
FROM movie WHERE release_date < '2000-01-01'ORDER BY popularity DESC;''')
res9 = db.execute_dql_commands(q9)
d9 = []
for i in res9:
    d9.append([i.original_title,i.release_date,i.popularity])
df9 = pd.DataFrame(data=d9,columns=['Movie Title','Release Date','Popularity'])
df9['Release Date'] = pd.to_datetime(df9['Release Date'])
df9 = df9.sort_values(by="Release Date")
################################
q11=text('''SELECT g.genres, ROUND(AVG(m.popularity),3) AS avg_popularity
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
GROUP BY g.genres
ORDER BY avg_popularity DESC
LIMIT 10;''')
res11 = db.execute_dql_commands(q11)

r11 = []
v11 = []
for i in res11:
    r11.append(i.genres)
    v11.append(i.avg_popularity)
    
############### DB QURIES FOR TAB 3 #####################
q15=text('''SELECT g.genres, COUNT(m.uid) AS high_budget_movie_count
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.budget > (SELECT AVG(budget) FROM movie)
GROUP BY g.genres
ORDER BY high_budget_movie_count DESC LIMIT 6;''')
res15=db.execute_dql_commands(q15)
v15=[]
r15 = []
for i in res15:
    v15.append(i.genres)
    r15.append(i.high_budget_movie_count)
#################################
q16=text("SELECT CORR(popularity, vote_average) FROM movie;")
res16=db.execute_dql_commands(q16) 
for i in res16:
    v16 = i.corr
r16 = "Corr Score"
#################################
q19=text('''SELECT EXTRACT(YEAR FROM release_date) AS release_year, 
ROUND(AVG(vote_average),3) AS avg_rating
FROM movie
GROUP BY release_year
ORDER BY avg_rating DESC
LIMIT 1;''')
res19=db.execute_dql_commands(q19)
for i in res19:
    v19 = i.release_year
    r19 = i.avg_rating
#################################
q14 = text('''SELECT a.actor_name, SUM(m.revenue) AS total_revenue
FROM actors a
JOIN movie_actors ma ON a.actor_id = ma.actor_id
JOIN movie m ON ma.movie_id = m.uid
GROUP BY a.actor_name
ORDER BY total_revenue DESC
LIMIT 15;''')
res14=db.execute_dql_commands(q14)
v14=[]
r14=[]
for i in res14:
    v14.append(i.actor_name)
    r14.append(i.total_revenue)
#################################
q20 = text('''SELECT d.director_name, SUM(m.vote_count) AS total_vote_count
FROM directors d
JOIN movie_directors md ON d.director_id = md.director_id
JOIN movie m ON md.movie_id = m.uid
GROUP BY d.director_name
ORDER BY total_vote_count DESC LIMIT 20;
''')
res20 = db.execute_dql_commands(q20)
d20 =[]
v20 = []
r20 = []
for i in res20:
    v20.append(i.director_name)
    r20.append(i.total_vote_count)
    d20.append([i.director_name,i.total_vote_count])
df20=pd.DataFrame(data=d20,columns=['Director Name','Total Vote Count'])

#################################
q21 = text('''SELECT ROUND((EXTRACT(YEAR FROM release_date) / 10 * 10),0) AS decade, 
       original_title, ROUND(popularity,2)
FROM movie
ORDER BY decade, popularity DESC;''')
res21=db.execute_dql_commands(q21)
d21=[]
for i in res21:
    d21.append([i.decade,i.original_title,i.round])
df21=pd.DataFrame(data=d21,columns=['Year','Movie Title','Popularity Index'])

############### PLOTLY FIGURES FOR TAB 1 #####################
def qq1():
    fig1 = go.Figure(go.Bar(
    x=v1,
    y=r1,
    orientation='h'))
    fig1.update_layout(
    title="Directors with most number of films directed",
    xaxis_title="Number of Films",
    yaxis_title="Director Name")
    return fig1

def t1p0():
    return dcc.Graph(figure=qq1())

t1p1 = dcc.Graph(
        id='t1p1',
        figure = {
            'data':[
                go.Scatter(
                    x=df5.popularity_score,
                    y=df5.box_office_revenue,
                    mode = 'markers'
                )
            ],
            'layout':go.Layout(
                title = 'Correlation Between Popularity Scores and Revenue',
                xaxis = {'title':'Popularity Scores'},
                yaxis = {'title':'Box Office Revenues'}
            )
        }
    )

t1p2 = dcc.Graph(
        id = 't1p2',
        figure = {
            'data' : [
                {'x': v2, 'y':r2,'type':'hist'},
            ],
            'layout':{
                'title': 'Top 5 Movies with the HIGHEST Profit Margin'
            }
        }
    )

t1p3 = dcc.Graph(
        id = 't1p3',
        figure = {
            'data' : [
                {'x': r3, 'y':v3,'type':'bar'},
            ],
            'layout':{
                'title': 'Directors having most movies in the top 100 grossing films'
            }
        }
    )

t1p4 = dcc.Graph(
    id = 't1p4',
    figure = {
        'data' : [
            {'x' : d13,'y':r13,'type':'bar','name':'Vote Count'},
            {'x' : d13,'y':v13,'type':'hist','name':'Popularity Score'},
                
            ],
        'layout':{
                'title': 'Top 10 Movies with the Highest Popularity-to-Vote Ratio.'
            }
    }
)

############### PLOTLY FIGURES FOR TAB 2 #####################
t2p1 = dcc.Graph(
        id='t2p1',
        figure={
            'data': [
                go.Pie(
                    labels=[l4],
                    values=[r4],
                    showlegend=False,
                    textinfo='label+value',
                    hoverinfo='label+value+percent'
                )
            ]
        }
)

t2p2 = dcc.Graph(
        id = 't2p2',
        figure = {
            'data' : [
                {'x': r6, 'y':v6,'type':'bar'},
            ],
            'layout':{
                'title': 'Total Box Office Revenue across Different Genres'
            }
        }
    )

def qq9():
    fig9 = px.line(df9, x='Release Date', y='Popularity', title='Popularity Scores of the films released before 2000s', markers=True)
    fig9.update_layout(
    xaxis_title='Release Date',
    yaxis_title='Popularity',
    xaxis=dict(tickformat='%Y-%m-%d'),
    template='plotly_white')
    return fig9

def t2p3():
    return dcc.Graph(figure=qq9())

def qq11():
    fig11 = px.line(x=v11, y=r11, title='Top GENRES with their Average Popularity Score')
    fig11.update_layout(
    xaxis_title='Average Popularity Score',
    yaxis_title=' ')
    return fig11

def t2p4():
    return dcc.Graph(figure=qq11())

t2p5 = dcc.Graph(
    id = 't2p5',
    figure = {
        'data' : [
            {'x' : d001,'y':r001,'type':'hist','name':'Adjusted Budget'},
            {'x' : d001,'y':v001,'type':'hist','name':'Budget'},
                
            ],
        'layout':{
                'title': "Top Movie's Actual Budget and the Budget adjusted for inflation"
            }
        }
    )

t2p6 = dcc.Graph(
    id = 't2p6',
    figure = {
        'data' : [
            {'x' : d002,'y':r002,'type':'hist','name':'Adjusted Revenue'},
            {'x' : d002,'y':v002,'type':'hist','name':'Revenue'},
                
            ],
        'layout':{
                'title': "Top Movie's Actual Revenue and the Revenue adjusted for inflation"
            }
        }
    )

############### PLOTLY FIGURES FOR TAB 3 #####################
t3p1 = dcc.Graph(
        id='t3p1',
        figure={
            'data': [
                go.Pie(
                    labels=[r16],
                    values=[v16],
                    hole=0.5,  
                    showlegend=False,
                    textinfo='label+value',
                    hoverinfo='label+value+percent'
                )
            ]
        }
)

def qq15():
    fig15 = go.Figure(go.Bar(
    x=r15,
    y=v15,
    orientation='h'))
    fig15.update_layout(
    title="Number of High Budget Movies in each Genre",
    xaxis_title="Number of Films",
    yaxis_title="Genre")
    return fig15

def t3p2():
    return dcc.Graph(figure=qq15())

t3p3 = dcc.Graph(
        id='t2p1',
        figure={
            'data': [
                go.Pie(
                    labels=[v19],
                    values=[r19],
                    showlegend=False,
                    hole=0.6,  
                    textinfo='label+value',
                    hoverinfo='label+value+percent'
                )
            ]
        }
)

t3p4 = dcc.Graph(
        id = 't3p4',
        figure = {
            'data' : [
                {'x': v14, 'y':r14,'type':'bar'},
            ],
            'layout':{
                'title': 'Top Actors with their highest Total Revenue across all the films they have acted in'
            }
        }
    )

t3p5 = dcc.Graph(
        id = 't1p2',
        figure = {
            'data' : [
                {'x': v20, 'y':r20,'type':'hist'},
            ],
            'layout':{
                'title': 'Top 5 Movies with the HIGHEST Profit Margin'
            }
        }
    )

def qq21():
    yearly_avg = df21.groupby('Year')['Popularity Index'].mean().reset_index()
    fig21 = px.line(yearly_avg, x='Year', y='Popularity Index', title='Average Movie Popularity Index (1960-2015)')
    fig21.update_layout(
    xaxis_title='Year',
    yaxis_title='Average Popularity Index',)
    return fig21

def t3p6():
    return dcc.Graph(figure=qq21())

############### APP LAYOUT #####################
app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"])

auth = dash_auth.BasicAuth(app,USER_PASS_MAPPING)

server = app.server

def create_graph(title):
    return dcc.Graph(
        figure=go.Figure(
            data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 3], mode='lines+markers')],
            layout=go.Layout(title=title)
        )
    )

def create_tab1_content():
    return html.Div([
        html.Div([html.Br(),
            html.Div([html.Br(),t1p0(),html.H4('''Woody Allen with 230 films becomes the Director with most number of films.
            Next would be Clint Eastwood with 171 films directed.''',className="mt-3",style={"wordWrap": "break-word","color":"#4811bf"}),]
                     , className="col-md-6 col-sm-12"),
            html.Div([html.Br(),t1p1,html.H4('''We can infer that there is a Movie with only 9.4 Popularity Score but still managed to claim 2.7 Billion Box Office Revenue. 
            At the same time, there's another Movie with 28.4 Popularity Score but managed only to collect 378 Million Box Office Revenue.'''
                ,className="mt-3",style={"wordWrap": "break-word","color":"#eb2710"}),], className="col-md-6 col-sm-12"),
        ], className="row"),
         html.Div([
            html.Div([html.Br(),t2p6,html.Br(),], className="col-12 text-center"),
        ], className="row"),
        html.Div([
            html.Div([t1p2,html.H4('''We can conclude that the movie - "The Karate Kid, Part II" stands away from the rest of the competitors by large margin.'''
                ,className="mt-3",style={"wordWrap": "break-word","color":"#dd810c"}),], className="col-md-6 col-sm-12"),
            html.Div([t1p3,html.H4('''Top Grossing Films obtained in terms of Box Office Revenue the movie collected and 
            Peter Jackson with 30 films becomes the Director having most number of movies in the Top 100.''',className="mt-3",style={"wordWrap": "break-word","color":"#3df505"}),], className="col-md-6 col-sm-12"),
        ], className="row"),
        
        html.Div([
            html.Div([t1p4,html.Br(),html.Br(),], className="col-12 text-center"),
        ], className="row"),
    ], className="container-fluid")

def create_tab2_content():
    return html.Div([html.Br(),
        html.Div([
            html.Div([t2p1,html.H4("Actor having the Highest Average Vote in Scientific-Fictional Movies",className="mt-3"),]
                     , className="col-md-4 col-sm-12",style={"wordWrap": "break-word","color":"#f57105"}),
            html.Div([t2p2,html.H4("We can infer that Comedy and Drama Genre films out performed near the Box Office",className="mt-3"),]
                     , className="col-md-8 col-sm-12",style={"wordWrap": "break-word","color":"#3df505"}),
        ], className="row"),
                     
        html.Div([
            html.Div([html.Br(),t2p5,html.Br(),], className="col-12 text-center"),
        ], className="row"),
                     
        html.Div([
            html.Div([html.Br(),t2p3(),html.Br(),], className="col-12 text-center"),
        ], className="row"),
                     
        
        
        html.Div([
            html.Div([html.Br(),t2p4(),html.Br(),], className="col-12 text-center"),
        ], className="row"),
        
    ], className="container-fluid")

def create_tab3_content():
    return html.Div([
         html.Div([
            html.Div([html.Br(),t3p6(),html.Br(),], className="col-12 text-center"),
        ], className="row"),
        
        html.Div([
            html.Div([html.Br(),t3p1,html.H4("The Correlation between a Movie's Popularity Score and it's Average Vote Count is 0.209",className="mt-3"),]
                     , className="col-md-3 col-sm-12",style={"wordWrap": "break-word","color":"#59b507"}),
            html.Div([html.Br(),t3p2()], className="col-md-6 col-sm-12"),
            html.Div([html.Br(),t3p3,html.H4("1973 is the year with HIGHEST Average Movie Rating of 6.704",className="mt-3"),]
                     , className="col-md-3 col-sm-12",style={"wordWrap": "break-word","color":"#25028d"}),
        ], className="row"),   
        
        html.Div([
            html.Div([html.Br(),t3p4,html.H4("Cameron Diaz stoods first having 10,491,168,565 (10.5 Billion approx) Total Revenue generated from all her Films."
                            ,className="mt-3"),] , className="col-12 text-center",style={"wordWrap": "break-word","color":"#ba007f"}),
        ], className="row"),

        html.Div([
            html.Div([html.Br(),t3p5,html.H4("Christopher Nolan stands first having the Highest Cumulative Vote Count of 208K for his Movies."
                            ,className="mt-3"),] , className="col-12 text-center",style={"wordWrap": "break-word","color":"#e03910"}),
        ], className="row"),                       
        
    ], className="container-fluid")

def create_tab4_content():
    return html.Div([html.Br(),
        html.H4("The Dataset used in depicting the plots and insights"),        
        html.Div([
            html.Div([html.Br(),dcc.Graph(id="dataset", figure=create_table()),html.Br(),html.Br(),], className="col-12 text-center"),
        ], className="row"),        
    ], className="container-fluid")
    
# DASHBOARD 
app.layout = html.Div([
    html.Br(),
    html.Div([
    html.H1("SVS(Shiva Vishnu Sanjiv) DATA ANALYTICS",style={'color':"#890bf8","text-align": "center"}),
    html.H2("MOVIE DATA ANALYSIS AND INSIGHTS VISUALIZATION",style={'color':"#eb0dcd","text-align": "center"}),
    ]),
    html.Br(),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Report 1', value='tab-1'),
        dcc.Tab(label='Report 2', value='tab-2'),
        dcc.Tab(label='Report 3', value='tab-3'),
        dcc.Tab(label='Preprocessed Dataset', value='tab-4'),
    ]),
    html.Div(id='tabs-content')
],style={"background-color": "#e5ecf6"})

# Callback to render content based on tab selection
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab in ['tab-1']:
        return create_tab1_content()
    if tab in ['tab-2']:
        return create_tab2_content()
    if tab in ['tab-3']:
        return create_tab3_content()
    if tab in ['tab-4']:
        return create_tab4_content()

if __name__ == '__main__':
    app.run_server(debug=False)                        