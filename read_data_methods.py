
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException
import requests
import time
import json

# Replace these with your actual Spotify API credentials
#CLIENT_ID = '6183796b64b4433291819da30c803b7b'
#CLIENT_SECRET = '4e1d393740cf410e9ddd52bfa9a68c03'
#CLIENT_ID = '535638d15af941b299aafe31a6f25114'
#CLIENT_SECRET = '025a06ed593b471780b3bda7ea50f5ed'
#CLIENT_ID = '23e627a798b74b71934a45c6b3441f23'
#CLIENT_SECRET = '2c897b12bd43470690f8b2c232e6bda4'
CLIENT_ID = 'ab27d51027bc4dd3b6cd9ae7dc2d571a'
CLIENT_SECRET = '37f49493fec24bed9945ad3d445e21a7'
#CLIENT_ID = '52b08f2db3914afb9cd2b5f510599e43'
#CLIENT_SECRET = '0fa08af355cc4421a7b06688aec7052d'

# Replace with your actual credentials
client_id = CLIENT_ID
client_secret = CLIENT_SECRET

# Get access token
auth_url = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(auth_url, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {
        'Authorization': f'Bearer {access_token}'
    }

def get_track_info(track_id):
    track_url = f'https://api.spotify.com/v1/tracks/{track_id}'
    response = requests.get(track_url, headers=headers)
    #print("Response is", response)
    response.raise_for_status() # Raise an exception for HTTP errors 
    return response.json()

def get_artist_data(artist_id): 
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    response = requests.get(artist_url, headers=headers) 
    response.raise_for_status() # Raise an exception for HTTP errors 
    return response.json()

def get_playlist_data(playlist_id):
    playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}' 
    response = requests.get(playlist_url, headers=headers) 
    response.raise_for_status() # Raise an exception for HTTP errors
    return response.json()

def get_tracks_data(track_ids):
    url = 'https://api.spotify.com/v1/tracks' 
    params = { 'ids': ','.join(track_ids) } 
    response = requests.get(url, headers=headers, params=params) 
    response.raise_for_status()
    return response.json()

def get_artists_data(artist_ids):
    url = 'https://api.spotify.com/v1/artists' 
    params = { 'ids': ','.join(artist_ids) } 
    response = requests.get(url, headers=headers, params=params) 
    response.raise_for_status()
    return response.json()

def get_audio_features(track_ids):
    url = 'https://api.spotify.com/v1/audio-features' 
    params = { 'ids': ','.join(track_ids) } 
    response = requests.get(url, headers=headers, params=params) 
    response.raise_for_status()
    return response.json()

def substring_after_second_colon(s):
    first_colon_index = s.find(':')
    second_colon_index = s.find(':', first_colon_index + 1)
    
    # If there are at least two colons, return the substring after the second colon
    if second_colon_index != -1:
        return s[second_colon_index + 1:]
    else:
        return None
    
