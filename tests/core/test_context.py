"""
Tests for the Context class and configuration management.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from sentinelx.core.context import Context, NetworkConfig, BlockchainConfig, SecretsConfig


class TestContext:
    
    def test_context_creation_with_defaults(self):
        """Test creating context with default values."""
        ctx = Context()
        
        assert ctx.config == {}
        assert ctx.network.retries == 3
        assert ctx.network.timeout == 30
        assert ctx.blockchain.rpc_urls == []
        assert ctx.blockchain.default_chain == "ethereum"
    
    def test_context_load_nonexistent_file(self, caplog):
        """Test loading context from non-existent file."""
        ctx = Context.load("nonexistent.yaml")
        
        assert ctx.config == {}
        assert "Configuration file nonexistent.yaml not found" in caplog.text
    
    def test_context_load_valid_file(self, temp_config_file):
        """Test loading context from valid config file."""
        ctx = Context.load(str(temp_config_file))
        
        assert ctx.network.retries == 5
        assert ctx.network.timeout == 60
        assert ctx.network.http_proxy == "http://proxy.example.com:8080"
        assert len(ctx.blockchain.rpc_urls) == 2
        assert ctx.blockchain.default_chain == "ethereum"
        assert ctx.sandbox.enabled is True
    
    def test_environment_variable_resolution(self, temp_config_file):
        """Test that environment variables are properly resolved."""
        with patch.dict(os.environ, {
            'ETHERSCAN_API_KEY': 'test_etherscan_key',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            ctx = Context.load(str(temp_config_file))
            
            assert ctx.secrets.etherscan_api == 'test_etherscan_key'
            assert ctx.secrets.openai == 'test_openai_key'
    
    def test_environment_variable_missing(self, temp_config_file, caplog):
        """Test handling of missing environment variables."""
        # Ensure environment variables are not set
        with patch.dict(os.environ, {}, clear=True):
            ctx = Context.load(str(temp_config_file))
            
            assert ctx.secrets.etherscan_api == ""
            assert ctx.secrets.openai == ""
            assert "Environment variable ETHERSCAN_API_KEY not set" in caplog.text
    
    def test_get_config_value(self):
        """Test getting configuration values with dot notation."""
        config_data = {
            "level1": {
                "level2": {
                    "value": "test_value"
                }
            },
            "simple": "simple_value"
        }
        ctx = Context(config=config_data)
        
        assert ctx.get("simple") == "simple_value"
        assert ctx.get("level1.level2.value") == "test_value"
        assert ctx.get("nonexistent") is None
        assert ctx.get("nonexistent", "default") == "default"
    
    def test_set_config_value(self):
        """Test setting configuration values with dot notation."""
        ctx = Context()
        
        ctx.set("simple", "value")
        ctx.set("nested.key", "nested_value")
        
        assert ctx.get("simple") == "value"
        assert ctx.get("nested.key") == "nested_value"
    
    def test_get_secret(self):
        """Test getting secret values."""
        secrets = SecretsConfig(etherscan_api="test_key", openai="test_openai")
        ctx = Context(secrets=secrets)
        
        assert ctx.get_secret("etherscan_api") == "test_key"
        assert ctx.get_secret("openai") == "test_openai"
        assert ctx.get_secret("nonexistent") is None
    
    def test_enable_sandbox(self):
        """Test enabling sandbox configuration."""
        ctx = Context()
        
        assert not ctx.sandbox.enabled
        
        ctx.enable_sandbox(docker=True, seccomp="strict")
        
        assert ctx.sandbox.enabled
        assert ctx.sandbox.docker_enabled
        assert ctx.sandbox.seccomp_profile == "strict"
    
    def test_to_dict_masks_secrets(self):
        """Test that to_dict masks sensitive information."""
        secrets = SecretsConfig(etherscan_api="secret_key", openai="another_secret")
        ctx = Context(secrets=secrets)
        
        ctx_dict = ctx.to_dict()
        
        assert ctx_dict["secrets"]["etherscan_api"] == "***"
        assert ctx_dict["secrets"]["openai"] == "***"
    
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML"):
                Context.load(str(temp_file))
        finally:
            temp_file.unlink()


class TestNetworkConfig:
    
    def test_network_config_validation(self):
        """Test network configuration validation."""
        # Valid config
        config = NetworkConfig(retries=5, timeout=60)
        assert config.retries == 5
        assert config.timeout == 60
        
        # Invalid retries (too high)
        with pytest.raises(ValueError):
            NetworkConfig(retries=15)
        
        # Invalid timeout (too low)
        with pytest.raises(ValueError):
            NetworkConfig(timeout=0)


class TestBlockchainConfig:
    
    def test_blockchain_config_defaults(self):
        """Test blockchain configuration defaults."""
        config = BlockchainConfig()
        
        assert config.rpc_urls == []
        assert config.default_chain == "ethereum"
        assert config.gas_limit is None
        assert config.gas_price is None
    
    def test_blockchain_config_with_values(self):
        """Test blockchain configuration with custom values."""
        rpc_urls = ["http://localhost:8545", "https://mainnet.infura.io"]
        config = BlockchainConfig(
            rpc_urls=rpc_urls,
            default_chain="polygon",
            gas_limit=21000,
            gas_price=20000000000
        )
        
        assert config.rpc_urls == rpc_urls
        assert config.default_chain == "polygon"
        assert config.gas_limit == 21000
        assert config.gas_price == 20000000000
