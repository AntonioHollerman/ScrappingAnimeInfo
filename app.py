from dash import Dash, html, dcc, Input, Output, callback
from statistics import mean
import plotly.express as px
import pandas as pd
import psycopg2 as pg2

con_info = {
    "host": "dpg-cl83kpqvokcc73arta6g-a.ohio-postgres.render.com",
    "port": "5432",
    "database": "animedb_67jg",
    "user": "animedb_67jg_user",
    "password": "snOlYgTWY9nhwwPE0RamVnYz5P5zrxT2"
}
db_conn = pg2.connect(**con_info)
db_cur = db_conn.cursor()
db_cur.execute("SELECT * FROM animeinfo WHERE rating is not null")
df = pd.DataFrame(db_cur.fetchall())
df.columns = ['anime_id', 'anime_name', 'description', 'rating', 'studio', 'themes', 'categories', 'eps',
              'mins_per_epi']
df.set_index('anime_id', inplace=True)


def get_cat_data(x_input, slider_val):
    min_, max_ = slider_val
    if x_input == 'Studio':
        temp_df = df.groupby('studio').agg({'studio': 'count', 'rating': 'mean'}).rename(
            columns={'studio': 'count'}).reset_index()
        temp_df.sort_values('count', ascending=False, inplace=True)
        temp_df.columns = ['X', 'count', 'rating']
    elif x_input == 'Themes':
        themes = {}
        temp_df = []
        for index, row in df.iterrows():
            anime_themes = row.themes.split(", ")
            for theme in anime_themes:
                if theme in themes:
                    themes[theme].append(float(row.rating))
                else:
                    themes[theme] = [float(row.rating)]
        for key, item in themes.items():
            temp_df.append({'theme': key, 'rating': mean(item), 'count': len(item)})
        temp_df = pd.DataFrame(temp_df, columns=['theme', 'rating', 'count'])
        temp_df.columns = ['X', 'rating', 'count']
        temp_df.sort_values('count', ascending=False, inplace=True)
    else:
        categories = {}
        temp_df = []
        for index, row in df.iterrows():
            anime_categories = row.categories.split(", ")
            for category in anime_categories:
                if category in categories:
                    categories[category].append(float(row.rating))
                else:
                    categories[category] = [float(row.rating)]
        for key, item in categories.items():
            temp_df.append({'category': key, 'rating': mean(item), 'count': len(item)})
        temp_df = pd.DataFrame(temp_df, columns=['category', 'rating', 'count'])
        temp_df.columns = ['X', 'rating', 'count']
        temp_df.sort_values('count', ascending=False, inplace=True)
    max_input_ = len(temp_df)
    temp_df = temp_df.iloc[min_-1:max_-1]
    return temp_df.copy(), max_input_


def get_cont_data(x_input):
    if x_input == 'Number of Episodes':
        temp_df: pd.DataFrame = df.groupby('eps')['rating'].mean().reset_index()
        temp_df.dropna(inplace=True)
        temp_df.columns = ['X', 'rating']
    elif x_input == 'Length of Anime in Minutes':
        temp_df = df[['rating', 'eps', 'mins_per_epi']].copy()
        temp_df['duration'] = temp_df['eps'] * temp_df['mins_per_epi']
        temp_df.columns = ['rating', 'eps', 'mins_per_epi', 'X']
    elif x_input == 'Length of Anime Name':
        temp_df = df[['anime_name', 'rating']].copy()
        temp_df['title_len'] = temp_df['anime_name'].str.len()
        temp_df = temp_df.groupby('title_len')['rating'].mean().reset_index()
        temp_df.columns = ['X', 'rating']
    else:
        temp_df = df[['description', 'rating']].copy()
        temp_df['desc_len'] = temp_df['description'].str.len()
        temp_df = temp_df.groupby('desc_len')['rating'].mean().reset_index()
        temp_df.columns = ['X', 'rating']
    temp_df.sort_values('X', inplace=True)
    return temp_df.copy()


