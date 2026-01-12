"""
Tests for get_genre_and_style tool.
"""

import pytest
from ixcore import LLM
from ixutils import EnvVar
from ixtools.music.allmusic import get_genre_and_style
from tests.conftest import DEFAULT_TEST_MODEL


def test_get_genre_and_style_beatles():
    """Test getting genre and style from AllMusic for The Beatles."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # The Beatles AllMusic artist page
    beatles_url = "https://www.allmusic.com/artist/the-beatles-mn0000754032"
    
    result = get_genre_and_style(url=beatles_url, llm=llm)
    
    assert result["success"] is True
    assert result["error"] is None
    assert "genre" in result["result"]
    assert "style" in result["result"]
    assert result["result"]["url"] == beatles_url
    
    # Check genres - should include "Pop/Rock"
    genres = result["result"]["genre"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    assert "Pop/Rock" in genres
    
    # Check styles - should include several from the example
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
    # Verify some expected styles are present
    expected_styles = [
        "British Invasion",
        "British Psychedelia",
        "Contemporary Pop/Rock",
        "Early Pop/Rock",
        "Merseybeat",
        "Psychedelic/Garage",
        "Rock & Roll",
        "AM Pop",
        "Folk-Rock",
    ]
    
    # At least some of the expected styles should be found
    found_styles = [style for style in expected_styles if style in styles]
    assert len(found_styles) > 0, f"Expected to find at least some of {expected_styles}, but got {styles}"


def test_get_genre_and_style_sgt_pepper():
    """Test getting genre and style from AllMusic for Sgt. Pepper's Lonely Hearts Club Band album."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # Sgt. Pepper's Lonely Hearts Club Band AllMusic album page
    album_url = "https://www.allmusic.com/album/sgt-peppers-lonely-hearts-club-band-mw0000649874"
    
    result = get_genre_and_style(url=album_url, llm=llm)
    
    assert result["success"] is True
    assert result["error"] is None
    assert "genre" in result["result"]
    assert "style" in result["result"]
    assert result["result"]["url"] == album_url
    
    # Check genres - should include "Pop/Rock"
    genres = result["result"]["genre"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    assert "Pop/Rock" in genres
    
    # Check styles - should include several from the example
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
    # Verify some expected styles are present
    expected_styles = [
        "British Psychedelia",
        "Contemporary Pop/Rock",
        "Psychedelic/Garage",
        "Rock & Roll",
        "Baroque Pop",
        "AM Pop",
        "Hard Rock",
    ]
    
    # At least some of the expected styles should be found
    found_styles = [style for style in expected_styles if style in styles]
    assert len(found_styles) > 0, f"Expected to find at least some of {expected_styles}, but got {styles}"


def test_get_genre_and_style_with_a_little_help():
    """Test getting genre and style from AllMusic for 'With a Little Help from My Friends' song."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # With a Little Help from My Friends AllMusic song page
    song_url = "https://www.allmusic.com/song/with-a-little-help-from-my-friends-mt0004635277"
    
    result = get_genre_and_style(url=song_url, llm=llm)
    
    assert result["success"] is True
    assert result["error"] is None
    assert "genre" in result["result"]
    assert "style" in result["result"]
    assert result["result"]["url"] == song_url
    
    # Check genres - should include "Pop/Rock"
    genres = result["result"]["genre"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    assert "Pop/Rock" in genres
    
    # Check styles - should include several from the example
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
    # Verify some expected styles are present
    expected_styles = [
        "Contemporary Pop/Rock",
        "Early Pop/Rock",
        "British Psychedelia",
        "Psychedelic/Garage",
        "Rock & Roll",
    ]
    
    # At least some of the expected styles should be found
    found_styles = [style for style in expected_styles if style in styles]
    assert len(found_styles) > 0, f"Expected to find at least some of {expected_styles}, but got {styles}"


def test_get_genre_and_style_powerslave():
    """Test getting genre and style from AllMusic for Powerslave album by Iron Maiden."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # Powerslave AllMusic album page
    album_url = "https://www.allmusic.com/album/powerslave-mw0000190289"
    
    result = get_genre_and_style(url=album_url, llm=llm)
    
    assert result["success"] is True
    assert result["error"] is None
    assert "genre" in result["result"]
    assert "style" in result["result"]
    assert result["result"]["url"] == album_url
    
    # Check genres - should include "Pop/Rock"
    genres = result["result"]["genre"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    assert "Pop/Rock" in genres
    
    # Check styles - should include several from the example
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
    # Verify some expected styles are present
    expected_styles = [
        "British Metal",
        "Heavy Metal",
        "New Wave of British Heavy Metal",
    ]
    
    # At least some of the expected styles should be found
    found_styles = [style for style in expected_styles if style in styles]
    assert len(found_styles) > 0, f"Expected to find at least some of {expected_styles}, but got {styles}"


def test_get_genre_and_style_2_minutes_to_midnight():
    """Test getting genre and style from AllMusic for '2 Minutes to Midnight' song by Iron Maiden."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # Get genre and style using query (no need to find URL separately)
    result = get_genre_and_style(
        query="Iron Maiden 2 Minutes to Midnight",
        llm=llm,
        result_type="song",
        max_trials=3,
    )
    
    song_url = result["result"]["url"]
    
    assert result["success"] is True
    assert result["error"] is None
    assert "genre" in result["result"]
    assert "style" in result["result"]
    assert result["result"]["url"] == song_url
    
    # Check genres - should include "Pop/Rock"
    genres = result["result"]["genre"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    assert "Pop/Rock" in genres
    
    # Check styles - should include several from the example
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
    # Verify some expected styles are present
    expected_styles = [
        "British Metal",
        "Heavy Metal",
        "New Wave of British Heavy Metal",
    ]
    
    # At least some of the expected styles should be found
    found_styles = [style for style in expected_styles if style in styles]
    assert len(found_styles) > 0, f"Expected to find at least some of {expected_styles}, but got {styles}"

