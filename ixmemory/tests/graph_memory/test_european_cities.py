"""
Test graph traversal using European cities data.
"""

# Colours
GERMANY_COLOUR = "#FFB3BA"  # Pastel Red
FRANCE_COLOUR = "#BAE1FF"   # Pastel Blue
ITALY_COLOUR = "#BAFFC9"    # Pastel Green
CROSS_BORDER_COLOUR = "#000000"  # Black

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

# Relationship types
DOMESTIC = "domestic"  # Within same country
CROSS_BORDER = "cross_border"  # Between countries

# European cities edges
EUROPEAN_CITIES_EDGES = [
    # Germany (within-country, domestic)
    {"source_id": "hamburg", "target_id": "berlin", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "berlin", "target_id": "leipzig", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "cologne", "target_id": "dusseldorf", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "cologne", "target_id": "frankfurt", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "frankfurt", "target_id": "stuttgart", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "stuttgart", "target_id": "munich", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    {"source_id": "munich", "target_id": "leipzig", "relationship_type": DOMESTIC, "colour": GERMANY_COLOUR},
    
    # France (within-country, domestic)
    {"source_id": "paris", "target_id": "lille", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "paris", "target_id": "strasbourg", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "paris", "target_id": "lyon", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "lyon", "target_id": "marseille", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "lyon", "target_id": "nice", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "marseille", "target_id": "nice", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    {"source_id": "bordeaux", "target_id": "toulouse", "relationship_type": DOMESTIC, "colour": FRANCE_COLOUR},
    
    # Italy (within-country, domestic)
    {"source_id": "milan", "target_id": "turin", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "milan", "target_id": "genoa", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "milan", "target_id": "bologna", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "bologna", "target_id": "florence", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "bologna", "target_id": "venice", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "florence", "target_id": "rome", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "rome", "target_id": "naples", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    {"source_id": "genoa", "target_id": "turin", "relationship_type": DOMESTIC, "colour": ITALY_COLOUR},
    
    # Cross-border (France ↔ Germany)
    {"source_id": "strasbourg", "target_id": "stuttgart", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "strasbourg", "target_id": "frankfurt", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "lille", "target_id": "cologne", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "lille", "target_id": "dusseldorf", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    
    # Cross-border (France ↔ Italy)
    {"source_id": "nice", "target_id": "genoa", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "nice", "target_id": "milan", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "marseille", "target_id": "genoa", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    
    # Cross-border (Germany ↔ Italy)
    {"source_id": "munich", "target_id": "milan", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "stuttgart", "target_id": "milan", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
    {"source_id": "munich", "target_id": "venice", "relationship_type": CROSS_BORDER, "colour": CROSS_BORDER_COLOUR},
]


# =============================================================================
# EXPECTED TRAVERSAL RESULTS
# =============================================================================
# These can be used by tests to verify traversal correctness.

# -----------------------------------------------------------------------------
# Outgoing traversal from Paris
# -----------------------------------------------------------------------------
# Depth 0: Just the starting node
PARIS_OUTGOING_DEPTH_0 = {"paris"}

# Depth 1: Paris has 3 outgoing edges:
#   Paris → Lille
#   Paris → Strasbourg
#   Paris → Lyon
PARIS_OUTGOING_DEPTH_1 = {"paris", "lille", "strasbourg", "lyon"}

# Depth 2: Continue from Lille, Strasbourg, Lyon:
#   From Lille:
#     Lille → Cologne
#     Lille → Düsseldorf
#   From Strasbourg:
#     Strasbourg → Stuttgart
#     Strasbourg → Frankfurt
#   From Lyon:
#     Lyon → Marseille
#     Lyon → Nice
PARIS_OUTGOING_DEPTH_2 = {
    "paris",
    "lille", "strasbourg", "lyon",
    "cologne", "dusseldorf",
    "stuttgart", "frankfurt",
    "marseille", "nice",
}

# Depth 3: Continue from depth 2 nodes:
#   From Cologne:
#     Cologne → Düsseldorf (already seen)
#     Cologne → Frankfurt (already seen)
#   From Frankfurt:
#     Frankfurt → Stuttgart (already seen)
#   From Stuttgart:
#     Stuttgart → Munich
#     Stuttgart → Milan
#   From Marseille:
#     Marseille → Genoa
#   From Nice:
#     Nice → Genoa (already seen)
#     Nice → Milan (already seen)
# New at depth 3: Munich, Milan, Genoa
PARIS_OUTGOING_DEPTH_3 = {
    "paris",
    "lille", "strasbourg", "lyon",
    "cologne", "dusseldorf", "stuttgart", "frankfurt", "marseille", "nice",
    "munich", "milan", "genoa",
}

# -----------------------------------------------------------------------------
# Incoming traversal from Milan
# -----------------------------------------------------------------------------
# Depth 0: Just the starting node
MILAN_INCOMING_DEPTH_0 = {"milan"}

# Depth 1: Edges that end at Milan:
#   Nice → Milan
#   Stuttgart → Milan
#   Munich → Milan
MILAN_INCOMING_DEPTH_1 = {"milan", "nice", "stuttgart", "munich"}

# Depth 2: Who points to those?
#   Into Nice:
#     Lyon → Nice
#     Marseille → Nice
#   Into Stuttgart:
#     Frankfurt → Stuttgart
#     Strasbourg → Stuttgart
#   Into Munich:
#     Stuttgart → Munich (already seen)
# New at depth 2: Lyon, Marseille, Frankfurt, Strasbourg
MILAN_INCOMING_DEPTH_2 = {
    "milan",
    "nice", "stuttgart", "munich",
    "lyon", "marseille", "frankfurt", "strasbourg",
}

# -----------------------------------------------------------------------------
# Both-direction traversal from Strasbourg
# -----------------------------------------------------------------------------
# Depth 0: Just the starting node
STRASBOURG_BOTH_DEPTH_0 = {"strasbourg"}

# Depth 1 (incoming + outgoing):
#   Outgoing:
#     Strasbourg → Stuttgart
#     Strasbourg → Frankfurt
#   Incoming:
#     Paris → Strasbourg
STRASBOURG_BOTH_DEPTH_1 = {"strasbourg", "paris", "stuttgart", "frankfurt"}

# Depth 2: From any direction:
#   From Paris → Lille, Lyon
#   From Stuttgart → Munich, Milan
#   From Frankfurt → Stuttgart (already seen)
#   Into Paris → (none in our graph)
#   Into Stuttgart → Frankfurt (already seen), Strasbourg (already seen)
#   Into Frankfurt → Cologne, Strasbourg (already seen)
# New: Lille, Lyon, Munich, Milan, Cologne
# Note: Also need to check outgoing from Lille → Cologne, Düsseldorf
STRASBOURG_BOTH_DEPTH_2 = {
    "strasbourg",
    "paris", "stuttgart", "frankfurt",
    "lille", "lyon", "munich", "milan", "cologne",
}


# =============================================================================
# EXPECTED DEPTHS (node_id -> min_depth)
# =============================================================================
# For validating that deduplication returns minimum depth.

# Outgoing from Paris: node_id -> expected minimum depth
PARIS_OUTGOING_DEPTHS = {
    # Depth 1: Paris → Lille, Strasbourg, Lyon
    "lille": 1,
    "strasbourg": 1,
    "lyon": 1,
    # Depth 2: From Lille → Cologne, Düsseldorf; From Strasbourg → Stuttgart, Frankfurt
    #          From Lyon → Marseille, Nice
    "cologne": 2,
    "dusseldorf": 2,
    "stuttgart": 2,
    "frankfurt": 2,
    "marseille": 2,
    "nice": 2,
    # Depth 3: From Stuttgart → Munich, Milan; From Marseille → Genoa
    "munich": 3,
    "milan": 3,
    "genoa": 3,
}

# Incoming to Milan: node_id -> expected minimum depth
MILAN_INCOMING_DEPTHS = {
    # Depth 1: Nice → Milan, Stuttgart → Milan, Munich → Milan
    "nice": 1,
    "stuttgart": 1,
    "munich": 1,
    # Depth 2: Into Nice (Lyon, Marseille), Into Stuttgart (Frankfurt, Strasbourg)
    "lyon": 2,
    "marseille": 2,
    "frankfurt": 2,
    "strasbourg": 2,
}

# Both-direction from Strasbourg: node_id -> expected minimum depth
STRASBOURG_BOTH_DEPTHS = {
    # Depth 1: Outgoing (Stuttgart, Frankfurt), Incoming (Paris)
    "paris": 1,
    "stuttgart": 1,
    "frankfurt": 1,
    # Depth 2: From Paris (Lille, Lyon), From Stuttgart (Munich, Milan),
    #          Into Frankfurt (Cologne)
    "lille": 2,
    "lyon": 2,
    "munich": 2,
    "milan": 2,
    "cologne": 2,
}


import sqlite3
from pathlib import Path

DB_PATH = Path("european_cities_graph.sqlite")

NODES_TABLE = "nodes"
EDGES_TABLE = "edges"


def build_sqlite_graph(
    db_path: Path = DB_PATH,
    nodes=EUROPEAN_CITIES_NODES,
    edges=EUROPEAN_CITIES_EDGES,
) -> None:
    """
    Create SQLite tables from EUROPEAN_CITIES_NODES / EUROPEAN_CITIES_EDGES.
    """
    db_path = Path(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")

    cur = conn.cursor()

    # Drop + create
    cur.execute(f"DROP TABLE IF EXISTS {EDGES_TABLE};")
    cur.execute(f"DROP TABLE IF EXISTS {NODES_TABLE};")

    cur.execute(
        f"""
        CREATE TABLE {NODES_TABLE} (
            node_id TEXT PRIMARY KEY,
            label   TEXT NOT NULL,
            colour  TEXT NOT NULL
        );
        """
    )

    cur.execute(
        f"""
        CREATE TABLE {EDGES_TABLE} (
            edge_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source_node_id  TEXT NOT NULL,
            target_node_id  TEXT NOT NULL,
            label           TEXT,
            colour          TEXT NOT NULL,
            FOREIGN KEY (source_node_id) REFERENCES {NODES_TABLE}(node_id),
            FOREIGN KEY (target_node_id) REFERENCES {NODES_TABLE}(node_id)
        );
        """
    )

    # Helpful indexes for traversal
    cur.execute(f"CREATE INDEX idx_edges_source ON {EDGES_TABLE}(source_node_id);")
    cur.execute(f"CREATE INDEX idx_edges_target ON {EDGES_TABLE}(target_node_id);")

    # Insert nodes
    cur.executemany(
        f"INSERT INTO {NODES_TABLE}(node_id, label, colour) VALUES (?, ?, ?);",
        [(n["id"], n["label"], n["colour"]) for n in nodes],
    )

    # Insert edges
    cur.executemany(
        f"INSERT INTO {EDGES_TABLE}(source_node_id, target_node_id, label, colour) VALUES (?, ?, ?, ?);",
        [(e["source_id"], e["target_id"], e.get("label", ""), e["colour"]) for e in edges],
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    build_sqlite_graph()
    print(f"Created: {DB_PATH.resolve()}")
