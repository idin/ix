"""
Tests for creating Fact instances.
"""

import pytest
from ixmachina.memory import Fact


def test_create_fact_with_minimal_arguments():
    """Create a fact with only required arguments."""
    fact = Fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": "alice-id", "role": "employee"},
            {"object_id": "acme-id", "role": "employer"},
        ],
    )
    
    assert fact.text == "Alice works at Acme"
    assert fact.relationship_type == "employment"
    assert len(fact.objects) == 2
    assert fact.fact_id is not None  # Auto-generated
    assert fact.metadata == {}
    assert fact.embedding is None
    assert fact.created_at is not None
    assert fact.updated_at is not None


def test_create_fact_with_custom_fact_id():
    """Create a fact with a custom fact_id."""
    custom_id = "my-custom-fact-id"
    
    fact = Fact(
        text="Bob is father of Charlie",
        relationship_type="father_of",
        objects=[
            {"object_id": "bob-id", "role": "father"},
            {"object_id": "charlie-id", "role": "child"},
        ],
        fact_id=custom_id,
    )
    
    assert fact.fact_id == custom_id


def test_create_fact_with_metadata():
    """Create a fact with metadata."""
    metadata = {"confidence": 0.95, "source": "company_db"}
    
    fact = Fact(
        text="David works at Initech",
        relationship_type="employment",
        objects=[
            {"object_id": "david-id", "role": "employee"},
            {"object_id": "initech-id", "role": "employer"},
        ],
        metadata=metadata,
    )
    
    assert fact.metadata == metadata


def test_create_fact_with_embedding():
    """Create a fact with an embedding vector."""
    embedding = [0.1, 0.2, 0.3, 0.4]
    
    fact = Fact(
        text="Eve manages Frank",
        relationship_type="manager_of",
        objects=[
            {"object_id": "eve-id", "role": "manager"},
            {"object_id": "frank-id", "role": "subordinate"},
        ],
        embedding=embedding,
    )
    
    assert fact.embedding == embedding


def test_create_nary_fact():
    """Create an n-ary fact with multiple objects (chemical reaction example)."""
    fact = Fact(
        text="Oxygen combined with Carbon produces CO2",
        relationship_type="chemical_reaction",
        objects=[
            {"object_id": "oxygen-id", "role": "reactant_1"},
            {"object_id": "carbon-id", "role": "reactant_2"},
            {"object_id": "co2-id", "role": "product"},
        ],
    )
    
    assert len(fact.objects) == 3
    assert fact.text == "Oxygen combined with Carbon produces CO2"
    assert fact.relationship_type == "chemical_reaction"

