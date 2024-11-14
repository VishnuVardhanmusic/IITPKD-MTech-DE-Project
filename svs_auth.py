from dash import dcc, html, dash, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
import sqlalchemy
import dash_auth
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text

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

qr00 = text('''SELECT * FROM rmovies LIMIT 50;''')
resr00=db.execute_dql_commands(qr00)
dr00 = []
for i in resr00:
    dr00.append([i.id,i.imdb_id,i.popularity,i.budget,i.revenue,i.original_title,i.castc,i.homepage,i.director,i.tagline,i.keywords,i.overview,
                i.runtime,i.genres,i.production_companies,i.release_date,i.vote_count,i.vote_average,i.release_year,i.budget_adj,i.revenue_adj])
dfr00=pd.DataFrame(data=dr00,columns=['id','imdb_id','popularity','budget','revenue','original_title','cast','homepage','director','tagline','keywords','overview','runtime',
'genres','production_companies','release_date','vote_count','vote_average','release_year','budget_adj','revenue_adj'])

q00 = text('''SELECT * FROM movies ORDER BY uid LIMIT 50;''')
res00=db.execute_dql_commands(q00)
d00 = []
for i in res00:
    d00.append([i.uid, i.idi, i.imdb_id, i.popularity, i.budget, i.revenue, i.original_title, i.actor_name, i.director_name, i.runtime, i.genres, i.release_date, i.vote_count, i.vote_average, i.release_year, i.budget_adj, i.revenue_adj])
df00=pd.DataFrame(data=d00,columns=['uid', 'idi', 'imdb_id', 'popularity', 'budget', 'revenue', 'original_title', 'actor_name', 'director_name', 'runtime', 'genres', 'release_date', 'vote_count', 'vote_average', 'release_year', 'budget_adj', 'revenue_adj'])

def create_table():
    fig123 = go.Figure(data=[go.Table(
        header=dict(values=df00.columns, align='left'),
        cells=dict(values=df00.values.T, align='left'))
    ]
    )
    fig123.update_layout(paper_bgcolor="#e5ecf6", margin={"t":2, "l":2, "r":2, "b":0}, height=1000)
    return fig123

def create_rtable():
    fig321 = go.Figure(data=[go.Table(
        header=dict(values=dfr00.columns, align='left'),
        cells=dict(values=dfr00.values.T, align='left'))
    ]
    )
    fig321.update_layout(paper_bgcolor="#e5ecf6", margin={"t":2, "l":2, "r":2, "b":0}, height=1000)
    return fig321

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
    
############### DB QURIES FOR TAB 1 #####################
q5 = text('''SELECT DISTINCT(g.genres),m.popularity, m.revenue
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.revenue > 870000 AND m.popularity IS NOT NULL
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
FROM movie m WHERE m.budget > 3000000.0 AND m.revenue >870000
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
GROUP BY a.actor_name   ORDER BY avg_vote DESC LIMIT 10;''')
res4 = db.execute_dql_commands(q4)
v4 = []
r4 = []
for i in res4:
    v4.append(i.actor_name)
    r4.append(i.avg_vote)
################################
q6 = text('''SELECT g.genres, SUM(m.revenue) AS Total_Revenue
FROM movie m
JOIN movie_genres mg ON m.uid = mg.movie_id 
JOIN genres g ON mg.genre_id = g.genre_id
GROUP BY g.genres
ORDER BY Total_Revenue DESC LIMIT 5;''')
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
q16 = text('''SELECT distinct(m.vote_count),a.actor_name,m.popularity
FROM movie m
JOIN movie_actors ma ON m.uid = ma.movie_id
JOIN actors a ON ma.actor_id = a.actor_id
WHERE  m.vote_count IS NOT NULL
ORDER BY m.vote_count DESC;
''')
res16=db.execute_dql_commands(q16) 
d16 = []
for i in res16:
    d16.append([i.vote_count,i.popularity,i.actor_name])
