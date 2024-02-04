# Spotify Recommender Project

#### Description:

Created for the CS50 final project.
The Spotify Recommender Project is a Python program that utilizes the Spotify API to provide personalized music recommendations based on user preferences. This project aims to assist users in discovering new music tailored to their tastes and preferences.

## Features

- **Genre-based Recommendations**: Users can choose to receive recommendations based on their preferred music genre.
- **Track-based Recommendations**: Users can receive recommendations based on tracks they have recently listened to or the currently playing track.
- **Authorization**: The script handles user authorization using the Spotify Authorization Code flow.
- **Access Token Management**: Access tokens are automatically refreshed when they expire.
- **Error Handling**: The script handles errors such as rate limiting and missing data gracefully.

## Files

- **project.py**: Contains the main Python script for the Spotify Recommender Project, including functions for accessing the Spotify API, generating recommendations, and managing tokens.
- **test_project.py**: Includes test functions for testing the functionality of the project's custom functions using pytest.
- **spotify_tokens.json**: Stores access tokens, refresh tokens, and expiration times in JSON format for token management.

## Usage

1. Upon running the script, you will be prompted to choose a recommendation method:
   - Enter `1` to receive recommendations based on a chosen genre.
   - Enter `2` to receive recommendations based on the currently playing track.
2. Follow the instructions to complete the authorization process if required.
3. Enjoy your personalized music recommendations!

## Setup

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Register your application with the Spotify Developer Dashboard and obtain your client ID and client secret.
4. Create .env file in the root directory of the project and put CLIENT_ID and CLIENT_SECRET in it.
   `CLIENT_ID=your_client_id_here`
   `CLIENT_SECRET=your_client_secret_here`
5. Run the script using `python spotify_recommendations.py`.

## Dependencies

- Python 3.x
- requests == 2.28.1
- tabulate == 0.9.0

## Contributing

Contributions to the Spotify Recommender Project are welcome! If you have any ideas for improvements or new features, feel free to open an issue or submit a pull request on GitHub.

## Credits

This project was created by Emanuel Juricev. Special thanks to the Spotify Developer Platform for providing access to the Spotify API.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
