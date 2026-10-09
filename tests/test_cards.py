"""Tests for card name normalization, expansion, and decklist parsing."""

from mtg_archetypes.cards import expand_card_counts
from mtg_archetypes.cards import normalize_card_name
from mtg_archetypes.cards import parse_decklist_text
from mtg_archetypes.cards import slugify_archetype


def test_parse_decklist_blank_line_transition():
    """Verify that a blank line separates mainboard from sideboard when no header is present."""
    text = """4 Arclight Phoenix
4 Consider
4 Treasure Cruise

1 Abrade
2 Brazen Borrower
"""
    mainboard, sideboard = parse_decklist_text(text)
    assert len(mainboard) == 3
    assert sum(c["count"] for c in mainboard) == 12
    assert mainboard[0] == {"card": "Arclight Phoenix", "count": 4}
    assert mainboard[1] == {"card": "Consider", "count": 4}
    assert mainboard[2] == {"card": "Treasure Cruise", "count": 4}

    assert len(sideboard) == 2
    assert sum(c["count"] for c in sideboard) == 3
    assert sideboard[0] == {"card": "Abrade", "count": 1}
    assert sideboard[1] == {"card": "Brazen Borrower", "count": 2}


def test_parse_decklist_multiple_blank_lines_transition():
    """Multiple blank lines between mainboard and sideboard are handled smoothly."""
    text = """4 Lightning Bolt


2 Pyroblast
"""
    mainboard, sideboard = parse_decklist_text(text)
    assert len(mainboard) == 1
    assert mainboard[0] == {"card": "Lightning Bolt", "count": 4}
    assert len(sideboard) == 1
    assert sideboard[0] == {"card": "Pyroblast", "count": 2}


def test_parse_decklist_explicit_sideboard_header():
    """Explicit sideboard headers are recognized and switch to sideboard."""
    for header in [
        "Sideboard",
        "Sideboard:",
        "// Sideboard",
        "//sideboard",
        "# Sideboard",
        "Sideboard (15):",
    ]:
        text = f"""Deck
4 Lightning Bolt

{header}
2 Pyroblast
"""
        mainboard, sideboard = parse_decklist_text(text)
        assert len(mainboard) == 1, f"Failed for header: {header}"
        assert mainboard[0] == {"card": "Lightning Bolt", "count": 4}
        assert len(sideboard) == 1, f"Failed for header: {header}"
        assert sideboard[0] == {"card": "Pyroblast", "count": 2}


def test_parse_decklist_sb_prefix():
    """Cards prefixed with SB: or sb: are placed in sideboard."""
    text = """4 Lightning Bolt
SB: 2 Pyroblast
sb: 1 Abrade
"""
    mainboard, sideboard = parse_decklist_text(text)
    assert len(mainboard) == 1
    assert mainboard[0] == {"card": "Lightning Bolt", "count": 4}
    assert len(sideboard) == 2
    assert sideboard[0] == {"card": "Pyroblast", "count": 2}
    assert sideboard[1] == {"card": "Abrade", "count": 1}


def test_parse_decklist_blank_lines_in_mainboard_with_explicit_sideboard():
    """Blank lines within mainboard should not trigger sideboard when explicit header exists."""
    text = """4 Arclight Phoenix

4 Consider

Sideboard
1 Abrade
"""
    mainboard, sideboard = parse_decklist_text(text)
    assert len(mainboard) == 2
    assert mainboard[0]["card"] == "Arclight Phoenix"
    assert mainboard[1]["card"] == "Consider"
    assert len(sideboard) == 1
    assert sideboard[0] == {"card": "Abrade", "count": 1}


def test_parse_decklist_no_sideboard_with_newlines():
    """A deck with only mainboard and leading/trailing blank lines produces an empty sideboard."""
    text = """

4 Lightning Bolt
4 Mountain

"""
    mainboard, sideboard = parse_decklist_text(text)
    assert len(mainboard) == 2
    assert len(sideboard) == 0


def test_parse_decklist_empty():
    """Empty or whitespace-only input returns empty lists."""
    assert parse_decklist_text("") == ([], [])
    assert parse_decklist_text("   \n\n  \n") == ([], [])


def test_parse_decklist_quantities_and_set_codes():
    """Set codes are stripped and counts are parsed correctly."""
    text = """4x Lightning Bolt (LEA) 161
1 Brainstorm [EMA:40]
Counterspell
"""
    mainboard, sideboard = parse_decklist_text(text)
    assert mainboard == [
        {"card": "Lightning Bolt", "count": 4},
        {"card": "Brainstorm", "count": 1},
        {"card": "Counterspell", "count": 1},
    ]
    assert sideboard == []


def test_normalize_card_name():
    """Card names are lowercased, stripped of accents and special punctuation."""
    assert normalize_card_name("Jace, the Mind Sculptor") == "jace the mind sculptor"
    assert normalize_card_name("Seance") == "seance"
    assert normalize_card_name("Fire // Ice") == "fire // ice"
    assert normalize_card_name("") == ""


def test_expand_card_counts():
    """Card counts are expanded for full names and split faces."""
    counts = expand_card_counts(["4 Fire // Ice", "2 Lightning Bolt"])
    assert counts["fire // ice"] == 4
    assert counts["fire"] == 4
    assert counts["ice"] == 4
    assert counts["lightning bolt"] == 2


def test_slugify_archetype():
    """Archetype names are properly slugified."""
    assert slugify_archetype("Izzet Delver") == "izzet-delver"
    assert slugify_archetype("Death & Taxes") == "death-taxes"
    assert slugify_archetype("Mono-Red / Burn") == "mono-red-burn"
