from enum import auto
from libraries import *

"""
Generate Playlist Table
"""
def generate_playlist_df(sp, playlist):
    this_playlist = pd.DataFrame(columns=['track_name', 'track_artists', 'artist_genres', 'artist_popularity','track_album','track_duration','album_release:yyyy','album_release:mm','album_release:dd','artist_image', 'track_image','added_by','added_at'])
    for track in playlist['tracks']['items']:
        track_title = track['track']['name']
        track_artists = []
        artist_genres = []
        artist_images = []
        artist_popularities = []
        for artist in track['track']['artists']:
            track_artists.append(artist['name'])
            artist_stats = sp.artist(artist['id'])
            artist_genres.extend(artist_stats['genres'])
            artist_images.append(artist_stats['images'][1]['url'])
            artist_popularities.append(artist_stats['popularity'])
        album_name = track['track']['album']['name']
        track_duration = track['track']['duration_ms']/60000
        release_date = track['track']['album']['release_date']
        if len(release_date.split('-')) == 3:
            year, month, day = release_date.split('-')
        else:
            year = release_date
            month, day = '',''
        album_art = track['track']['album']['images'][1]['url']
        added_by = sp.user(track['added_by']['id'])['display_name']
        added_at = track['added_at']
        this_playlist.loc[len(this_playlist)] = [track_title, track_artists, artist_genres, artist_popularities, album_name, track_duration, year, month,day, artist_images, album_art, added_by, added_at]
    return this_playlist

"""
Generate Artist Figures
"""

def generate_artist_figure(artist, image):
    fig = go.Figure()
    fig.add_layout_image(
            dict(
                source=image,
                xref="paper", yref="paper",
                x=1, y=0,
                sizex=1, sizey=1,
                xanchor="right", yanchor="bottom",
                opacity=1,
                layer="above")
    )

    # Set templates
    fig.update_xaxes(title='', visible=False, showticklabels=False, range=[0,1])
    fig.update_yaxes(title='', visible=False, showticklabels=False, range=[0,1])

    fig.update_layout(
        template="plotly_white",
        hovermode=False,
        autosize=True,
        height=350,
        width=350,
        title=dict(
            text='<b>' + artist + '</b>',
            x=0.5,
            y=0.8,
            font=dict(
                family="Courier New",
                size=18,
                color='#000000'
            )
        )
    )
    return fig


"""
Calendar View
"""

def generate_calendar_map(playlist_df):
    calendar_view = [['01', '02', '03'],
                    ['04', '05', '06'],
                    ['07', '08', '09'],
                    ['10', '11', '12']]

    calendar_y = ['<b>winter</b>', '<b>spring</b>', '<b>summer</b>', '<b>fall</b>']

    heat_map = []
    for season in calendar_view:
        season_ = []
        for count, month in enumerate(season):
            season_.append(len(playlist_df[playlist_df['album_release:mm']==month]))
        heat_map.append(season_)

    fig = go.Figure(data=go.Heatmap(
                        z=heat_map,
                        texttemplate="%{text}",
                        textfont={"size":20},
                        colorscale="Agsunset",
                        ))

    fig.update_layout(
                font_family="Courier New",
                font_size = 15)
    fig.update_layout(
        yaxis = dict(
            tickmode = 'array',
            tickvals = [0, 1, 2, 3],
            ticktext = calendar_y
        ))
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.update_xaxes(title='', visible=False, showticklabels=False)
    fig.update_layout(
            width=450,
            template="plotly_white",
            title=dict(
                text='<b>Track Release Distribution</b>',
                x=0.5,
                y=0.95,
                font=dict(
                    family="Courier New",
                    size=18,
                    color='#000000'
                )
            )
        )
    fig.update_layout(hovermode=False)
    return fig


"""
Track Duration Plot
"""

def histogram_plotting(df, column_name, x_label, title):
    fig = px.histogram(df, x=column_name,width=600,  hover_name=None)
    fig.update_yaxes(title='y', visible=False, showticklabels=False)
    fig.update_xaxes(title=x_label, visible=True, showticklabels=True)
    fig.update_layout(
            font_family="Courier New",
            font_size = 15)
    title_string = '<b> '+title+' </b>'
    fig.update_layout(
        width=450,
        template="plotly_white",
        title=dict(
            text=title_string,
            x=0.5,
            y=0.95,
            font=dict(
                family="Courier New",
                size=18,
                color='#000000'
            )
        )
    )
    fig.update_layout(hovermode=False)
    return fig

"""
Top Five Figure
"""
def top_five_figure(playlist_df, n, title, column):
    if type(playlist_df[column].iloc[0]) == list:
        value_distribution = Counter(playlist_df[column].explode())
    else:
         value_distribution = Counter(playlist_df[column])
    df = pd.DataFrame({'cat':value_distribution.keys(),
                    'count':value_distribution.values()})
    df.sort_values('count',ascending=False, inplace=True)
    if len(df) > n:
        df = df.head(n)
    else:
        df = df.head(3)
    fig = px.bar(df, x='count',y='cat',
                width=400, orientation='h', text='cat',hover_name=None)
    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})
    fig.update_traces(textposition='inside')
    colors = ['pink','red','blue','green','goldenrod','black','mediumslateblue','cyan','crimson','teal']
    fig.update_traces(marker_color=random.sample(colors, len(df)))
    fig.update_layout(hovermode=False)
    fig.update_yaxes(title='y', visible=False, showticklabels=False)
    fig.update_xaxes(title='x', visible=False, showticklabels=False)
    fig.update_layout(
        font_family="Courier New",
        font_size = 45)
    title_string = '<b> ' + title + ' </b>'
    fig.update_layout(
        template="plotly_white",
        width=450,
        title=dict(
            text=title_string,
            x=0.5,
            y=0.95,
            font=dict(
                family="Courier New",
                size=18,
                color='#000000'
            )
        )
    )
    fig.update_layout(uniformtext_minsize=60)
    return fig