df16 = pd.DataFrame(d16,columns=['Vote_Count','Popularity_Score','Actor_Name'])
#################################
q19=text('''SELECT EXTRACT(YEAR FROM release_date) AS release_year, 
ROUND(AVG(vote_average),3) AS avg_rating
FROM movie
GROUP BY release_year
ORDER BY avg_rating DESC
LIMIT 4;''')
res19=db.execute_dql_commands(q19)
d19 = []
for i in res19:
    d19.append([i.release_year,i.avg_rating])
df19 = pd.DataFrame(data=d19,columns =['Release Year','Avg Movie Rating'])
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
    ORDER BY total_vote_count DESC LIMIT 10;''')
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
       original_title, ROUND(popularity,2) FROM movie
ORDER BY decade,popularity DESC;''')
res21=db.execute_dql_commands(q21)
d21=[]
for i in res21:
    d21.append([i.decade,i.original_title,i.round])
df21=pd.DataFrame(data=d21,columns=['Year','Movie Title','Popularity Index'])

q111 = text("select corr(popularity,revenue) from movie;")
res111 = db.execute_dql_commands(q111)
for i in res111:
    r111 = i.corr

q112 = text("select corr(popularity,vote_count) from movie;")
res112 = db.execute_dql_commands(q112)
for i in res112:
    r112 = i.corr

############### PLOTLY FIGURES FOR TAB 1 #####################
def qq1():
    fig1 = go.Figure(go.Bar(
    x=v1,
    y=r1,
    orientation='h'))
    fig1.update_layout(
    title={
        "text": "Directors with Most Number of Films",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
    xaxis_title="Number of Films",
    yaxis_title="Director Name",
    autosize=True)

    fig1.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig1

def t1p0():
    return dcc.Graph(figure=qq1())

t1p1 = dcc.Graph(
    id='t1p1',
    figure={
        'data': [
            go.Scatter(
                x=df5.popularity_score,
                y=df5.box_office_revenue,
                mode='markers',
                name='Data Points'
            )
        ],
        'layout': go.Layout(
            autosize=True,
            title={
                'text': "Correlation Between Movie Popularity and its Revenue across Different Genres",
                'xanchor': 'center',
                'yanchor': 'top',
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            },
            xaxis={'title': 'Popularity Scores'},
            yaxis={'title': 'Box Office Revenues'},
            annotations=[
                {
                    'x': 1,
                    'y': 1,
                    'xref': 'paper',
                    'yref': 'paper',
                    'text': f'Correlation Coefficient: {r111:.4f}',
                    'showarrow': False,
                    'xanchor': 'right',
                    'yanchor': 'top',
                    'font': {
                        'size': 16,
                        'color': 'red'
                    }
                }
            ]
        )
    }
)
           
t1p2 = dcc.Graph(
        id = 't1p2',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': v2, 'y':r2,'type':'hist'},
            ],
            'layout':{
                'title': 'Top 5 Movies with the HIGHEST Profit Margin',
                'autosize': True,
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        },
                
            }
        }
)


