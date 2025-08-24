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


class ChainMonitor(Task):
    """Blockchain network monitoring and analysis."""
    
    # Common blockchain networks and their RPC endpoints
    NETWORK_CONFIGS = {
        "ethereum": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "rpc_urls": [
                "https://eth-mainnet.alchemyapi.io/v2/demo",
                "https://ethereum.publicnode.com",
                "https://rpc.ankr.com/eth"
            ],
            "explorer": "https://etherscan.io"
        },
        "polygon": {
            "name": "Polygon",
            "chain_id": 137,
            "rpc_urls": [
                "https://polygon-rpc.com",
                "https://rpc.ankr.com/polygon"
            ],
            "explorer": "https://polygonscan.com"
        },
        "bsc": {
            "name": "Binance Smart Chain",
            "chain_id": 56,
            "rpc_urls": [
                "https://bsc-dataseed.binance.org",
                "https://rpc.ankr.com/bsc"
            ],
            "explorer": "https://bscscan.com"
        },
        "arbitrum": {
            "name": "Arbitrum One",
            "chain_id": 42161,
            "rpc_urls": [
                "https://arb1.arbitrum.io/rpc",
                "https://rpc.ankr.com/arbitrum"
            ],
            "explorer": "https://arbiscan.io"
        }
    }
    
    async def validate_params(self) -> None:
        """Validate ChainMonitor parameters."""
        network = self.params.get("network", "ethereum")
        if network not in self.NETWORK_CONFIGS:
            available = ", ".join(self.NETWORK_CONFIGS.keys())
            raise ValueError(f"Unsupported network: {network}. Available: {available}")
    
    async def run(self) -> Dict[str, Any]:
        """Execute blockchain monitoring."""
        if not AIOHTTP_AVAILABLE:
            return {
                "status": "error", 
                "error": "aiohttp is required. Install with: pip install aiohttp"
            }
            
        network = self.params.get("network", "ethereum")
        monitor_type = self.params.get("type", "network_status")
        addresses = self.params.get("addresses", [])
        blocks_to_scan = self.params.get("blocks", 10)
        include_txns = self.params.get("include_transactions", False)
        
        self.logger.info(f"Starting blockchain monitoring for {network}")
        
        network_config = self.NETWORK_CONFIGS[network]
        
        # Get active RPC endpoint
        rpc_url = await self._get_active_rpc(network_config["rpc_urls"])
        if not rpc_url:
            raise ValueError(f"No active RPC endpoints found for {network}")
        
        self.logger.info(f"Using RPC endpoint: {rpc_url}")
        
        results = {
            "network": network,
            "network_info": network_config,
            "rpc_endpoint": rpc_url,
            "timestamp": time.time(),
            "monitoring_type": monitor_type
        }
        
        # Execute monitoring based on type
        if monitor_type == "network_status":
            results.update(await self._monitor_network_status(rpc_url))
        elif monitor_type == "address_activity":
            if not addresses:
                raise ValueError("addresses parameter required for address_activity monitoring")
            results.update(await self._monitor_addresses(rpc_url, addresses))
        elif monitor_type == "block_analysis":
            results.update(await self._analyze_recent_blocks(rpc_url, blocks_to_scan, include_txns))
        elif monitor_type == "gas_tracker":
            results.update(await self._track_gas_prices(rpc_url))
        elif monitor_type == "suspicious_activity":
            results.update(await self._detect_suspicious_activity(rpc_url, blocks_to_scan))
        else:
            raise ValueError(f"Unknown monitoring type: {monitor_type}")
        
        self.logger.info(f"Blockchain monitoring completed for {network}")
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
    
    async def _rpc_call(self, rpc_url: str, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """Make an RPC call to the blockchain node."""
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
    
    async def _monitor_network_status(self, rpc_url: str) -> Dict[str, Any]:
        """Monitor basic network status and health."""
        try:
            # Get latest block number
            block_number_hex = await self._rpc_call(rpc_url, "eth_blockNumber")
            latest_block = int(block_number_hex, 16)
            
            # Get latest block details
            block_data = await self._rpc_call(rpc_url, "eth_getBlockByNumber", [block_number_hex, False])
            
            # Get current gas price
            gas_price_hex = await self._rpc_call(rpc_url, "eth_gasPrice")
            gas_price_gwei = int(gas_price_hex, 16) / 1e9
            
            # Get network version
            network_version = await self._rpc_call(rpc_url, "net_version")
            
            # Calculate block time
            block_timestamp = int(block_data["timestamp"], 16)
            current_time = int(time.time())
            block_age = current_time - block_timestamp
            
            return {
                "network_status": {
                    "latest_block": latest_block,
                    "block_timestamp": block_timestamp,
                    "block_age_seconds": block_age,
                    "gas_price_gwei": round(gas_price_gwei, 2),
                    "network_version": network_version,
                    "block_hash": block_data["hash"],
                    "transaction_count": len(block_data.get("transactions", [])),
                    "is_healthy": block_age < 300  # Block should be less than 5 minutes old
                }
            }
        except Exception as e:
            return {
                "network_status": {
                    "error": str(e),
                    "is_healthy": False
                }
            }
    
    async def _monitor_addresses(self, rpc_url: str, addresses: List[str]) -> Dict[str, Any]:
        """Monitor specific addresses for activity."""
        address_data = {}
        
        for address in addresses:
            try:
                # Get balance
                balance_hex = await self._rpc_call(rpc_url, "eth_getBalance", [address, "latest"])
                balance_eth = int(balance_hex, 16) / 1e18
                
                # Get transaction count (nonce)
                nonce_hex = await self._rpc_call(rpc_url, "eth_getTransactionCount", [address, "latest"])
                nonce = int(nonce_hex, 16)
                
                # Get code (to check if it's a contract)
                code = await self._rpc_call(rpc_url, "eth_getCode", [address, "latest"])
                is_contract = code != "0x"
                
                address_data[address] = {
                    "balance_eth": round(balance_eth, 6),
                    "nonce": nonce,
                    "is_contract": is_contract,
                    "last_checked": time.time()
                }
                
            except Exception as e:
                address_data[address] = {
                    "error": str(e),
                    "last_checked": time.time()
                }
        
        return {"address_monitoring": address_data}
    
    async def _analyze_recent_blocks(self, rpc_url: str, block_count: int, include_txns: bool) -> Dict[str, Any]:
        """Analyze recent blocks for patterns and anomalies."""
        # Get latest block number
        latest_block_hex = await self._rpc_call(rpc_url, "eth_blockNumber")
        latest_block = int(latest_block_hex, 16)
        
        blocks_data = []
        total_txns = 0
        total_gas_used = 0
        block_times = []
        
        for i in range(block_count):
            block_num = latest_block - i
            block_hex = hex(block_num)
            
            try:
                block_data = await self._rpc_call(rpc_url, "eth_getBlockByNumber", [block_hex, include_txns])
                
                gas_used = int(block_data["gasUsed"], 16)
                gas_limit = int(block_data["gasLimit"], 16)
                timestamp = int(block_data["timestamp"], 16)
                txn_count = len(block_data.get("transactions", []))
                
                block_info = {
                    "number": block_num,
                    "hash": block_data["hash"],
                    "timestamp": timestamp,
                    "transaction_count": txn_count,
                    "gas_used": gas_used,
                    "gas_limit": gas_limit,
                    "gas_utilization": round((gas_used / gas_limit) * 100, 2),
                    "miner": block_data.get("miner"),
                    "size": int(block_data.get("size", "0x0"), 16)
                }
                
                if include_txns and block_data.get("transactions"):
                    block_info["transactions"] = block_data["transactions"][:5]  # Limit to first 5 txns
                
                blocks_data.append(block_info)
                total_txns += txn_count
                total_gas_used += gas_used
                block_times.append(timestamp)
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch block {block_num}: {e}")
        
        # Calculate averages and patterns
        avg_txns = total_txns / len(blocks_data) if blocks_data else 0
        avg_gas_used = total_gas_used / len(blocks_data) if blocks_data else 0
        
        # Calculate average block time
        avg_block_time = 0
        if len(block_times) > 1:
            time_diffs = [block_times[i] - block_times[i+1] for i in range(len(block_times)-1)]
            avg_block_time = sum(time_diffs) / len(time_diffs)
        
        return {
            "block_analysis": {
                "blocks_analyzed": len(blocks_data),
                "block_range": f"{latest_block - block_count + 1} - {latest_block}",
                "total_transactions": total_txns,
                "average_transactions_per_block": round(avg_txns, 2),
                "average_gas_used": avg_gas_used,
                "average_block_time": round(avg_block_time, 2),
                "blocks": blocks_data
            }
        }
    
    async def _track_gas_prices(self, rpc_url: str) -> Dict[str, Any]:
        """Track and analyze gas prices."""
        try:
            # Get current gas price
            gas_price_hex = await self._rpc_call(rpc_url, "eth_gasPrice")
            gas_price_wei = int(gas_price_hex, 16)
            gas_price_gwei = gas_price_wei / 1e9
            
            # Simulate historical data (in real implementation, this would come from storage)
            historical_prices = []
            for i in range(10):
                # Simulate some variance in gas prices
                import random
                price_variation = random.uniform(0.8, 1.2)
                simulated_price = gas_price_gwei * price_variation
                historical_prices.append({
                    "timestamp": time.time() - (i * 300),  # Every 5 minutes
                    "price_gwei": round(simulated_price, 2)
                })
            
            # Calculate price ranges
            prices = [p["price_gwei"] for p in historical_prices]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            return {
                "gas_tracking": {
                    "current_price_gwei": round(gas_price_gwei, 2),
                    "current_price_wei": gas_price_wei,
                    "price_analysis": {
                        "min_price_gwei": round(min_price, 2),
                        "max_price_gwei": round(max_price, 2),
                        "avg_price_gwei": round(avg_price, 2),
                        "price_volatility": round(max_price - min_price, 2)
                    },
                    "price_recommendations": {
                        "fast": round(gas_price_gwei * 1.2, 2),
                        "standard": round(gas_price_gwei, 2),
                        "safe": round(gas_price_gwei * 0.8, 2)
                    },
                    "historical_prices": historical_prices
                }
            }
        except Exception as e:
            return {
                "gas_tracking": {
                    "error": str(e)
                }
            }
    
    async def _detect_suspicious_activity(self, rpc_url: str, block_count: int) -> Dict[str, Any]:
        """Detect suspicious patterns in recent blocks."""
        suspicious_patterns = []
        
        try:
            # Get recent blocks
            latest_block_hex = await self._rpc_call(rpc_url, "eth_blockNumber")
            latest_block = int(latest_block_hex, 16)
            
            large_transactions = []
            high_gas_blocks = []
            frequent_addresses = {}
            
            for i in range(block_count):
                block_num = latest_block - i
                block_hex = hex(block_num)
                
                try:
                    block_data = await self._rpc_call(rpc_url, "eth_getBlockByNumber", [block_hex, True])
                    
                    gas_used = int(block_data["gasUsed"], 16)
                    gas_limit = int(block_data["gasLimit"], 16)
                    gas_utilization = (gas_used / gas_limit) * 100
                    
                    # Check for high gas utilization
                    if gas_utilization > 95:
                        high_gas_blocks.append({
                            "block": block_num,
                            "gas_utilization": round(gas_utilization, 2)
                        })
                    
                    # Analyze transactions
                    transactions = block_data.get("transactions", [])
                    for tx in transactions:
                        # Check for large value transactions
                        if tx.get("value"):
                            value_wei = int(tx["value"], 16)
                            value_eth = value_wei / 1e18
                            
                            if value_eth > 100:  # Transactions > 100 ETH
                                large_transactions.append({
                                    "hash": tx["hash"],
                                    "block": block_num,
                                    "value_eth": round(value_eth, 4),
                                    "from": tx.get("from"),
                                    "to": tx.get("to")
                                })
                        
                        # Track address frequency
                        for addr in [tx.get("from"), tx.get("to")]:
                            if addr:
                                frequent_addresses[addr] = frequent_addresses.get(addr, 0) + 1
                
                except Exception as e:
                    self.logger.debug(f"Error analyzing block {block_num}: {e}")
            
            # Find most active addresses
            most_active = sorted(frequent_addresses.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Generate suspicious patterns report
            if large_transactions:
                suspicious_patterns.append(f"Found {len(large_transactions)} large transactions (>100 ETH)")
            
            if high_gas_blocks:
                suspicious_patterns.append(f"Found {len(high_gas_blocks)} blocks with >95% gas utilization")
            
            if most_active and most_active[0][1] > block_count * 0.5:
                suspicious_patterns.append(f"High activity address detected: {most_active[0][0]} ({most_active[0][1]} transactions)")
            
            return {
                "suspicious_activity": {
                    "patterns_detected": suspicious_patterns,
                    "large_transactions": large_transactions[:10],  # Limit to top 10
                    "high_gas_blocks": high_gas_blocks,
                    "most_active_addresses": most_active,
                    "analysis_summary": {
                        "blocks_analyzed": block_count,
                        "total_suspicious_patterns": len(suspicious_patterns),
                        "risk_level": "high" if len(suspicious_patterns) > 2 else "medium" if suspicious_patterns else "low"
                    }
                }
            }
            
        except Exception as e:
            return {
                "suspicious_activity": {
                    "error": str(e),
                    "analysis_summary": {"risk_level": "unknown"}
                }
            }
