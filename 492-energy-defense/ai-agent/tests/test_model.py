"""
Tests for AI model manager
"""

import pytest
from app.ml.model_manager import ModelManager


@pytest.fixture
async def model_manager():
    """Create model manager instance"""
    manager = ModelManager()
    await manager.initialize()
    return manager


@pytest.mark.asyncio
async def test_model_initialization(model_manager):
    """Test model initializes correctly"""
    assert model_manager.is_ready()
    assert model_manager.model is not None


@pytest.mark.asyncio
async def test_threat_analysis(model_manager):
    """Test threat analysis with sample data"""
    result = await model_manager.analyze_threat(
        auth_score=0.7,
        vuln_score=0.8,
        firewall_score=0.5,
        patch_score=0.3,
    )
    
    assert "threat_score" in result
    assert "confidence_score" in result
    assert "threat_category" in result
    assert "severity" in result
    assert 0 <= result["threat_score"] <= 1
    assert 0 <= result["confidence_score"] <= 1


@pytest.mark.asyncio
async def test_weight_update(model_manager):
    """Test weight update functionality"""
    new_weights = {
        "auth_events": 0.25,
        "vulnerability_severity": 0.40,
        "firewall_anomalies": 0.25,
        "patch_criticality": 0.10,
    }
    
    model_manager.update_weights(new_weights)
    assert model_manager.current_weights == new_weights


@pytest.mark.asyncio
async def test_invalid_weights(model_manager):
    """Test that invalid weights are rejected"""
    invalid_weights = {
        "auth_events": 0.5,
        "vulnerability_severity": 0.5,
        "firewall_anomalies": 0.5,
        "patch_criticality": 0.5,
    }
    
    with pytest.raises(ValueError):
        model_manager.update_weights(invalid_weights)


pytest_plugins = ('pytest_asyncio',)
