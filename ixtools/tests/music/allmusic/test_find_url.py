"""
Tests for find_allmusic_url tool.
"""

import pytest
from ixcore import LLM
from ixutils import EnvVar
from ixtools.music.allmusic import find_allmusic_url, get_genre_and_style
from tests.conftest import DEFAULT_TEST_MODEL


def test_find_allmusic_url_beatles_artist():
    """Test finding AllMusic URL for The Beatles artist."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    result = find_allmusic_url(query="The Beatles", llm=llm, result_type="artist")
    
    assert result["success"] is True
    assert result["error"] is None
    assert "url" in result["result"]
    assert result["result"]["url"].startswith("https://www.allmusic.com")
    assert "artist" in result["result"]["url"] or result["result"]["type"] == "artist"
    assert result["result"]["title"] is not None
    assert "beatles" in result["result"]["title"].lower() or "beatles" in result["result"]["url"].lower()


def test_find_allmusic_url_sgt_pepper_album():
    """Test finding AllMusic URL for Sgt. Pepper's Lonely Hearts Club Band album."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    result = find_allmusic_url(
        query="The Beatles Sgt. Pepper's Lonely Hearts Club Band",
        llm=llm,
        result_type="album",
    )
    
    assert result["success"] is True
    assert result["error"] is None
    assert "url" in result["result"]
    assert result["result"]["url"].startswith("https://www.allmusic.com")
    assert "album" in result["result"]["url"] or result["result"]["type"] == "album"
    assert result["result"]["title"] is not None
    # Verify it finds a Sgt. Pepper's album URL (there may be multiple releases)
    assert "sgt" in result["result"]["url"].lower() and "pepper" in result["result"]["url"].lower()
    assert "pepper" in result["result"]["title"].lower()


def test_get_genre_and_style_sgt_pepper_correct_url():
    """Test getting genre and style using the correct Sgt. Pepper's album URL."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    # The correct URL provided by the user
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
    
    # Check styles - should include the expected styles
    styles = result["result"]["style"]
    assert isinstance(styles, list)
    assert len(styles) > 0
    
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


def test_find_allmusic_url_with_a_little_help_song():
    """Test finding AllMusic URL for 'With a Little Help from My Friends' song."""
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name=DEFAULT_TEST_MODEL)
    
    result = find_allmusic_url(
        query="The Beatles With a Little Help from My Friends",
        llm=llm,
        result_type="song",
    )
    
    assert result["success"] is True
    assert result["error"] is None
    assert "url" in result["result"]
    assert result["result"]["url"].startswith("https://www.allmusic.com")
    assert "song" in result["result"]["url"] or result["result"]["type"] == "song"
    assert result["result"]["title"] is not None

