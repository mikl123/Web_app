import base64
from requests import post, get
import os
import json

CLIENT_ID = "b5cda0c66a9641c48eb2b67b309d95d9"
CLIENT_SECRET = "ed9903701c404902af2e721a228f1ffa"


def get_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def auth_headers(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(artist_name, token):
    url = "https://api.spotify.com/v1/search"
    headers = auth_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)
    return json_result


def print_possibilyties(artist_feature):
    possible_inp = []
    if type(artist_feature) is dict:
        for feature in artist_feature:
            possible_inp.append(feature)
        return possible_inp
    elif type(artist_feature) is list:
        return str(len(artist_feature)) + " len"
    else:
        return artist_feature


def open_object_with_path(paths, artist):
    object_art = artist
    for path in paths:
        object_art = object_art[path]
    return object_art


if __name__ == "__main__":
    while True:
        print("Input Artist Name")
        input_name = input()
        if "exit" == input_name:
            break
        else:
            artist = search_for_artist(input_name, get_token())["artists"]
            path_json = []
            while True:
                artist_feature = open_object_with_path(path_json, artist)
                possible_input = print_possibilyties(artist_feature)
                print(
                    ".. - to go back\nexit - to finish execution\n* - to enter new user"
                )
                if type(possible_input) is list:
                    print("\n".join(possible_input))
                    input_feature = input()
                    if "*" == input_feature:
                        break
                    if "exit" == input_feature:
                        exit()
                    if ".." == input_feature:
                        path_json = path_json[:-1]
                        continue
                    if input_feature in possible_input:
                        path_json.append(input_feature)
                        path = "/".join(list(map(str, path_json)))
                        print(f"Okay now your path is ./{path}")
                        continue
                    else:
                        print(f"there is no feature like {input_feature}")
                else:
                    if "len" in str(possible_input):
                        list_size = int(possible_input.split(" ")[0])
                        print(f"We have list here type numbre from 0 to {list_size-1}")
                        input_list = input()
                        if input_list == "..":
                            path_json = path_json[:-1]
                            continue
                        if "exit" == input_list:
                            exit()
                        if (
                            input_list.isnumeric()
                            and 0 <= int(input_list) <= list_size - 1
                        ):
                            path_json.append(int(input_list))
                            continue
                        else:
                            print(
                                f"Invalid data you should input number from 0 to {list_size-1}"
                            )
                            continue
                    else:
                        print(possible_input)
                        input_end = input()
                        if input_end == "..":
                            path_json = path_json[:-1]
                            continue
                        if input_end == "exit":
                            exit()
