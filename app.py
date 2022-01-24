## import the rest of the modules
from turtle import width
from app_functions import *
from SETTINGS import *

### retrieve data bases
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
client_credentials_manager = SpotifyClientCredentials(client_id=CID, client_secret=SECRETID)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# retrieve playlist info
this_playlist = generate_playlist_df(sp, sp.playlist('63vCzInW2mIYOVhZDa4Azj'))

def generate_tab_content(playlist_df, user=None):
    if user:
        playlist_df = playlist_df[playlist_df['added_by']==user]

    figs = [generate_calendar_map(playlist_df), histogram_plotting(playlist_df, 'track_duration', 'Track Duration (m)', 'Track Duration Distribution')]
    figs.extend([top_five_figure(playlist_df, 5, 'Top Genres', 'artist_genres'), top_five_figure(playlist_df, 5, 'Top Release Years', 'album_release:yyyy')])

    quick_stats = []
    for fig in figs:
        quick_stats.append(dcc.Graph(figure=fig, style={}))

    # get artist popularity table
    artist_rankings = pd.DataFrame({'artist':playlist_df['track_artists'].explode(),
                                    'popularity':playlist_df['artist_popularity'].explode(),
                                    'image':playlist_df['artist_image'].explode()})
    artist_rankings.drop_duplicates(inplace=True)
    artist_rankings.sort_values('popularity',inplace=True)

    if len(artist_rankings)>10:
        ## Create most famous row
        most_famous = artist_rankings.sort_values('popularity')[-5:]
        famous_div = []
        for idx, row in most_famous.iterrows():
            famous_div.append(dcc.Graph(figure=generate_artist_figure(row['artist'], row['image']), style={}))

        ## Create least famous row
        least_popular = artist_rankings.sort_values('popularity')[0:5]
        unfamous_div = []
        for idx, row in least_popular.iterrows():
            unfamous_div.append(dcc.Graph(figure=generate_artist_figure(row['artist'], row['image']), style={}))

        ## all user tab content
        tab_content = [
            html.Div(children=quick_stats, style={'display': 'flex','flexDirection': 'row'}),
            html.H2('Most Known Artists:',style={'font-family': 'monospace, monospace','margin-left':'50px'}),
            html.Div(children= famous_div, style={'display': 'flex','flexDirection': 'row'}),
            html.H2('Most Unknown Artists:',style={'font-family': 'monospace, monospace','margin-left':'50px'}),
            html.Div(children= unfamous_div, style={'display': 'flex','flexDirection': 'row'})]
    else:
        
        artists = artist_rankings.head(1)
        artists = artists.append(artist_rankings.tail(1))
        artist_div = []
        for idx, row in artists.iterrows():
            artist_div.append(dcc.Graph(figure=generate_artist_figure(row['artist'], row['image']), style={}))

        ## all user tab content
        tab_content = [
            html.Div(children=quick_stats, style={'display': 'flex','flexDirection': 'row'}),
            html.H2('Most Known + Unknown Artist:',style={'font-family': 'monospace, monospace','margin-left':'50px'}),
            html.Div(children= artist_div, style={'display': 'flex','flexDirection': 'row'})]
        
    return tab_content

## generate tabs
tab_styling = {'padding-bottom':'1vh','padding-top':'1.5vh','font-size':'14','font-family': 'monospace, monospace'}
tab_selected_style = tab_styling.copy()
tab_selected_style['borderTop'] = '1px solid #d6d6d6'
tab_selected_style['color'] = '#0000b5'
tab_opts = [dcc.Tab(label='Overall', value='all-users',style=tab_styling,selected_style=tab_selected_style)]
for user in this_playlist['added_by'].unique():
    display_name = user.split(' ')
    tab_opts.extend([dcc.Tab(label=display_name[0], value=user,style=tab_styling,selected_style=tab_selected_style)])

##  Combine Layout
app.layout = html.Div([
    html.Div(html.Img(src='https://raw.githubusercontent.com/ttorir/spotify-wrapped-weekly-public/main/header_small.png',width='1600px')
            ),
    dcc.Tabs(id="user-tab-filter", value='all-users', 
        children=tab_opts,style={'height':'5vh'}),
    html.Div(id='tabs-content-example-graph')],
    style={'background-color':'#fcfcfc'}
    )

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('user-tab-filter', 'value'))
def render_content(tab):
    if tab == 'all-users':
        return generate_tab_content(this_playlist)
    else:
        return generate_tab_content(this_playlist, user=tab)

if __name__ == '__main__':
    app.run_server(debug=True)