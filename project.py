import os
import requests
from dotenv import load_dotenv
import json
import time
from urllib.parse import urlencode


def main():
    # Load environment variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = "http://localhost:8888/callback"
    scopes = [
        "user-read-currently-playing",
        "user-read-recently-played",
        "user-read-playback-state",
    ]  # Adjust scopes as needed

    # Get or refresh the access token
    access_token, refresh_token, expiration_time = get_spotify_access_token(
        client_id, client_secret, redirect_uri, scopes
    )
    print("Access token:", access_token)

    # Prompt the user to choose between genre-based recommendations and recommendations based on currently playing track
    print("\nChoose recommendation method:")
    print("1. Based on chosen genre")
    print("2. Based on currently playing track\n")
    method_choice = input("Enter the number of your desired method: ")

    if method_choice == "1":
        chosen_genre = get_user_genre(get_genres(access_token))
        print(f"\nChosen genre: {chosen_genre}\n")
        recommendations = get_spotify_recommendations(
            access_token, seed_genre=chosen_genre
        )
    elif method_choice == "2":
        # Get the currently playing track
        current_track = get_currently_playing_track(access_token)
        if current_track:
            print(
                f"\nCurrently playing: {current_track['name']} by {', '.join(artist['name'] for artist in current_track['artists'])}\n"
            )
            # Use the currently playing track as a seed to get recommendations
            recommendations = get_spotify_recommendations(
                access_token, seed_tracks=[current_track["id"]]
            )
            print_recommendations(recommendations)
        else:
            print("No track currently playing.")
            return
    else:
        print("Invalid choice. Defaulting to genre-based recommendations.")
        chosen_genre = get_user_genre(get_genres(access_token))
        print(f"\nChosen genre: {chosen_genre}\n")
        recommendations = get_spotify_recommendations(
            access_token, seed_genre=chosen_genre
        )

    print_recommendations(recommendations)

    # Check if access token needs to be refreshed
    if time.time() >= expiration_time:
        print("Access token expired. Refreshing token...")
        access_token = refresh_access_token(client_id, client_secret, refresh_token)
        print("New access token:", access_token)

        # Make the request again with the new access token
        recommendations = get_spotify_recommendations(
            access_token, seed_genres=[chosen_genre]
        )
        print_recommendations(recommendations)


def get_spotify_access_token(client_id, client_secret, redirect_uri, scopes):
    """
    Args:
        client_id (str): Your Spotify application's client ID.
        client_secret (str): Your Spotify application's client secret.
        redirect_uri (str): The redirect URI registered for your application.
        scopes (list): List of scopes required by your application.

    Returns:
        tuple: Tuple containing Spotify access token, refresh token, and expiration time.
    """
    try:
        with open("spotify_tokens.json", "r") as file:
            tokens = json.load(file)
            if tokens["expiration_time"] > time.time():
                return (
                    tokens["access_token"],
                    tokens["refresh_token"],
                    tokens["expiration_time"],
                )
    except FileNotFoundError:
        pass

    # Construct the authorization URL
    authorize_url = "https://accounts.spotify.com/authorize"
    authorize_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
    }
    full_authorize_url = authorize_url + "?" + urlencode(authorize_params)

    # Print the authorization URL and instruct the user to visit it
    print("Visit the following URL and authorize your application:")
    print(full_authorize_url)
    print()

    # Get the authorization code from the user
    authorization_code = input("Enter the authorization code from the URL: ")

    # Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"
    token_params = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(token_url, data=token_params)
    response_data = response.json()

    # Extract and return the access token and refresh token
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")
    expiration_time = int(response_data.get("expires_in", 3600)) + int(time.time())
    with open("spotify_tokens.json", "w") as file:
        json.dump(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration_time": expiration_time,
            },
            file,
        )

    return access_token, refresh_token, expiration_time


def refresh_access_token(client_id, client_secret, refresh_token):
    # Refresh the Spotify access token using the refresh token.

    token_url = "https://accounts.spotify.com/api/token"
    token_params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(token_url, data=token_params)
    response_data = response.json()
    return response_data.get("access_token")


def get_genres(access_token):
    # Get a list of available genres from Spotify.

    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("genres", [])
    else:
        print("Error fetching available genres:", response.status_code)
        return []


def get_user_genre(genres):
    # Ask the user to choose a genre from a list of available genres.

    print("\nAvailable genres:\n")
    num_per_row = 4
    max_genre_length = max(len(genre) for genre in genres)
    padding = 2  # Adjust the padding as needed
    total_items = len(genres)
    row_length = (max_genre_length + padding) * num_per_row
    for i, genre in enumerate(genres, start=1):
        print(f"{i:3}. {genre.ljust(max_genre_length)}", end="")
        if i % num_per_row == 0 or i == total_items:
            if i != total_items:
                print("\n" + "-" * row_length)
            else:
                remaining_items = total_items % num_per_row
                remaining_length = (max_genre_length + padding) * remaining_items
                print("\n" + "-" * remaining_length)
        else:
            print("|", end="")
    while True:
        choice = input("\nEnter the number of your desired genre: ")
        if choice.isdigit() and 1 <= int(choice) <= len(genres):
            return genres[int(choice) - 1]
        else:
            print("Invalid choice. Please enter a number between 1 and", len(genres))


def get_spotify_recommendations(
    access_token, seed_genre=None, seed_artists=None, seed_tracks=None, limit=20
):
    """
    Get recommendations from Spotify based on seed artists, genres, or tracks.

    Args:
        access_token (str): Spotify access token.
        seed_genre (str, optional): The genre to use as a seed for recommendations.
        seed_artists (list, optional): List of Spotify artist IDs to use as seed artists.
        seed_tracks (list, optional): List of Spotify track IDs to use as seed tracks.
        limit (int, optional): The target size of the list of recommended tracks. Default is 20.
    """
    url = "https://api.spotify.com/v1/recommendations"
    params = {"limit": limit}
    if seed_genre:
        params["seed_genres"] = seed_genre
    if seed_artists:
        params["seed_artists"] = ",".join(seed_artists)
    if seed_tracks:
        params["seed_tracks"] = ",".join(seed_tracks)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching recommendations:", response.status_code)
        error_message = response.json().get("error", {}).get("message", "Unknown error")
        print("Error message:", error_message)
        return None


def get_currently_playing_track(access_token):
    # Get the currently playing track from Spotify.

    url = "https://api.spotify.com/v1/me/player/currently-playing"

    # Make the GET request to the Spotify API
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful and a track is currently playing
    if response.status_code == 200:
        return response.json().get("item")
    else:
        print("Error fetching currently playing track:", response.status_code)
        return None


def print_recommendations(recommendations):
    # Print the recommended tracks in a readable format.

    if recommendations:
        print("Recommended Tracks:")
        for track in recommendations["tracks"]:
            artists = ", ".join(artist["name"] for artist in track["artists"])
            print(f"{track['name']} by {artists}")
    else:
        print("Failed to fetch recommendations.")


if __name__ == "__main__":
    main()
