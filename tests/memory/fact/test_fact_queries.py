"""
Tests for querying Fact objects.
"""

from ixmachina.memory import Fact


def test_get_objects_by_role():
    """Get all objects with a specific role."""
    fact = Fact(
        text="Oxygen combined with Carbon produces CO2",
        relationship_type="chemical_reaction",
        objects=[
            {"object_id": "oxygen-id", "role": "reactant"},
            {"object_id": "carbon-id", "role": "reactant"},
            {"object_id": "co2-id", "role": "product"},
        ],
    )
    
    reactants = fact.get_objects_by_role(role="reactant")
    products = fact.get_objects_by_role(role="product")
    
    assert len(reactants) == 2
    assert "oxygen-id" in reactants
    assert "carbon-id" in reactants
    assert len(products) == 1
    assert "co2-id" in products


def test_get_objects_by_role_no_matches():
    """Get objects by role when no objects have that role."""
    fact = Fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": "alice-id", "role": "employee"},
            {"object_id": "acme-id", "role": "employer"},
        ],
    )
    
    managers = fact.get_objects_by_role(role="manager")
    
    assert managers == []


def test_get_role_for_object():
    """Get the role of a specific object in a fact."""
    fact = Fact(
        text="Bob is father of Charlie",
        relationship_type="father_of",
        objects=[
            {"object_id": "bob-id", "role": "father"},
            {"object_id": "charlie-id", "role": "child"},
        ],
    )
    
    bob_role = fact.get_role_for_object(object_id="bob-id")
    charlie_role = fact.get_role_for_object(object_id="charlie-id")
    
    assert bob_role == "father"
    assert charlie_role == "child"


def test_get_role_for_object_not_in_fact():
    """Get role for an object not in the fact."""
    fact = Fact(
        text="David manages Eve",
        relationship_type="manager_of",
        objects=[
            {"object_id": "david-id", "role": "manager"},
            {"object_id": "eve-id", "role": "subordinate"},
        ],
    )
    
    role = fact.get_role_for_object(object_id="nonexistent-id")
    
    assert role is None


def test_has_object_true():
    """Check if fact has an object (positive case)."""
    fact = Fact(
        text="Frank works at Globex",
        relationship_type="employment",
        objects=[
            {"object_id": "frank-id", "role": "employee"},
            {"object_id": "globex-id", "role": "employer"},
        ],
    )
    
    assert fact.has_object(object_id="frank-id") is True
    assert fact.has_object(object_id="globex-id") is True


def test_has_object_false():
    """Check if fact has an object (negative case)."""
    fact = Fact(
        text="Grace is mother of Henry",
        relationship_type="mother_of",
        objects=[
            {"object_id": "grace-id", "role": "mother"},
            {"object_id": "henry-id", "role": "child"},
        ],
    )
    
    assert fact.has_object(object_id="nonexistent-id") is False