cat_comparison = ['Studio', 'Themes', 'Categories']
cont_comparison = ['Number of Episodes', 'Length of Anime in Minutes', 'Length of Anime Name',
                   'Length of Anime Description']

data1, max_input = get_cat_data('Studio', [1, 10])
data2 = get_cont_data('Length of Anime Description')
cat_parameters = {
    'data_frame': data1,
    'x': 'X',
    'y': 'rating',
}
cont_parameters = {
    'data_frame': data2,
    'x': 'X',
    'y': 'rating'
}
fig1 = px.bar(**cat_parameters)
fig1.update_xaxes(title_text='Studio')
fig1.update_yaxes(title_text="Rating")

fig2 = px.line(**cont_parameters)
fig2.update_xaxes(title_text="Length of Anime Description")
fig2.update_yaxes(title_text="Rating")

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Categorical Data'),
        html.Label('Bar Chart or Pie Chart'),
        dcc.Dropdown(id='dropdown1-1',
                     options=[{'label': 'Bar Chart', 'value': 'Bar'},
                              {'label': 'Pie Chart', 'value': 'Pie'}],
                     value='Bar'),
        html.Label('X input'),
        dcc.Dropdown(id='dropdown1-2',
                     options=[{'label': x_input, 'value': x_input} for x_input in cat_comparison],
                     value='Studio'),
        dcc.Graph(id='graph1', figure=fig1),
        html.Label('Range of unique data displayed (Ordered by how popularity)'),
        dcc.RangeSlider(
            id='slider1',
            min=1,
            max=max_input,
            step=10,
            value=[1, 10]
        )
    ]),
    html.Div([
        html.H1('Continuous data'),
        html.Label('Line Plot or Dot Plot'),
        dcc.Dropdown(id='dropdown2-1',
                     options=[{'label': 'Line Plot', 'value': 'Line'},
                              {'label': 'Dot Plot', 'value': 'Dot'}],
                     value='Line'),
        html.Label('X input'),
        dcc.Dropdown(id='dropdown2-2',
                     options=[{'label': x_input, 'value': x_input} for x_input in cont_comparison],
                     value='Length of Anime Description'),
        dcc.Graph(id='graph2', figure=fig2)
    ])
])


@callback([Output(component_id='graph1', component_property='figure'),
           Output(component_id='slider1', component_property='max'),
           Output(component_id='slider1', component_property='step')],
          [Input(component_id='dropdown1-1', component_property='value'),
           Input(component_id='dropdown1-2', component_property='value'),
           Input(component_id='slider1', component_property='value')]
)
def update_cat_graph(graph_type, x_input, slider_val):
    data, max_in = get_cat_data(x_input, slider_val)
    bar_parameters = {
        'data_frame': data,
        'x': 'X',
        'y': 'rating'
    }
    pie_parameters = {
        'data_frame': data,
        'names': 'X',
        'values': 'rating',
    }
    if graph_type == 'Bar':
        fig = px.bar(**bar_parameters)
    else:
        fig = px.pie(**pie_parameters)
    if x_input == 'Studio':
        step = 10
    else:
        step = 1
    fig.update_xaxes(title_text=x_input)
    fig.update_yaxes(title_text="Rating")
    return fig, max_in, step


@callback(
    Output(component_id='graph2', component_property='figure'),
    [Input(component_id='dropdown2-1', component_property='value'),
     Input(component_id='dropdown2-2', component_property='value')])
def update_cont_graph(graph_type, x_input):
    data = get_cont_data(x_input)
    parameters = {
        'data_frame': data,
        'x': 'X',
        'y': 'rating',
    }
    if graph_type == 'Line':
        fig = px.line(**parameters)
    else:
        fig = px.scatter(**parameters)
    fig.update_xaxes(title_text=x_input)
    fig.update_yaxes(title_text="Rating")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

