from __future__ import annotations
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from ..core.task import Task

# Optional dependencies with graceful fallback
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None


class BNBChain(Task):
    """BNB Chain (Binance Smart Chain) monitoring and analysis tools."""
    
    # BNB Chain network configurations
    BNB_CONFIGS = {
        "mainnet": {
            "name": "BNB Smart Chain Mainnet",
            "chain_id": 56,
            "rpc_urls": [
                "https://bsc-dataseed.binance.org",
                "https://bsc-dataseed1.binance.org",
                "https://bsc-dataseed2.binance.org",
                "https://rpc.ankr.com/bsc"
            ],
            "explorer": "https://bscscan.com",
            "native_token": "BNB",
            "native_decimals": 18
        },
        "testnet": {
            "name": "BNB Smart Chain Testnet",
            "chain_id": 97,
            "rpc_urls": [
                "https://data-seed-prebsc-1-s1.binance.org:8545",
                "https://data-seed-prebsc-2-s1.binance.org:8545",
                "https://rpc.ankr.com/bsc_testnet_chapel"
            ],
            "explorer": "https://testnet.bscscan.com",
            "native_token": "tBNB",
            "native_decimals": 18
        }
    }
    
    # BEP-20 token standard (similar to ERC-20)
    BEP20_METHODS = {
        "name": "0x06fdde03",
        "symbol": "0x95d89b41",
        "decimals": "0x313ce567",
        "totalSupply": "0x18160ddd",
        "balanceOf": "0x70a08231"
    }
    
    async def validate_params(self) -> None:
        """Validate BNBChain parameters."""
        operation = self.params.get("operation", "status")
        valid_operations = [
            "status", "balance", "token_info", "validator_info", 
            "staking_info", "gas_tracker", "contract_verify"
        ]
        
        if operation not in valid_operations:
            available = ", ".join(valid_operations)
            raise ValueError(f"Unknown operation: {operation}. Available: {available}")
        
        # Validate network
        network = self.params.get("network", "mainnet")
        if network not in self.BNB_CONFIGS:
            available = ", ".join(self.BNB_CONFIGS.keys())
            raise ValueError(f"Unknown network: {network}. Available: {available}")
    
    async def run(self) -> Dict[str, Any]:
        """Execute BNB Chain operations."""
        if not AIOHTTP_AVAILABLE:
            return {
                "status": "error",
                "error": "aiohttp is required. Install with: pip install aiohttp"
            }
        
        operation = self.params.get("operation", "status")
        network = self.params.get("network", "mainnet")
        
        self.logger.info(f"Starting BNB Chain operation: {operation} on {network}")
        
        network_config = self.BNB_CONFIGS[network]
        
        # Get active RPC endpoint
        rpc_url = await self._get_active_rpc(network_config["rpc_urls"])
        if not rpc_url:
            raise ValueError(f"No active RPC endpoints found for {network}")
        
        self.logger.info(f"Using RPC endpoint: {rpc_url}")
        
        results = {
            "network": network,
            "network_config": network_config,
            "rpc_endpoint": rpc_url,
            "timestamp": time.time(),
            "operation": operation
        }
        
        # Execute operation
        if operation == "status":
            results.update(await self._get_chain_status(rpc_url, network_config))
        elif operation == "balance":
            address = self.params.get("address")
            if not address:
                raise ValueError("address parameter required for balance operation")
            results.update(await self._get_balance(rpc_url, address, network_config))
        elif operation == "token_info":
            token_address = self.params.get("token_address")
            if not token_address:
                raise ValueError("token_address parameter required for token_info operation")
            results.update(await self._get_token_info(rpc_url, token_address))
        elif operation == "validator_info":
            results.update(await self._get_validator_info(rpc_url))
        elif operation == "staking_info":
            results.update(await self._get_staking_info(rpc_url))
        elif operation == "gas_tracker":
            results.update(await self._track_gas_prices(rpc_url))
        elif operation == "contract_verify":
            contract_address = self.params.get("contract_address")
            if not contract_address:
                raise ValueError("contract_address parameter required for contract_verify operation")
            results.update(await self._verify_contract(rpc_url, contract_address))
        
        self.logger.info(f"BNB Chain operation completed: {operation}")
        return results
    
    async def _get_active_rpc(self, rpc_urls: List[str]) -> Optional[str]:
        """Find the first working RPC endpoint."""
        for rpc_url in rpc_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 1
                    }
                    
                    async with session.post(
                        rpc_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "result" in data:
                                return rpc_url
            except Exception as e:
                self.logger.debug(f"RPC endpoint {rpc_url} failed: {e}")
                continue
        
        return None
    
    async def _rpc_call(self, rpc_url: str, method: str, params: List[Any] = None) -> Any:
        """Make an RPC call to the BNB Chain node."""
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                rpc_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        return data["result"]
                    elif "error" in data:
                        raise Exception(f"RPC error: {data['error']}")
                else:
                    raise Exception(f"HTTP error: {response.status}")
    
    async def _get_chain_status(self, rpc_url: str, network_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get BNB Chain network status."""
        try:
            # Get latest block number
            block_number_hex = await self._rpc_call(rpc_url, "eth_blockNumber")
            latest_block = int(block_number_hex, 16)
            
            # Get latest block details
            block_data = await self._rpc_call(rpc_url, "eth_getBlockByNumber", [block_number_hex, False])
            
            # Get current gas price
            gas_price_hex = await self._rpc_call(rpc_url, "eth_gasPrice")
            gas_price_gwei = int(gas_price_hex, 16) / 1e9
            
            # Get chain ID
            chain_id_hex = await self._rpc_call(rpc_url, "eth_chainId")
            chain_id = int(chain_id_hex, 16)
            
            # Calculate block time
            block_timestamp = int(block_data["timestamp"], 16)
            current_time = int(time.time())
            block_age = current_time - block_timestamp
            
            return {
                "chain_status": {
                    "chain_id": chain_id,
                    "latest_block": latest_block,
                    "block_timestamp": block_timestamp,
                    "block_age_seconds": block_age,
                    "gas_price_gwei": round(gas_price_gwei, 2),
                    "block_hash": block_data["hash"],
                    "transaction_count": len(block_data.get("transactions", [])),
                    "is_synced": block_age < 30,  # Block should be less than 30 seconds old for BNB Chain
                    "native_token": network_config["native_token"]
                }
            }
        except Exception as e:
            return {
                "chain_status": {
                    "error": str(e),
                    "is_synced": False
                }
            }
    
    async def _get_balance(self, rpc_url: str, address: str, network_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get BNB balance for an address."""
        try:
            # Get BNB balance
            balance_hex = await self._rpc_call(rpc_url, "eth_getBalance", [address, "latest"])
            balance_wei = int(balance_hex, 16)
            balance_bnb = balance_wei / 1e18
            
            # Get transaction count (nonce)
            nonce_hex = await self._rpc_call(rpc_url, "eth_getTransactionCount", [address, "latest"])
            nonce = int(nonce_hex, 16)
            
            # Check if it's a contract
            code = await self._rpc_call(rpc_url, "eth_getCode", [address, "latest"])
            is_contract = code != "0x"
            
            return {
                "balance_info": {
                    "address": address,
                    "balance_wei": str(balance_wei),
                    "balance_bnb": round(balance_bnb, 6),
                    "balance_formatted": f"{balance_bnb:.6f} {network_config['native_token']}",
                    "transaction_count": nonce,
                    "is_contract": is_contract,
                    "account_type": "contract" if is_contract else "wallet"
                }
            }
        except Exception as e:
            return {
                "balance_info": {
                    "address": address,
                    "error": str(e)
                }
            }
    
    async def _get_token_info(self, rpc_url: str, token_address: str) -> Dict[str, Any]:
        """Get BEP-20 token information."""
        try:
            token_info = {
                "token_address": token_address,
                "standard": "BEP-20"
            }
            
            # Check if it's a contract
            code = await self._rpc_call(rpc_url, "eth_getCode", [token_address, "latest"])
            if code == "0x":
                return {
                    "token_info": {
                        "error": "Address is not a contract",
                        "token_address": token_address
                    }
                }
            
            # Try to get token name
            try:
                name_data = await self._rpc_call(
                    rpc_url,
                    "eth_call",
                    [{"to": token_address, "data": self.BEP20_METHODS["name"]}, "latest"]
                )
                if name_data and name_data != "0x":
                    # Decode the name (simplified - in production use web3.py)
                    token_info["name"] = "Token Name (use web3.py for proper decoding)"
            except:
                token_info["name"] = "Unable to retrieve"
            
            # Try to get token symbol
            try:
                symbol_data = await self._rpc_call(
                    rpc_url,
                    "eth_call",
                    [{"to": token_address, "data": self.BEP20_METHODS["symbol"]}, "latest"]
                )
                if symbol_data and symbol_data != "0x":
                    token_info["symbol"] = "TOKEN (use web3.py for proper decoding)"
            except:
                token_info["symbol"] = "Unable to retrieve"
            
            # Try to get decimals
            try:
                decimals_data = await self._rpc_call(
                    rpc_url,
                    "eth_call",
                    [{"to": token_address, "data": self.BEP20_METHODS["decimals"]}, "latest"]
                )
                if decimals_data and decimals_data != "0x":
                    token_info["decimals"] = int(decimals_data, 16)
            except:
                token_info["decimals"] = "Unable to retrieve"
            
            # Try to get total supply
            try:
                supply_data = await self._rpc_call(
                    rpc_url,
                    "eth_call",
                    [{"to": token_address, "data": self.BEP20_METHODS["totalSupply"]}, "latest"]
                )
                if supply_data and supply_data != "0x":
                    total_supply = int(supply_data, 16)
                    token_info["total_supply"] = str(total_supply)
                    if isinstance(token_info.get("decimals"), int):
                        formatted_supply = total_supply / (10 ** token_info["decimals"])
                        token_info["total_supply_formatted"] = f"{formatted_supply:,.2f}"
            except:
                token_info["total_supply"] = "Unable to retrieve"
            
            token_info["note"] = "For full token details, use web3.py library for proper ABI decoding"
            
            return {"token_info": token_info}
        except Exception as e:
            return {
                "token_info": {
                    "token_address": token_address,
                    "error": str(e)
                }
            }
    
    async def _get_validator_info(self, rpc_url: str) -> Dict[str, Any]:
        """Get BNB Chain validator information."""
        return {
            "validator_info": {
                "consensus": "Proof of Staked Authority (PoSA)",
                "validator_count": 21,
                "validator_set_size": "Active: 21, Candidate validators can apply",
                "block_time": "~3 seconds",
                "epoch_period": "200 blocks (~10 minutes)",
                "features": [
                    "Fast block times",
                    "Low transaction fees",
                    "EVM compatible",
                    "Cross-chain compatibility with BNB Beacon Chain"
                ],
                "note": "BNB Chain uses a Proof of Staked Authority (PoSA) consensus with 21 active validators"
            }
        }
    
    async def _get_staking_info(self, rpc_url: str) -> Dict[str, Any]:
        """Get BNB Chain staking information."""
        return {
            "staking_info": {
                "mechanism": "Delegated Proof of Stake on BNB Beacon Chain",
                "minimum_stake": "Varies by validator",
                "staking_token": "BNB",
                "rewards": "Block rewards + transaction fees",
                "unbonding_period": "7 days",
                "slashing_conditions": [
                    "Double signing",
                    "Downtime",
                    "Malicious behavior"
                ],
                "staking_options": [
                    "Direct staking on BNB Beacon Chain",
                    "Liquid staking protocols (e.g., Ankr, pSTAKE)",
                    "Centralized exchange staking"
                ],
                "note": "BNB staking is primarily done on BNB Beacon Chain, not BNB Smart Chain"
            }
        }
    
    async def _track_gas_prices(self, rpc_url: str) -> Dict[str, Any]:
        """Track BNB Chain gas prices."""
        try:
            # Get current gas price
            gas_price_hex = await self._rpc_call(rpc_url, "eth_gasPrice")
            gas_price_wei = int(gas_price_hex, 16)
            gas_price_gwei = gas_price_wei / 1e9
            
            # BNB Chain typically has low and stable gas prices
            return {
                "gas_info": {
                    "current_price_gwei": round(gas_price_gwei, 2),
                    "current_price_wei": str(gas_price_wei),
                    "network_characteristics": {
                        "typical_range_gwei": "3-10 Gwei",
                        "avg_transaction_cost_usd": "$0.10-$0.50",
                        "congestion_level": "low" if gas_price_gwei < 10 else "medium" if gas_price_gwei < 20 else "high"
                    },
                    "price_recommendations": {
                        "fast": round(gas_price_gwei * 1.2, 2),
                        "standard": round(gas_price_gwei, 2),
                        "slow": max(3, round(gas_price_gwei * 0.8, 2))
                    },
                    "estimated_tx_costs": {
                        "simple_transfer_gwei": round(21000 * gas_price_gwei, 2),
                        "token_transfer_gwei": round(65000 * gas_price_gwei, 2),
                        "swap_gwei": round(150000 * gas_price_gwei, 2)
                    }
                }
            }
        except Exception as e:
            return {
                "gas_info": {
                    "error": str(e)
                }
            }
    
    async def _verify_contract(self, rpc_url: str, contract_address: str) -> Dict[str, Any]:
        """Verify and analyze a smart contract on BNB Chain."""
        try:
            # Get contract bytecode
            code = await self._rpc_call(rpc_url, "eth_getCode", [contract_address, "latest"])
            
            if code == "0x":
                return {
                    "contract_verification": {
                        "contract_address": contract_address,
                        "is_contract": False,
                        "error": "Address is not a contract"
                    }
                }
            
            # Basic contract analysis
            code_size = (len(code) - 2) // 2  # Remove 0x prefix and convert hex to bytes
            
            # Check for common patterns
            is_proxy = "3636" in code.lower()  # CALLDATASIZE pattern common in proxies
            has_selfdestruct = "ff" in code.lower()  # SELFDESTRUCT opcode
            
            verification_info = {
                "contract_address": contract_address,
                "is_contract": True,
                "bytecode_size_bytes": code_size,
                "bytecode_hash": code[:10] + "...",  # First few bytes as identifier
                "analysis": {
                    "possibly_proxy": is_proxy,
                    "has_selfdestruct": has_selfdestruct,
                    "complexity": "high" if code_size > 10000 else "medium" if code_size > 5000 else "low"
                },
                "verification_status": "unverified",
                "recommendations": [
                    "Verify source code on BscScan: https://bscscan.com/verifyContract",
                    "Check for similar contracts on BscScan",
                    "Use security tools like Slither or Mythril for deeper analysis"
                ],
                "explorer_url": f"https://bscscan.com/address/{contract_address}",
                "note": "For full verification, submit source code to BscScan or use Hardhat verification"
            }
            
            return {"contract_verification": verification_info}
        except Exception as e:
            return {
                "contract_verification": {
                    "contract_address": contract_address,
                    "error": str(e)
                }
            }
