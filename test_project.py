import pytest
from unittest.mock import patch, MagicMock
from project import (
    get_user_genre,
    print_recommendations,
    get_spotify_recommendations,
    get_currently_playing_track,
)


@pytest.fixture
def mocked_responses():
    return {
        "access_token": "mocked_access_token",
        "currently_playing_track": {
            "json_data": {
                "artists": [{"name": "Current Artist... Playing Track"}],
                "expiration_time": 1643932800,
                "genres": {"json_data": {"genres": ["rock", "pop", "hip hop"]}},
            }
        },
        # Add other mock responses as needed
    }


# Test get_user_genre function
def test_get_user_genre(monkeypatch, capsys):
    genres = ["rock", "pop", "hip hop"]
    expected_genre = "rock"

    def mock_input(prompt):
        return "1"

    monkeypatch.setattr("builtins.input", mock_input)

    get_user_genre(genres)
    captured = capsys.readouterr()

    for genre in genres:
        assert genre in captured.out


# Test print_recommendations function
def test_print_recommendations(capsys):
    recommendations = {
        "tracks": [
            {"name": "Track 1", "artists": [{"name": "Artist 1"}]},
            {"name": "Track 2", "artists": [{"name": "Artist 2"}]},
        ]
    }

    print_recommendations(recommendations)
    captured = capsys.readouterr()

    assert "Recommended Tracks:" in captured.out
    assert "Track 1 by Artist 1" in captured.out
    assert "Track 2 by Artist 2" in captured.out


# Test get_spotify_recommendations function
def test_get_spotify_recommendations():
    access_token = "mocked_access_token"
    seed_genre = "rock"
    mocked_responses = {
        "recommendations": {
            "json_data": {
                "tracks": [
                    {"name": "Track 1", "artists": [{"name": "Artist 1"}]},
                    {"name": "Track 2", "artists": [{"name": "Artist 2"}]},
                ]
            }
        }
    }

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mocked_responses["recommendations"][
            "json_data"
        ]
        mock_get.return_value = mock_response

        recommendations = get_spotify_recommendations(
            access_token, seed_genre=seed_genre
        )

    assert recommendations == mocked_responses["recommendations"]["json_data"]
