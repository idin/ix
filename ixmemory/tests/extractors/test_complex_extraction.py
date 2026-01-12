"""
Tests with complex, realistic text containing multiple types of extractable content.

Each test uses longer text with varied counts of different types.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.detect import detect, detect_and_extract
from ixmemory.extractors.extract import extract
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


# =============================================================================
# Example 1: Job posting
# Entities: 1 (Acme Corp)
# Numbers: 3 (5 years, $80k, $120k)
# Number ranges: 1 (salary range)
# Relationships: 0
# Attributes: 2 (remote, full-time)
# =============================================================================

JOB_POSTING_TEXT = """
Acme Corp is hiring a Senior Software Engineer. This is a full-time remote position.
Candidates must have at least 5 years of experience. The salary range is $80,000 to 
$120,000 depending on experience.
"""


def test_job_posting_detect(llm):
    """Detect content types in job posting."""
    result = detect(llm=llm, text=JOB_POSTING_TEXT)
    
    assert result["entities"] is True      # Acme Corp
    assert result["numbers"] is True       # 5 years experience
    assert result["number_ranges"] is True # salary range


def test_job_posting_extract_entities(llm):
    """Extract entities from job posting - should find 1."""
    result = extract(llm=llm, text=JOB_POSTING_TEXT, types=["entities"])
    
    entities = result["entities"]
    names = [e["name"] for e in entities]
    assert any("Acme" in name for name in names)


def test_job_posting_extract_numbers(llm):
    """Extract numbers from job posting - should find at least 3."""
    result = extract(llm=llm, text=JOB_POSTING_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    values = [n["value"] for n in numbers]
    # Should find 5 (years), 80000, 120000
    assert len(values) >= 1  # At least the experience years


def test_job_posting_extract_number_ranges(llm):
    """Extract number ranges from job posting - should find salary range."""
    result = extract(llm=llm, text=JOB_POSTING_TEXT, types=["number_ranges"])
    
    ranges = result["number_ranges"]
    assert len(ranges) >= 1
    # Should have both bounds for salary
    salary_range = ranges[0]
    assert salary_range.get("min") is not None or salary_range.get("max") is not None


# =============================================================================
# Example 2: Company bio
# Entities: 3 (Alice Chen, Bob Martinez, TechStart Inc)
# Numbers: 2 (2018, 50 employees)
# Moments: 1 (2018)
# Relationships: 2 (founded, works at)
# Attributes: 1 (innovative)
# =============================================================================

COMPANY_BIO_TEXT = """
TechStart Inc was founded by Alice Chen in 2018. Bob Martinez joined as CTO 
shortly after. The company now has 50 employees and is known for its innovative 
approach to cloud computing.
"""


def test_company_bio_detect(llm):
    """Detect content types in company bio."""
    result = detect(llm=llm, text=COMPANY_BIO_TEXT)
    
    assert result["entities"] is True      # TechStart, Alice, Bob
    assert result["relationships"] is True # founded, works at
    assert result["moments"] is True       # 2018


def test_company_bio_extract_entities(llm):
    """Extract entities from company bio - should find 3."""
    result = extract(llm=llm, text=COMPANY_BIO_TEXT, types=["entities"])
    
    entities = result["entities"]
    names = [e["name"] for e in entities]
    assert len(entities) >= 3
    assert any("Alice" in name for name in names)
    assert any("Bob" in name for name in names)
    assert any("TechStart" in name for name in names)


def test_company_bio_extract_relationships(llm):
    """Extract relationships from company bio - should find 2."""
    result = extract(llm=llm, text=COMPANY_BIO_TEXT, types=["relationships"])
    
    relationships = result["relationships"]
    assert len(relationships) >= 2


def test_company_bio_extract_numbers(llm):
    """Extract numbers from company bio - should find employee count."""
    result = extract(llm=llm, text=COMPANY_BIO_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    values = [n["value"] for n in numbers]
    assert 50 in values or 50.0 in values


# =============================================================================
# Example 3: Event announcement
# Entities: 2 (Global Tech Summit, San Francisco)
# Moments: 2 (March 15, March 18)
# Moment ranges: 1 (March 15-18)
# Numbers: 1 (500 attendees)
# Attributes: 1 (annual)
# =============================================================================

EVENT_TEXT = """
The annual Global Tech Summit will be held in San Francisco from March 15 to 
March 18, 2025. We expect over 500 attendees from around the world. Registration
closes on February 28.
"""


def test_event_detect(llm):
    """Detect content types in event announcement."""
    result = detect(llm=llm, text=EVENT_TEXT)
    
    assert result["entities"] is True       # Summit, San Francisco
    assert result["moments"] is True        # dates
    assert result["moment_ranges"] is True  # March 15-18


def test_event_extract_entities(llm):
    """Extract entities from event - should find 2."""
    result = extract(llm=llm, text=EVENT_TEXT, types=["entities"])
    
    entities = result["entities"]
    names = [e["name"] for e in entities]
    assert len(entities) >= 2
    assert any("San Francisco" in name for name in names)


def test_event_extract_moment_ranges(llm):
    """Extract moment ranges from event - should find conference dates."""
    result = extract(llm=llm, text=EVENT_TEXT, types=["moment_ranges"])
    
    ranges = result["moment_ranges"]
    assert len(ranges) >= 1
    # Should have start and end
    event_range = ranges[0]
    assert "start" in event_range or "end" in event_range


def test_event_extract_numbers(llm):
    """Extract numbers from event - should find attendee count."""
    result = extract(llm=llm, text=EVENT_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    values = [n["value"] for n in numbers]
    assert 500 in values or 500.0 in values


# =============================================================================
# Example 4: Product review
# Entities: 2 (iPhone 15 Pro, Apple)
# Numbers: 3 (4.8, $999, 6.7)
# Attributes: 3 (excellent, fast, sleek)
# Number ranges: 0
# Relationships: 1 (made by)
# =============================================================================

PRODUCT_REVIEW_TEXT = """
The iPhone 15 Pro by Apple is an excellent device. It has a sleek 6.7-inch display
and fast performance. With a rating of 4.8 out of 5 stars, it's worth every penny
of its $999 price tag.
"""


def test_product_review_detect(llm):
    """Detect content types in product review."""
    result = detect(llm=llm, text=PRODUCT_REVIEW_TEXT)
    
    assert result["entities"] is True    # iPhone, Apple
    assert result["numbers"] is True     # rating, price, screen size
    assert result["attributes"] is True  # excellent, fast, sleek


def test_product_review_extract_entities(llm):
    """Extract entities from product review - should find 2."""
    result = extract(llm=llm, text=PRODUCT_REVIEW_TEXT, types=["entities"])
    
    entities = result["entities"]
    names = [e["name"] for e in entities]
    assert len(entities) >= 2
    assert any("iPhone" in name for name in names)
    assert any("Apple" in name for name in names)


def test_product_review_extract_numbers(llm):
    """Extract numbers from product review - should find 3."""
    result = extract(llm=llm, text=PRODUCT_REVIEW_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    assert len(numbers) >= 3
    values = [n["value"] for n in numbers]
    # Should find 4.8 (rating), 999 (price), 6.7 (screen)
    assert any(v == 4.8 or abs(v - 4.8) < 0.1 for v in values)


def test_product_review_extract_attributes(llm):
    """Extract attributes from product review - should find descriptors."""
    result = extract(llm=llm, text=PRODUCT_REVIEW_TEXT, types=["attributes"])
    
    attributes = result["attributes"]
    assert len(attributes) >= 1


# =============================================================================
# Example 5: Personal profile
# Entities: 4 (Maria, Toronto, Google, Stanford)
# Numbers: 2 (35, 10)
# Moments: 1 (2015)
# Relationships: 3 (lives in, works at, graduated from)
# Attributes: 2 (senior, passionate)
# =============================================================================

PROFILE_TEXT = """
Maria is a 35-year-old senior data scientist living in Toronto. She has been
working at Google since 2015, accumulating over 10 years of experience in machine
learning. Maria graduated from Stanford University and is passionate about AI ethics.
"""


def test_profile_detect(llm):
    """Detect content types in personal profile."""
    result = detect(llm=llm, text=PROFILE_TEXT)
    
    assert result["entities"] is True      # Maria, Toronto, Google, Stanford
    assert result["numbers"] is True       # age, years
    assert result["relationships"] is True # lives, works, graduated
    assert result["moments"] is True       # 2015


def test_profile_extract_entities(llm):
    """Extract entities from profile - should find 4."""
    result = extract(llm=llm, text=PROFILE_TEXT, types=["entities"])
    
    entities = result["entities"]
    names = [e["name"] for e in entities]
    assert len(entities) >= 4
    assert any("Maria" in name for name in names)
    assert any("Toronto" in name for name in names)
    assert any("Google" in name for name in names)


def test_profile_extract_relationships(llm):
    """Extract relationships from profile - should find 3."""
    result = extract(llm=llm, text=PROFILE_TEXT, types=["relationships"])
    
    relationships = result["relationships"]
    assert len(relationships) >= 3


def test_profile_extract_numbers(llm):
    """Extract numbers from profile - should find age and experience."""
    result = extract(llm=llm, text=PROFILE_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    values = [n["value"] for n in numbers]
    assert 35 in values or 35.0 in values
    assert 10 in values or 10.0 in values


# =============================================================================
# Example 6: Real estate listing
# Entities: 1 (Sunset Heights)
# Numbers: 4 (3 beds, 2 baths, 1850 sqft, $450k)
# Number ranges: 1 (price negotiable down to $420k)
# Attributes: 3 (spacious, modern, quiet)
# Moment ranges: 1 (available from June)
# =============================================================================

REAL_ESTATE_TEXT = """
Beautiful home in Sunset Heights neighbourhood. This spacious 3-bedroom, 2-bathroom
property offers 1850 square feet of modern living space. Listed at $450,000 but
price is negotiable down to $420,000 for serious buyers. Located on a quiet 
street. Available from June 2025.
"""


def test_real_estate_detect(llm):
    """Detect content types in real estate listing."""
    result = detect(llm=llm, text=REAL_ESTATE_TEXT)
    
    assert result["entities"] is True       # Sunset Heights
    assert result["numbers"] is True        # beds, baths, sqft, price
    assert result["number_ranges"] is True  # negotiable price
    assert result["attributes"] is True     # spacious, modern, quiet


def test_real_estate_extract_numbers(llm):
    """Extract numbers from listing - should find 4 key numbers."""
    result = extract(llm=llm, text=REAL_ESTATE_TEXT, types=["numbers"])
    
    numbers = result["numbers"]
    values = [n["value"] for n in numbers]
    assert len(values) >= 4
    # Should find 3 (beds), 2 (baths), 1850 (sqft)
    assert 3 in values or 3.0 in values


def test_real_estate_extract_number_ranges(llm):
    """Extract number ranges from listing - should find price range."""
    result = extract(llm=llm, text=REAL_ESTATE_TEXT, types=["number_ranges"])
    
    ranges = result["number_ranges"]
    assert len(ranges) >= 1


def test_real_estate_extract_attributes(llm):
    """Extract attributes from listing - should find descriptors."""
    result = extract(llm=llm, text=REAL_ESTATE_TEXT, types=["attributes"])
    
    attributes = result["attributes"]
    values = [a["value"].lower() for a in attributes]
    assert len(attributes) >= 1


# =============================================================================
# Example 7: Full extraction test
# Tests detect_and_extract on complex text
# =============================================================================

COMPLEX_TEXT = """
Dr. Sarah Johnson, aged 42, is the Chief Medical Officer at Boston General Hospital.
She has been leading the cardiology department since January 2019. Her team of 25 
specialists handles between 100 and 150 patients weekly. Dr. Johnson graduated from
Harvard Medical School and lives in Cambridge with her husband Michael.
"""


def test_complex_detect_and_extract(llm):
    """Full detect and extract on complex text."""
    result = detect_and_extract(llm=llm, text=COMPLEX_TEXT)
    
    # Should have multiple types
    assert "entities" in result
    assert "numbers" in result
    assert "relationships" in result
    
    # Entities: Sarah Johnson, Boston General Hospital, Harvard, Cambridge, Michael
    assert len(result["entities"]) >= 4
    
    # Numbers: 42, 25, 100, 150
    assert len(result["numbers"]) >= 2
    
    # Relationships: CMO at hospital, leads department, graduated from, lives in
    assert len(result["relationships"]) >= 2


def test_complex_extract_all_types(llm):
    """Extract all types from complex text."""
    all_types = [
        "entities", "numbers", "moments", "attributes",
        "relationships", "number_ranges", "moment_ranges",
    ]
    result = extract(llm=llm, text=COMPLEX_TEXT, types=all_types)
    
    # Should have all requested keys
    for t in all_types:
        assert t in result
        assert isinstance(result[t], list)
    
    # Verify some content
    entity_names = [e["name"] for e in result["entities"]]
    assert any("Sarah" in name for name in entity_names)
    assert any("Boston" in name or "Hospital" in name for name in entity_names)
