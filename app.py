import pickle
from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

CLIENT_ID = "9df7175fc8fa45e39ba18724112ef3ec"
CLIENT_SECRET = "b3f9a700163947c687e68989b3c3f4bf"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load music data and similarity matrix
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
music_list = music['song'].values

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        print(album_cover_url)
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        # fetch the song poster
        artist = music.iloc[i[0]].artist
        print(artist)
        print(music.iloc[i[0]].song)
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)

    return recommended_music_names, recommended_music_posters

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_song = request.form.get("selected_song")
        recommended_music_names, recommended_music_posters = recommend(selected_song)
        return render_template("index.html", music_list=music_list, recommended_names=recommended_music_names, recommended_posters=recommended_music_posters)

    return render_template("index.html", music_list=music_list)

if __name__ == "__main__":
    app.run(debug=True)
