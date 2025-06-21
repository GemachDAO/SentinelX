"""
Docker integration for SentinelX - sandboxed task execution and deployment.
"""
from __future__ import annotations
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import docker
import yaml

from ..core.task import BaseTask
from ..core.context import SentinelXContext
from ..core.utils import logger

@dataclass
class DockerConfig:
    """Docker execution configuration."""
    image: str = "sentinelx:latest"
    sandbox_image: str = "sentinelx:sandbox"
    network: str = "sentinelx-net"
    sandbox_network: str = "sentinelx-sandbox-net"
    memory_limit: str = "1g"
    cpu_limit: float = 1.0
    timeout: int = 300  # 5 minutes default
    volumes: Dict[str, str] = None
    environment: Dict[str, str] = None
    
    def __post_init__(self):
        if self.volumes is None:
            self.volumes = {}
        if self.environment is None:
            self.environment = {}

class DockerTaskRunner:
    """Execute SentinelX tasks in Docker containers."""
    
    def __init__(self, config: DockerConfig = None):
        self.config = config or DockerConfig()
        self.client = None
        self._ensure_client()
    
    def _ensure_client(self):
        """Ensure Docker client is available."""
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            logger.error(f"Docker not available: {e}")
            raise RuntimeError("Docker is required but not available")
    
    async def run_task_sandboxed(
        self, 
        task_name: str, 
        task_args: Dict[str, Any],
        dangerous: bool = False
    ) -> Dict[str, Any]:
        """
        Run a task in a sandboxed Docker container.
        
        Args:
            task_name: Name of the task to run
            task_args: Arguments for the task
            dangerous: Use isolated sandbox for dangerous tasks
            
        Returns:
            Task execution results
        """
        image = self.config.sandbox_image if dangerous else self.config.image
        network = self.config.sandbox_network if dangerous else self.config.network
        
        # Create temporary directory for task execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Prepare task configuration
            task_config = {
                "task_name": task_name,
                "task_args": task_args,
                "output_file": "/tmp/task_output.json"
            }
            
            config_file = temp_path / "task_config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(task_config, f)
            
            # Set up container volumes
            volumes = {
                str(config_file): {"bind": "/tmp/task_config.yaml", "mode": "ro"},
                **self.config.volumes
            }
            
            # Set up environment
            environment = {
                "SENTINELX_SANDBOX_MODE": "true" if dangerous else "false",
                "SENTINELX_CONFIG_FILE": "/tmp/task_config.yaml",
                **self.config.environment
            }
            
            try:
                # Run container
                container = self.client.containers.run(
                    image=image,
                    command=f"sentinelx run {task_name} --config /tmp/task_config.yaml --output /tmp/task_output.json",
                    volumes=volumes,
                    environment=environment,
                    network=network,
                    mem_limit=self.config.memory_limit,
                    nano_cpus=int(self.config.cpu_limit * 1e9),
                    detach=True,
                    remove=True,
                    security_opt=["no-new-privileges"] if dangerous else None,
                    cap_drop=["ALL"] if dangerous else None,
                    cap_add=["NET_ADMIN"] if not dangerous else None
                )
                
                # Wait for completion with timeout
                try:
                    result = container.wait(timeout=self.config.timeout)
                    logs = container.logs().decode('utf-8')
                    
                    if result['StatusCode'] == 0:
                        # Try to read output file
                        try:
                            output_data = yaml.safe_load(logs.split("OUTPUT:")[-1])
                            return {
                                "success": True,
                                "result": output_data,
                                "logs": logs,
                                "container_id": container.id[:12]
                            }
                        except Exception:
                            return {
                                "success": True,
                                "result": {"message": "Task completed successfully"},
                                "logs": logs,
                                "container_id": container.id[:12]
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Container exited with code {result['StatusCode']}",
                            "logs": logs,
                            "container_id": container.id[:12]
                        }
                        
                except docker.errors.APIError as e:
                    logger.error(f"Container execution failed: {e}")
                    return {
                        "success": False,
                        "error": f"Container execution failed: {e}",
                        "logs": "",
                        "container_id": container.id[:12] if container else "unknown"
                    }
                    
            except Exception as e:
                logger.error(f"Failed to run containerized task: {e}")
                return {
                    "success": False,
                    "error": f"Failed to run containerized task: {e}",
                    "logs": "",
                    "container_id": "unknown"
                }

