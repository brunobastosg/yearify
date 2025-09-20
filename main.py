"""
Organizes songs into yearly playlists based on a list of an users' playlists and a list of years.
"""
import json
import os
import sys
from pathlib import Path

import spotipy
from dotenv import load_dotenv

local_run = os.getenv('LOCAL_RUN', 'false')

if local_run.lower() == 'true':
    load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
source_playlist_names = json.loads(os.getenv('SOURCE_PLAYLIST_NAMES', '[]'))
years = json.loads(os.getenv('YEARS', '[]'))
yearly_playlist_prefix = os.getenv('YEARLY_PLAYLIST_NAME_PREFIX', '')
yearly_playlist_suffix = os.getenv('YEARLY_PLAYLIST_NAME_SUFFIX', '')

local_cache_exists = Path('.cache').is_file()

if not local_cache_exists and 'SPOTIFY_AUTH_CACHE' in os.environ:
    auth_cache = os.environ['SPOTIFY_AUTH_CACHE']

    with open('.cache', 'w', encoding='utf-8') as cache_file:
        cache_file.write(json.dumps(json.loads(auth_cache)))

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-modify-public'
    )
)

my_playlists = sp.current_user_playlists()

if my_playlists is None or 'items' not in my_playlists:
    print('No playlists found for the user.')
    sys.exit()

playlists_to_be_processed = []
existing_yearly_playlists = {}

for playlist in my_playlists['items']:
    if playlist['name'] in source_playlist_names:
        playlists_to_be_processed.append({ 'id': playlist['id'], 'name': playlist['name'] })

    for year in years:
        yearly_playlist_name = f'{yearly_playlist_prefix}{year}{yearly_playlist_suffix}'
        if playlist['name'] == yearly_playlist_name:
            existing_yearly_playlists[year] = { 'id': playlist['id'], 'name': playlist['name'] }

for playlist in playlists_to_be_processed:
    tracks = []
    results = sp.playlist_items(playlist['id'], additional_types=['track'])
    if results is None or 'items' not in results:
        print(f'No tracks found in playlist: {playlist['name']}')
        continue

    tracks.extend(results['items'])

    while results is not None and results.get('next'):
        results = sp.next(results)
        if results is not None and 'items' in results:
            tracks.extend(results['items'])

    tracks_to_add = {year: [] for year in years}

    for item in tracks:
        track = item['track']
        if track and track.get('album') and track['album'].get('release_date'):
            release_year = int(track['album']['release_date'][:4])
            if release_year in years:
                tracks_to_add[release_year].append({ 'id': track['id'], 'name': track['name'], 'uri': track['uri'] })

    for year, tracks in tracks_to_add.items():
        print(f'Processing year {year}...')
        if tracks:
            if existing_yearly_playlists.get(year):
                print(f'\tPlaylist for year {year} already exists.')
                existing_playlist = existing_yearly_playlists[year]

                existing_tracks = []

                results_existing_tracks = sp.playlist_items(existing_playlist['id'], additional_types=['track'])
                if results_existing_tracks is None or 'items' not in results_existing_tracks:
                    print(f'\t\tNo tracks found in playlist "{existing_playlist['name']}"')
                    continue

                existing_tracks.extend(results_existing_tracks['items'])

                for track in tracks:
                    if track['id'] not in [item['track']['id'] for item in existing_tracks if item['track']]:
                        sp.playlist_add_items(existing_playlist['id'], [track['uri']])
                        print(f'\t\tAdded track "{track['name']}" to existing playlist "{existing_playlist['name']}".')
                    else:
                        print(f'\t\tTrack "{track['name']}" already exists in playlist "{existing_playlist['name']}". Skipping.')
                continue

            yearly_playlist_name = f'{yearly_playlist_prefix}{year}{yearly_playlist_suffix}'

            my_user = sp.current_user()

            if my_user is None or 'id' not in my_user:
                print('\tCould not retrieve current user information.')
                continue

            new_playlist = sp.user_playlist_create(
                user=my_user['id'],
                name=yearly_playlist_name,
                public=True
            )

            if new_playlist is None or 'id' not in new_playlist:
                print(f'\tCould not create playlist "{yearly_playlist_name}"')
                continue

            sp.playlist_add_items(new_playlist['id'], [track['uri'] for track in tracks])
            print(f'\tCreated playlist "{new_playlist['name']}" with {len(tracks)} tracks.')