def write_audio_data_to_file(song_list, file_offset):
    n = 15
    ttl = 100
    
    if len(song_list) < 1500:
        n = (len(song_list) // 100)
        print("n is now", n)
        if len(song_list) < 100:
            #add stuff here to finish loading all songs
            n = 1
            ttl = len(song_list)
            print("under 100 songs, songs left:", ttl)
            #print("Not enough songs")
            #return
    
    j = 0
    to_write_data = []
    for i in range(n):
        num_tracks_to_load = ttl
        track_ids = [substring_after_second_colon(t['track_uri']) for t in song_list[i * num_tracks_to_load:num_tracks_to_load * (i + 1)]]
        audio_features = get_audio_features(track_ids)
        to_write_data += ([a for a in audio_features['audio_features'] if a is not None])
        print("to write data length is", len(to_write_data))
        overwrite = (n != 15) and i == n - 1
        if ((i + 1) % 5 == 0) or overwrite:
            #print(i, j)
            file_name = 'audio_data' + str(j + file_offset) + '.json'

            # Write the list of dictionaries to a JSON file
            with open(file_name, 'w') as json_file:
                json.dump(to_write_data, json_file, indent=4)  # indent=4 for pretty-printing

            print(f"Data has been written to {file_name}")

            to_write_data = []
            j += 1
            #print(i, j)

def write_tracks_data_to_file(song_list, file_offset):
    n = 15
    ttl = 100
    
    if len(song_list) < 1500:
        n = (len(song_list) // 100)
        print("n is now", n)
        if len(song_list) < 100:
            #add stuff here to finish loading all songs
            n = 1
            ttl = len(song_list)
            print("under 100 songs, songs left:", ttl)
            #print("Not enough songs")
            #return
    
    j = 0
    to_write_tracks = []
    artist_genres = {}
    for i in range(n):
        num_tracks_to_load = ttl
        track_ids = [substring_after_second_colon(t['track_uri']) for t in song_list[i * num_tracks_to_load:num_tracks_to_load * (i + 1)]]
        tracks_info = get_tracks_data(track_ids)
        print("Length of track ids is", len(track_ids))
        artist_ids = []
        # add all the track data stuff
        for track_data_api in tracks_info['tracks']:
            if track_data_api != None:
                # Get artist IDs
                feature_artist_names = []
                if len(track_data_api['artists']) > 1:
                    feature_artist_names = [artist['name'] for artist in track_data_api['artists'][1:]]
                track_data_api['featured_artists'] = feature_artist_names
                track_data_api["album_uri"] = track_data_api['album']['uri']
                track_data_api["album_name"] = track_data_api['album']['name']
                track_data_api["artist_uri"] = track_data_api['artists'][0]['uri']
                track_data_api["artist_name"] = track_data_api['artists'][0]['name']
                keys_to_delete = ["artists", "available_markets", "external_urls", "external_ids", "album", "href", "id", "is_local", "preview_url", "type"]
                artist_id = track_data_api['artists'][0]['id']
                artist_ids.append(artist_id)
                for key in keys_to_delete:
                    if key in track_data_api:
                        del track_data_api[key]
            else:
                print("api is none")
                tracks_info['tracks'].remove(track_data_api)


        artist_data = get_artists_data(artist_ids[:50])['artists']
        for a in artist_data:
            artist_genres[a['uri']] = a['genres']
        #artist_genres += [{a['uri']: a['genres']} for a in artist_data]
        artist_data = get_artists_data(artist_ids[50:])['artists']
        for a in artist_data:
            artist_genres[a['uri']] = a['genres']
        #artist_genres += [{a['uri']: a['genres']} for a in artist_data]
        artist_ids = []
        
        for track in tracks_info['tracks']:
            if track != None:
                if 'artist_uri' in track:
                    artist_uri = track['artist_uri']
                    track['genres'] = artist_genres[artist_uri]
                    track['track_uri'] = track.pop('uri')
                    track['track_name'] = track.pop('name')
                else:
                    tracks_info['tracks'].remove(track)

        to_write_tracks += tracks_info['tracks']
        overwrite = (n != 15) and i == n - 1
        #print("number of tracks to write is", len(to_write_tracks))
        if ((i + 1) % 5 == 0) or overwrite:
            print(i, j)
            # Specify the file name
            file_name = 'data' + str(j + file_offset) + ".json"

            # Write the list of dictionaries to a JSON file
            with open(file_name, 'w') as json_file:
                json.dump(to_write_tracks, json_file, indent=4)  # indent=4 for pretty-printing

            print(f"Data has been written to {file_name}")

            artist_genres.clear()
            to_write_tracks = []
            j += 1
            print(i, j)

def write_track_data_to_file(song_list, file_offset):
    if len(song_list) < 1500:
        return
    
    j = 0
    for i, track in enumerate(song_list[:1500]):
        #print(i)
        TRACK_ID = track['track_uri']
        TRACK_ID = substring_after_second_colon(TRACK_ID)

        track_data_api = get_track_info(TRACK_ID)
        # Get artist IDs
        feature_artist_names = []
        if len(track_data_api['artists']) > 1:
            feature_artist_names = [artist['name'] for artist in track_data_api['artists'][1:]]
        song_popularity = track_data_api['popularity']
        song_explicit = track_data_api['explicit']

        #print("found extra data")

        artist_id = substring_after_second_colon(track['artist_uri'])
        artist_genres = get_artist_data(artist_id)['genres']

        #print("Got genres")
        
        track['related_genres'] = (artist_genres)
        track['featured_artists'] = feature_artist_names
        track['explicit'] = song_explicit
        track['popularity'] = song_popularity

        if (i + 1) % 100 == 0:
            print(i, j)
            # Specify the file name
            file_name = 'data' + str(j + file_offset) + ".json"

            # Write the list of dictionaries to a JSON file
            with open(file_name, 'w') as json_file:
                json.dump(song_list[j:j+100], json_file, indent=4)  # indent=4 for pretty-printing

            print(f"Data has been written to {file_name}")
            j += 100
            print(i, j)

def remove_common_items_by_track_name(list1, list2): 
    # Create a set of track names in list2
    track_names_in_list2 = {item['track_uri'] for item in list2 if 'track_uri' in item}
    # Create a list of items to keep in list1
    updated_list1 = [item for item in list1 if item['track_uri'] not in track_names_in_list2] 
    return updated_list1

def write_curr_audio_data(data):
    file_name = "extended_audio_data4.json"
    # Write the list of dictionaries to a JSON file
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # indent=4 for pretty-printing

    print(f"Data has been written to {file_name}")
    
def remove_duplicates_in_list(dict_list):
    seen_ids = set()
    unique_dicts = []
    duplicates = []

    for item in dict_list:
        item_id = item.get('track_uri')
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_dicts.append(item)
        else:
            duplicates.append(item)

    '''print("Duplicate entries:")
    for dup in duplicates:
        print(dup)
    '''

    return unique_dicts

def merge_dicts_by_id(list1, list2):
    combined_dict = {}

    # Function to update the combined dictionary with data from a list of dictionaries
    def update_combined_dict(dict_list):
        for item in dict_list:
            item_id = item['track_uri']
            if item_id not in combined_dict:
                combined_dict[item_id] = item.copy()
            else:
                combined_dict[item_id].update(item)

    # Update combined dictionary with both lists
    update_combined_dict(list1)
    update_combined_dict(list2)

    return combined_dict

def write_song_audio_data(data):
    file_name = "song_data1.json"
    # Write the list of dictionaries to a JSON file
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # indent=4 for pretty-printing

    print(f"Data has been written to {file_name}")