class DockerBuilder:
    """Build and manage SentinelX Docker images."""
    
    def __init__(self):
        self.client = docker.from_env()
    
    def build_images(self, force_rebuild: bool = False) -> Dict[str, str]:
        """Build SentinelX Docker images."""
        results = {}
        
        # Build main image
        try:
            logger.info("Building main SentinelX image...")
            image, logs = self.client.images.build(
                path=".",
                tag="sentinelx:latest",
                dockerfile="Dockerfile",
                rm=True,
                forcerm=True,
                nocache=force_rebuild
            )
            results["main"] = image.id
            logger.info(f"Built main image: {image.id[:12]}")
        except Exception as e:
            logger.error(f"Failed to build main image: {e}")
            results["main"] = f"ERROR: {e}"
        
        # Build sandbox image
        try:
            logger.info("Building sandbox SentinelX image...")
            image, logs = self.client.images.build(
                path=".",
                tag="sentinelx:sandbox",
                dockerfile="Dockerfile.sandbox",
                rm=True,
                forcerm=True,
                nocache=force_rebuild
            )
            results["sandbox"] = image.id
            logger.info(f"Built sandbox image: {image.id[:12]}")
        except Exception as e:
            logger.error(f"Failed to build sandbox image: {e}")
            results["sandbox"] = f"ERROR: {e}"
        
        return results
    
    def setup_networks(self) -> Dict[str, str]:
        """Set up Docker networks for SentinelX."""
        results = {}
        
        # Main network
        try:
            network = self.client.networks.create(
                "sentinelx-net",
                driver="bridge",
                check_duplicate=True
            )
            results["main"] = network.id
        except docker.errors.APIError as e:
            if "already exists" in str(e):
                results["main"] = "EXISTS"
            else:
                results["main"] = f"ERROR: {e}"
        
        # Sandbox network (isolated)
        try:
            network = self.client.networks.create(
                "sentinelx-sandbox-net",
                driver="bridge",
                internal=True,  # No external access
                check_duplicate=True
            )
            results["sandbox"] = network.id
        except docker.errors.APIError as e:
            if "already exists" in str(e):
                results["sandbox"] = "EXISTS"
            else:
                results["sandbox"] = f"ERROR: {e}"
        
        return results

class DockerManager:
    """High-level Docker management for SentinelX."""
    
    def __init__(self):
        self.builder = DockerBuilder()
        self.runner = DockerTaskRunner()
    
    async def setup(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Set up complete Docker environment."""
        logger.info("Setting up SentinelX Docker environment...")
        
        results = {
            "images": self.builder.build_images(force_rebuild),
            "networks": self.builder.setup_networks()
        }
        
        # Check if setup was successful
        success = (
            not any("ERROR" in str(v) for v in results["images"].values()) and
            not any("ERROR" in str(v) for v in results["networks"].values())
        )
        
        results["success"] = success
        results["ready"] = success
        
        if success:
            logger.info("Docker environment setup complete!")
        else:
            logger.error("Docker environment setup failed!")
        
        return results
    
    def cleanup(self) -> Dict[str, Any]:
        """Clean up Docker resources."""
        results = {"images": [], "networks": [], "containers": []}
        
        try:
            # Stop and remove containers
            containers = self.builder.client.containers.list(
                filters={"ancestor": ["sentinelx:latest", "sentinelx:sandbox"]}
            )
            for container in containers:
                container.stop()
                container.remove()
                results["containers"].append(container.id[:12])
            
            # Remove images
            for tag in ["sentinelx:latest", "sentinelx:sandbox"]:
                try:
                    self.builder.client.images.remove(tag, force=True)
                    results["images"].append(tag)
                except Exception:
                    pass
            
            # Remove networks
            for network_name in ["sentinelx-net", "sentinelx-sandbox-net"]:
                try:
                    network = self.builder.client.networks.get(network_name)
                    network.remove()
                    results["networks"].append(network_name)
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Docker cleanup failed: {e}")
            results["error"] = str(e)
        
        return results

# Export main classes
__all__ = ["DockerManager", "DockerTaskRunner", "DockerBuilder", "DockerConfig"]
