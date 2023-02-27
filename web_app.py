"""
Web app
"""
import base64
from requests import post, get
import json
import folium
import pycountry
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from flask import Flask, request

all_location = {}
app = Flask(__name__)

CLIENT_ID = "b5cda0c66a9641c48eb2b67b309d95d9"
CLIENT_SECRET = "ed9903701c404902af2e721a228f1ffa"


def get_token():
    """
    Gets access token
    """
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data,timeout=10)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def auth_headers(token):
    """
    Return auth header
    """
    return {"Authorization": "Bearer " + token}


def search_for_artist(artist_name, token):
    """
    Search fo artist
    """
    url = "https://api.spotify.com/v1/search"
    headers = auth_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers, timeout=10)
    json_result = json.loads(result.content)
    print(json_result)
    return json_result


def search_top_song(artist_id, token):
    """
    Search for top song in artist
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = auth_headers(token)
    result = get(url, headers=headers, timeout=10)
    json_result = json.loads(result.content)
    return json_result


def search_song_markets(song_id, token):
    """
    Search for markets in song
    """
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = auth_headers(token)
    result = get(url, headers=headers, params={"country": "US"}, timeout=10)
    json_result = json.loads(result.content)["available_markets"]
    return json_result


@app.route("/")
def base_page():
    """
    return base form
    """
    return "<form action='get_countries' method='get'>\
<input type='text' name='artist_name' value=''\
 required><input type='submit' value='Submit'></form>"


@app.route("/get_countries")
def get_countries():
    """
    Return artists top song markets
    """
    artist_name = request.args.get("artist_name")
    token = get_token()
    try:
        artist_id = search_for_artist(artist_name, token)["artists"]["items"][0][
            "external_urls"
        ]["spotify"].split("/")[-1]
    except IndexError:
        return (
            "<form action='get_countries' method='get'>\
        <input type='text' name='artist_name' value=''\
        required><input type='submit' value='Submit'></form>"
            + "<div>No artist were found</div>"
        )
    top_track = search_top_song(artist_id, token)["tracks"][0]
    top_track_id = top_track["id"]
    top_track_name = top_track["name"]
    available_markets = search_song_markets(top_track_id, token)
    map_marker = folium.Map()
    folium_g = folium.FeatureGroup(name=top_track_name)
    geolocator = Nominatim(user_agent="web_app.py")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for country_alpha in available_markets:
        try:
            if country_alpha not in all_location:
                country = pycountry.countries.get(alpha_2=country_alpha)
                country_name = country.name
                location = geocode(country_name)
                all_location[country_alpha] = (location, country_name)
            else:
                location = all_location[country_alpha][0]
                country_name = all_location[country_alpha][1]
            folium_g.add_child(
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=country_name,
                    icon=folium.Icon(),
                )
            )
        except AttributeError:
            continue
    map_marker.add_child(folium_g)
    map_marker.add_child(folium.LayerControl())
    return (
        "<form action='get_countries' method='get'>\
<input type='text' name='artist_name' value=''\
 required><input type='submit' value='Submit'></form>"
        + map_marker.get_root().render()
    )