t1p3 = dcc.Graph(
        id = 't1p3',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': r3, 'y':v3,'type':'bar'},
            ],
            'layout':{
                'title': 'Directors having Most Movies in the Top 100 Grossing Films',
                'autosize': True,
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

t1p4 = dcc.Graph(
    id = 't1p4',
    config={'responsive': True}, 
    figure = {
        'data' : [
            {'x' : d13,'y':r13,'type':'bar','name':'Vote Count'},
            {'x' : d13,'y':v13,'type':'hist','name':'Popularity Score'},
                
            ],
        'layout':{
                'title': 'Top Movies with the Highest Popularity-to-Vote Ratio.',
            'autosize': True,
            "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
    }
)

############### PLOTLY FIGURES FOR TAB 2 #####################

t2p1 = dcc.Graph(
        id = 't2p2',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': v4, 'y':r4,'type':'bar'},
            ],
            'layout':{
                'title': 'Actors having the Highest Avg Vote in Sci-Fi Movies',
                'autosize':True,
                 "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )


t2p2 = dcc.Graph(
        id = 't2p2',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': r6, 'y':v6,'type':'hist'},
            ],
            'layout':{
                'title': 'Box Office Revenue across Different Genres',
                'autosize':True,
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

def qq9():
    fig9 = px.line(df9, x='Release Date', y='Popularity', markers=True)
    fig9.update_layout(
    title={
        "text":"Popularity Scores of the Films released before 2000s",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
    xaxis_title='Release Date',
    yaxis_title='Popularity',
    autosize=True,
    xaxis=dict(tickformat='%Y-%m-%d'),
    template='plotly_white')

    fig9.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig9

def t2p3():
    return dcc.Graph(figure=qq9())

def qq11():
    fig11 = px.line(x=v11, y=r11, title='Top GENRES with their Average Popularity Score')
    fig11.update_layout(
    title={
        "text":"Top GENRES with their Average Popularity Scores",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
    xaxis_title='Average Popularity Score',
    yaxis_title=' ',
    autosize=True,
    )
    fig11.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig11

def t2p4():
    return dcc.Graph(figure=qq11())

t2p5 = dcc.Graph(
    id = 't2p5',
    config={'responsive': True}, 
    figure = {
        'data' : [
            {'x' : d001,'y':r001,'type':'hist','name':'Adj. Budget'},
            {'x' : d001,'y':v001,'type':'hist','name':'Budget'},
                
            ],
        'layout':{
                'title': "Top Movie's Budget and the Budget Adjusted for Inflation",
                'autosize':True,
            "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

t2p6 = dcc.Graph(
    id = 't2p6',
    config={'responsive': True}, 
    figure = {
        'data' : [
            {'x' : d002,'y':r002,'type':'hist','name':'Adj. Revenue'},
            {'x' : d002,'y':v002,'type':'hist','name':'Revenue'},
                
            ],
        'layout':{
                'title': "Top Movie's Revenue and the Revenue Adjusted for Inflation",
                'autosize':True,
            "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

############### PLOTLY FIGURES FOR TAB 3 #####################
t3p1 = dcc.Graph(
        id='t3p1',
        figure = {
            'data':[
                go.Scatter(
                    x=df16.Popularity_Score,
                    y=df16.Vote_Count,
                    mode = 'markers'
                )
            ],
            'layout': go.Layout(
            autosize=True,
            title={
                'text': 'Correlation Between Popularity and Vote Count for different Actors',
                'xanchor': 'center',
                'yanchor': 'top',
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            },
            xaxis = {'title':'Popularity Scores'},
            yaxis = {'title':'Vote Count'},
            annotations=[
                {
                    'x': 1,
                    'y': 1,
                    'xref': 'paper',
                    'yref': 'paper',
                    'text': f'Correlation Coefficient: {r112:.4f}',
                    'showarrow': False,
                    'xanchor': 'right',
                    'yanchor': 'top',
                    'font': {
                        'size': 16,
                        'color': 'red'
                    }
                }
            ]
        )
    }
)
           
def qq15():
    fig15 = go.Figure(go.Bar(
    x=r15,
    y=v15,
    orientation='h'))
    fig15.update_layout(
    title={
        "text":"Number of High Budget Films in the Top Genres",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
    xaxis_title="Number of Films",
    yaxis_title="Genre",
    autosize=True,
    )
    fig15.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig15

def t3p2():
    return dcc.Graph(figure=qq15())

def qq19():
    fig19 = px.line(df19, x='Release Year', y='Avg Movie Rating', markers=True)
    fig19.update_layout(
        title={
        "text":"Top Average Movie Ratings",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
            "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
        xaxis_title='Release Year',
        yaxis_title='Average Rating',
        xaxis=dict(tickformat='%Y', automargin=True),
        yaxis=dict(automargin=True),
        autosize=True
    )
    fig19.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig19

def t3p3():
    return dcc.Graph(figure=qq19())


t3p4 = dcc.Graph(
        id = 't3p4',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': v14, 'y':r14,'type':'bar'},
            ],
            'layout':{
                'title': 'Top Actors with their Highest Total Revenue across all the films they have acted in',
                'autosize':True,
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

t3p5 = dcc.Graph(
        id = 't3p5',
        config={'responsive': True}, 
        figure = {
            'data' : [
                {'x': v20, 'y':r20,'type':'hist'},
            ],
            'layout':{
                'title': 'Top Directors with their Cumulative Vote Counts',
                'autosize':True,
                "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
            }
        }
    )

def qq21():
    yearly_avg = df21.groupby('Year')['Popularity Index'].mean().reset_index()
    fig21 = px.line(yearly_avg, x='Year', y='Popularity Index')
    fig21.update_layout(
    title={
        "text":"Average Popularity Index of the Movies in the Past (1960-2015)",
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {
            "color": "black",
            "family": "Arial",
            "weight": "bold"
        }
    },
    xaxis_title='Year',
    yaxis_title='Average Popularity Index',
    autosize=True,
    )
    fig21.update_annotations([
        dict(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            borderpad=10
        )
    ])
    return fig21

def t3p6():
    return dcc.Graph(figure=qq21())

############### APP LAYOUT #####################
app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"])

auth = dash_auth.BasicAuth(app,USER_PASS_MAPPING)

def create_tab1_content():
    return html.Div([
        html.Div([html.Br(),
            html.Div([html.Br(),t1p0(),html.H5('''Woody Allen with 46 films becomes the Director with most number of films.
            Next would be Clint Eastwood with 34 films directed.''',className="mt-3",style={"wordWrap": "break-word","color":"#4811bf"}),]
                     , className="col-md-5 col-sm-12"),
            html.Div([html.Br(),t1p1,html.H5('''We can infer that, there is a particular Genre with only 9.4 Popularity Score i.e Very Less Popularly Known Genre
            but still managed to collect 2.7 Billion Box Office Revenue.At the same time, there's another Genre with 
            28.4 Popularity Score i.e Very Popular Genre but managed to collect only 378 Million Box Office Revenue.'''
                ,className="mt-3",style={"wordWrap": "break-word","color":"#ff5733"}),], className="col-md-7 col-sm-12"),
        ], className="row"),

        html.Div([
            html.Div([html.Br(),t3p5,html.H5("Christopher Nolan has the Highest Cumulative Vote Count of 41,759"
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#e03910"}),] , className="col-md-6 col-sm-12"),
            html.Div([html.Br(),t1p3,html.H5('''We can conclude Peter Jackson have 6 films in the Top 100 Grossing Films.
            Next comes George Lucas, David Yates and Christopher Nolan each having 4 films.''',
                                   className="mt-3",style={"wordWrap": "break-word","color":"#045457"}),], className="col-md-6 col-sm-12"),
        ], className="row"),
        
        html.Div([
            html.Div([html.Br(),t2p6,html.H4('''We can infer the films "Titanic" & "The Net" have a large margin between the Revenue and the Adjusted Revenue.''',
                                   className="mt-3",style={"wordWrap": "break-word","color":"#055d18"}),], className="col-12 text-center"),
        ], className="row"),
        
        html.Div([
            html.Div([html.Br(),t2p5,html.Br(),], className="col-12 text-center"),
        ], className="row"),
        
    ], className="container-fluid")

def create_tab2_content():
    return html.Div([html.Br(),
        html.Div([
            html.Div([
            html.Div([html.Br(),t2p3(),html.H4('''We can infer that there was a Film released on 
            20th March 1977 which acquired the maximum Popularity Score. The film is "Star Wars".'''
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#69c908"}),html.Br(),], className="col-12 text-center"),
        ], className="row"),
            
            html.Div([t2p1,html.H5('''We can conclude there are 4 Actors - [Jon Hamm, Oona Chaplin, Rafe Spall, Janet Montgomery] 
            who have the Highest Average Voting of 8.80 in the Scientific Fictional Films.''',className="mt-3",style={"wordWrap": "break-word","color":"#f57105"}),]
                     , className="col-md-6 col-sm-12"),
            html.Div([t2p2,html.H5("We can infer that Comedy and Drama Genre Films out performed near the Box Office",className="mt-3",style={"wordWrap": "break-word","color":"#75990e"}),]
                     , className="col-md-6 col-sm-12"),
        ], className="row"),
                                         
        html.Div([
            html.Div([html.Br(),t2p4(),html.H4('''We can say that the People are more
            inclinded towards Adventurous, Science Fictional Thrillers. More Popularity was gained by the Action Drama Films.'''
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#6411c2"}),], className="col-12 text-center"),
        ], className="row"),
         html.Div([
            html.Div([t1p4,html.Br(),html.Br(),], className="col-12 text-center"),
        ], className="row"),
        
    ], className="container-fluid")

def create_tab3_content():
    return html.Div([
         html.Div([
            html.Div([html.Br(),t3p6(),html.H4("We can clearly visualize that through the years, there was a steady rise in the Popularity of Films."
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#450b52"}),], className="col-12 text-center"),
        ], className="row"),
        
        html.Div([
            html.Div([html.Br(),t3p1,html.H5('''We can clearly see a near to Unity Correlation Coefficient 
            between an Actor's Popularity Score and his/her Vote Counts. This tells who has much votes that one is more Popular.''',className="mt-3",style={"wordWrap": "break-word","color":"#59b507"}),]
                     , className="col-md-6 col-sm-12"),
            html.Div([html.Br(),t3p3(),html.H5('''We can conclude that the year 1973 released
            many Good Rated Films. Recorded the Highest Average Rating of 6.7''',className="mt-3",style={"wordWrap": "break-word","color":"#25028d"}),]
                     , className="col-md-6 col-sm-12"),
        ], className="row"),   
        
        html.Div([
            html.Div([html.Br(),t3p4,html.H4("Harrison Ford stoods first having 8,922,840,695 (8.9 Billion approx) Total Revenue."
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#ba007f"}),] , className="col-12 text-center"),
        ], className="row"),
        html.Div([
            html.Div([html.Br(),t1p2,html.H5(''' E.T. the Extra-Terrestrial Film stands at the peak having the maximum Revenue 
            to Budget Ratio''' ,className="mt-3",style={"wordWrap": "break-word","color":"#059a0e"}),], className="col-md-6 col-sm-12"),
             html.Div([html.Br(),t3p2(),html.H5("There are 170 High Budget Films directed in Comedy Genre. "
                            ,className="mt-3",style={"wordWrap": "break-word","color":"#6411c2"}),], className="col-md-6 col-sm-12"),
        ], className="row"),                       
        
    ], className="container-fluid")

def create_tab4_content():
    return html.Div([html.Br(),
        html.H4("The Dataset used in depicting the Plots and Insights."),        
        html.Div([
            html.Div([html.Br(),dcc.Graph(id="pdata", figure=create_table()),html.Br(),html.Br(),], className="col-12 text-center"),
        ], className="row"),        
    ], className="container-fluid")

def create_tab5_content():
    return html.Div([html.Br(),
        html.H4("The Raw Dataset (before Preprocessing) "),        
        html.Div([
            html.Div([html.Br(),dcc.Graph(id="rdata", figure=create_rtable()),html.Br(),html.Br(),], className="col-12 text-center"),
        ], className="row"),        
    ], className="container-fluid")
    
# DASHBOARD 
app.layout = html.Div([
    html.Br(),
    
    html.Div([
    html.H1("SVS(Shiva Vishnu Sanjiv) DATA ANALYTICS",style={'color':"#890bf8",
                        "text-align": "center",'font-weight': "bold",'text-shadow': "2px 2px 4px rgba(0, 0, 0, 0.3)"}),
    html.H2("MOVIE DATA ANALYSIS AND INSIGHTS VISUALIZATION",style={'color':"#eb0dcd",
                            "text-align": "center",'font-weight': "bold",'text-shadow': "2px 2px 4px rgba(0, 0, 0, 0.3)"}),
    ]),
    html.Br(),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Report 1', value='tab-1'),
        dcc.Tab(label='Report 2', value='tab-2'),
        dcc.Tab(label='Report 3', value='tab-3'),
        dcc.Tab(label='Preprocessed Dataset', value='tab-4'),
        dcc.Tab(label='Raw Dataset', value='tab-5'),
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
    if tab in ['tab-5']:
        return create_tab5_content()
if __name__ == '__main__':
    app.run_server(debug=True)                        