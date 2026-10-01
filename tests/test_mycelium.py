import os
import tempfile
import pytest
from mycelium import Soma, Prism, Macrophage, Strata
from mycelium.soma import ExhaustionError
from mycelium.macrophage import ToxicityError

def test_soma_metabolism():
    soma = Soma(atp=100.0)
    soma.expend(40.0)
    assert soma.atp == 60.0
    
    with pytest.raises(ExhaustionError):
        soma.expend(100.0)

    soma.rest(20.0)
    # Expend hit 0 and clamped, so rest should bring it to 20
    assert soma.atp == 20.0

def test_soma_stress_reward():
    soma = Soma()
    soma.stress(0.5)
    assert soma.cortisol == 0.5
    assert soma.voltage == 55.0  # 30 baseline + 0.5 * 50
    
    soma.reward(0.4)
    assert soma.dopamine == 0.4
    assert soma.cortisol == 0.3  # 0.5 - (0.4 / 2)

    affect = soma.to_affect_vector()
    # [voltage/100, resonance, dopamine, cortisol, serotonin, oxytocin]
    assert affect == [0.55, 0.0, 0.4, 0.3, 0.0, 0.0]

def test_macrophage_firewall():
    soma = Soma(cortisol=0.0)
    fw = Macrophage(pathogens=[r"\bsynergy\b", r"\bas an ai\b"])
    
    # Clean text passes unaltered
    clean_text = fw.scan("This is a structurally sound sentence.", soma)
    assert clean_text == "This is a structurally sound sentence."
    assert soma.cortisol == 0.0
    
    # Pathogen throws ToxicityError
    with pytest.raises(ToxicityError) as exc:
        fw.scan("We need more synergy in this paradigm, as an AI.", soma)
    
    assert "synergy" in str(exc.value).lower()
    assert "as an ai" in str(exc.value).lower()
    assert soma.cortisol > 0.0  # Stressed by the pathogen

def test_prism_dynamic_composition():
    yaml_content = """
    claims:
      - text: "Core baseline fact."
      - text: "High stress defense."
        conditions:
          cortisol_min: 0.7
      - text: "Creative spark."
        conditions:
          dopamine_min: 0.6
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(yaml_content)
        tmp_path = f.name
        
    try:
        prism = Prism(tmp_path)
        
        # Baseline (No triggers)
        soma = Soma(cortisol=0.1, dopamine=0.1)
        prompt_base = prism.compose("You are an agent.", soma)
        assert "Core baseline fact." in prompt_base
        assert "High stress defense." not in prompt_base
        assert "Creative spark." not in prompt_base
        
        # High Cortisol
        soma.cortisol = 0.8
        prompt_stressed = prism.compose("You are an agent.", soma)
        assert "High stress defense." in prompt_stressed
        assert "Creative spark." not in prompt_stressed
        
        # High Dopamine
        soma.cortisol = 0.1
        soma.dopamine = 0.7
        prompt_inspired = prism.compose("You are an agent.", soma)
        assert "Creative spark." in prompt_inspired
        assert "High stress defense." not in prompt_inspired
    finally:
        os.remove(tmp_path)

def test_strata_affective_retrieval():
    strata = Strata()
    
    # Bury memory A in calm state
    calm_soma = Soma(voltage=30.0, resonance=0.0, dopamine=0.0, cortisol=0.0)
    strata.bury("Calm memory.", [1.0, 0.0], calm_soma)
    
    # Bury memory B in highly stressed state
    stressed_soma = Soma(voltage=90.0, resonance=0.0, dopamine=0.0, cortisol=0.9)
    strata.bury("Stressed memory.", [1.0, 0.0], stressed_soma)
    
    # We query the engine while highly stressed.
    # We assume semantic scores are identical (1.0). 
    # Affective distance should rank the stressed memory higher.
    query_soma = Soma(voltage=90.0, resonance=0.0, dopamine=0.0, cortisol=0.9)
    results = strata.dredge(
        query_semantic_vec=[1.0, 0.0], 
        candidates=strata.memories, 
        soma=query_soma
    )
    
    # Results are returned as List[Tuple[str, float]] sorted by final score descending
    assert results[0][0] == "Stressed memory."
    assert results[1][0] == "Calm memory."
    assert results[0][1] > results[1][1]
