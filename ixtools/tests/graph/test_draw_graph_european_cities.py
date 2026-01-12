"""
Test draw_graph function with European cities example.
"""

import pytest
import os

from ixtools.graph import draw_graph
from tests.conftest import TEST_DATA_DIR


# Country colour constants
GERMANY_COLOUR = "#F4B6B6"  # Pastel Red
FRANCE_COLOUR = "#A7C7E7"   # Pastel Blue
ITALY_COLOUR = "#B7E4C7"   # Pastel Green
CROSS_BORDER_COLOUR = "black"

# European cities with their hex colours organized by country
EUROPEAN_CITIES_NODES = [
    # Germany – Pastel Red
    {"id": "berlin", "label": "Berlin", "colour": GERMANY_COLOUR},
    {"id": "hamburg", "label": "Hamburg", "colour": GERMANY_COLOUR},
    {"id": "munich", "label": "Munich", "colour": GERMANY_COLOUR},
    {"id": "frankfurt", "label": "Frankfurt", "colour": GERMANY_COLOUR},
    {"id": "cologne", "label": "Cologne", "colour": GERMANY_COLOUR},
    {"id": "stuttgart", "label": "Stuttgart", "colour": GERMANY_COLOUR},
    {"id": "dusseldorf", "label": "Düsseldorf", "colour": GERMANY_COLOUR},
    {"id": "leipzig", "label": "Leipzig", "colour": GERMANY_COLOUR},
    
    # France – Pastel Blue
    {"id": "paris", "label": "Paris", "colour": FRANCE_COLOUR},
    {"id": "lyon", "label": "Lyon", "colour": FRANCE_COLOUR},
    {"id": "marseille", "label": "Marseille", "colour": FRANCE_COLOUR},
    {"id": "toulouse", "label": "Toulouse", "colour": FRANCE_COLOUR},
    {"id": "nice", "label": "Nice", "colour": FRANCE_COLOUR},
    {"id": "bordeaux", "label": "Bordeaux", "colour": FRANCE_COLOUR},
    {"id": "lille", "label": "Lille", "colour": FRANCE_COLOUR},
    {"id": "strasbourg", "label": "Strasbourg", "colour": FRANCE_COLOUR},
    
    # Italy – Pastel Green
    {"id": "milan", "label": "Milan", "colour": ITALY_COLOUR},
    {"id": "rome", "label": "Rome", "colour": ITALY_COLOUR},
    {"id": "turin", "label": "Turin", "colour": ITALY_COLOUR},
    {"id": "venice", "label": "Venice", "colour": ITALY_COLOUR},
    {"id": "bologna", "label": "Bologna", "colour": ITALY_COLOUR},
    {"id": "florence", "label": "Florence", "colour": ITALY_COLOUR},
    {"id": "naples", "label": "Naples", "colour": ITALY_COLOUR},
    {"id": "genoa", "label": "Genoa", "colour": ITALY_COLOUR},
]

# European cities edges
EUROPEAN_CITIES_EDGES = [
    # Germany (within-country, use country colour)
    {"source_id": "hamburg", "target_id": "berlin", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "berlin", "target_id": "leipzig", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "cologne", "target_id": "dusseldorf", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "cologne", "target_id": "frankfurt", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "frankfurt", "target_id": "stuttgart", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "stuttgart", "target_id": "munich", "label": "", "colour": GERMANY_COLOUR},
    {"source_id": "munich", "target_id": "leipzig", "label": "", "colour": GERMANY_COLOUR},
    
    # France (within-country, use country colour)
    {"source_id": "paris", "target_id": "lille", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "paris", "target_id": "strasbourg", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "paris", "target_id": "lyon", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "lyon", "target_id": "marseille", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "lyon", "target_id": "nice", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "marseille", "target_id": "nice", "label": "", "colour": FRANCE_COLOUR},
    {"source_id": "bordeaux", "target_id": "toulouse", "label": "", "colour": FRANCE_COLOUR},
    
    # Italy (within-country, use country colour)
    {"source_id": "milan", "target_id": "turin", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "milan", "target_id": "genoa", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "milan", "target_id": "bologna", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "bologna", "target_id": "florence", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "bologna", "target_id": "venice", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "florence", "target_id": "rome", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "rome", "target_id": "naples", "label": "", "colour": ITALY_COLOUR},
    {"source_id": "genoa", "target_id": "turin", "label": "", "colour": ITALY_COLOUR},
    
    # Cross-border (France ↔ Germany, use black)
    {"source_id": "strasbourg", "target_id": "stuttgart", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "strasbourg", "target_id": "frankfurt", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "lille", "target_id": "cologne", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "lille", "target_id": "dusseldorf", "label": "", "colour": CROSS_BORDER_COLOUR},
    
    # Cross-border (France ↔ Italy, use black)
    {"source_id": "nice", "target_id": "genoa", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "nice", "target_id": "milan", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "marseille", "target_id": "genoa", "label": "", "colour": CROSS_BORDER_COLOUR},
    
    # Cross-border (Germany ↔ Italy, use black)
    {"source_id": "munich", "target_id": "milan", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "stuttgart", "target_id": "milan", "label": "", "colour": CROSS_BORDER_COLOUR},
    {"source_id": "munich", "target_id": "venice", "label": "", "colour": CROSS_BORDER_COLOUR},
]


def test_draw_graph_european_cities():
    """Test drawing a graph of European cities with connections."""
    # Create test directory
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Draw the graph
    output_path = os.path.join(TEST_DATA_DIR, "european_cities_graph")
    result = draw_graph(
        nodes=EUROPEAN_CITIES_NODES,
        edges=EUROPEAN_CITIES_EDGES,
        output_path=output_path,
        direction="LR",
        format="png",
        view=True,
    )
    
    # Verify the result
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"] is not None
    assert "path" in result["result"]
    
    # Verify the file was created
    graph_path = result["result"]["path"]
    assert os.path.exists(graph_path)
    assert graph_path.endswith(".png")
