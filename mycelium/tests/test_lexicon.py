import pytest
from mycelium.lexicon import LinguisticAnalyzer

@pytest.fixture
def test_config():
    vocab = {
        "heavy": ["synergy", "delve", "leverage", "paradigm"],
        "kinetic": ["run", "jump", "sprint"],
        "solvents": ["the", "a", "and"],
        "antigen_replacements": {"synergy": "cooperation"}
    }
    ling = {
        "PHONETICS": {
            "PLOSIVE": ["p", "t", "k", "b", "d", "g"],
            "LIQUID": ["l", "r"],
            "VOWELS": ["a", "e", "i", "o", "u"]
        },
        "ROOTS": {
            "heavy": ["synerg", "paradigm"]
        },
        "BIASES": {"heavy": 1.5, "kinetic": 1.0},
        "DIMENSION_MAP": {
            "heavy": {"narrative_drag": 1.0, "tension": 0.5},
            "kinetic": {"flow": 1.0, "tension": 0.1}
        }
    }
    return vocab, ling

def test_analyzer_initialization(test_config):
    vocab, ling = test_config
    analyzer = LinguisticAnalyzer(vocab, ling)
    
    assert "heavy" in analyzer._reverse_index["delve"]
    assert analyzer.antigen_regex is not None
    assert analyzer.plosive_chars == set(["p", "t", "k", "b", "d", "g"])

def test_sanitize(test_config):
    analyzer = LinguisticAnalyzer(*test_config)
    words = analyzer.sanitize("Hello, World! We are synergizing.")
    assert words == ["hello", "world", "we", "are", "synergizing"]

def test_measure_viscosity(test_config):
    analyzer = LinguisticAnalyzer(*test_config)
    
    # Solvent should be very low viscosity
    assert analyzer.measure_viscosity("the") == 0.1
    
    # Plosive heavy word
    visc = analyzer.measure_viscosity("paradigm")
    assert visc > 0.1

def test_vectorize(test_config):
    analyzer = LinguisticAnalyzer(*test_config)
    
    # Text with explicit heavy word
    vector = analyzer.vectorize("Let's leverage this.")
    assert "narrative_drag" in vector
    assert vector["narrative_drag"] > 0.0
    
    # Text with root-matched heavy word
    vector2 = analyzer.vectorize("We are synergizing.")
    assert "narrative_drag" in vector2

def test_antigens(test_config):
    analyzer = LinguisticAnalyzer(*test_config)
    
    # Ensure antigen regex compiles properly to catch "synergy"
    text = "We need synergy here."
    assert analyzer.antigen_regex.search(text) is not None
    assert analyzer.antigen_regex.sub("cooperation", text) == "We need cooperation here."
