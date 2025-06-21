from __future__ import annotations
import os
import yaml
import logging
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class NetworkConfig(BaseModel):
    """Network configuration settings."""
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    retries: int = Field(default=3, ge=0, le=10)
    timeout: int = Field(default=30, ge=1, le=300)
    user_agent: str = "SentinelX/0.1.0"

class BlockchainConfig(BaseModel):
    """Blockchain configuration settings."""
    rpc_urls: List[str] = Field(default_factory=list)
    default_chain: str = "ethereum"
    gas_limit: Optional[int] = None
    gas_price: Optional[int] = None

class SecretsConfig(BaseModel):
    """Secrets and API keys configuration."""
    etherscan_api: Optional[str] = None
    openai: Optional[str] = None
    anthropic: Optional[str] = None
    infura_key: Optional[str] = None
    alchemy_key: Optional[str] = None

class SandboxConfig(BaseModel):
    """Sandboxing configuration."""
    enabled: bool = False
    docker_enabled: bool = False
    seccomp_profile: Optional[str] = None
    memory_limit: str = "1G"
    cpu_limit: str = "1.0"
    network_isolation: bool = True

class Context(BaseModel):
    """Application context with configuration and runtime state."""
    
    config: Dict[str, Any] = Field(default_factory=dict)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    blockchain: BlockchainConfig = Field(default_factory=BlockchainConfig)
    secrets: SecretsConfig = Field(default_factory=SecretsConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def load(cls, path: Optional[str] = "config.yaml") -> "Context":
        """Load configuration from YAML file with environment variable resolution."""
        if path is None:
            logger.warning("No configuration file specified, using defaults")
            data: Dict[str, Any] = {}
        else:
            config_path = Path(path)
            
            if not config_path.exists():
                logger.warning(f"Configuration file {path} not found, using defaults")
                data: Dict[str, Any] = {}
            else:
                try:
                    with open(config_path, "r") as f:
                        data = yaml.safe_load(f) or {}
                    logger.info(f"Loaded configuration from {config_path}")
                except yaml.YAMLError as e:
                    logger.error(f"Failed to parse YAML configuration: {e}")
                    raise ValueError(f"Invalid YAML in {path}: {e}")
                except Exception as e:
                    logger.error(f"Failed to load configuration file: {e}")
                    raise ValueError(f"Cannot load config file {path}: {e}")
        
        # Resolve environment variables
        resolved = cls._resolve_env_vars(data)
        
        try:
            # Extract typed configurations
            network_config = NetworkConfig(**resolved.get("network", {}))
            blockchain_config = BlockchainConfig(**resolved.get("blockchain", {}))
            secrets_config = SecretsConfig(**resolved.get("secrets", {}))
            sandbox_config = SandboxConfig(**resolved.get("sandbox", {}))
            
            return cls(
                config=resolved,
                network=network_config,
                blockchain=blockchain_config,
                secrets=secrets_config,
                sandbox=sandbox_config
            )
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ValueError(f"Invalid configuration: {e}")

    @staticmethod
    def _resolve_env_vars(value: Any) -> Any:
        """Recursively resolve environment variables in configuration values."""
        if isinstance(value, str) and value.startswith("ENV:"):
            env_var = value[4:]
            env_value = os.getenv(env_var)
            if env_value is None:
                logger.warning(f"Environment variable {env_var} not set")
                return ""
            return env_value
        elif isinstance(value, dict):
            return {k: Context._resolve_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [Context._resolve_env_vars(v) for v in value]
        else:
            return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key with dot notation support."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key with dot notation support."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value

    def enable_sandbox(self, docker: bool = False, seccomp: str | None = None) -> None:
        """Enable sandboxing with optional Docker and seccomp configuration."""
        self.sandbox.enabled = True
        self.sandbox.docker_enabled = docker
        if seccomp:
            self.sandbox.seccomp_profile = seccomp
        
        logger.info(f"Sandbox enabled (docker={docker}, seccomp={seccomp})")

    def get_secret(self, name: str) -> Optional[str]:
        """Get a secret value by name."""
        secret = getattr(self.secrets, name, None)
        if not secret:
            logger.warning(f"Secret '{name}' not configured")
        return secret

    def validate_blockchain_config(self) -> bool:
        """Validate blockchain configuration."""
        if not self.blockchain.rpc_urls:
            logger.warning("No blockchain RPC URLs configured")
            return False
        
        # Test connectivity to at least one RPC URL
        # This would be implemented with actual HTTP requests
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "config": self.config,
            "network": self.network.dict(),
            "blockchain": self.blockchain.dict(),
            "secrets": {k: "***" if v else None for k, v in self.secrets.dict().items()},
            "sandbox": self.sandbox.dict(),
        }
