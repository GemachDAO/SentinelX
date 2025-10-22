#!/usr/bin/env python3
"""
BNB Chain Analysis Examples

This script demonstrates various use cases for the BNB Chain security toolkit.
It shows how to monitor the network, analyze addresses, check tokens, and more.

Requirements:
    - SentinelX installed with blockchain dependencies
    - Internet connection for RPC access
"""

import asyncio
import json
from sentinelx.core.registry import PluginRegistry


async def example_chain_status():
    """Example: Get BNB Chain network status"""
    print("\n" + "="*60)
    print("EXAMPLE 1: BNB Chain Status Check")
    print("="*60)
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "status",
        "network": "mainnet"
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Check if chain is synced
    if result.get("chain_status", {}).get("is_synced"):
        print("\n✅ BNB Chain is synced and healthy!")
    else:
        print("\n⚠️  BNB Chain may have sync issues")
    
    return result


async def example_balance_check():
    """Example: Check BNB balance for an address"""
    print("\n" + "="*60)
    print("EXAMPLE 2: BNB Balance Check")
    print("="*60)
    
    # Example address (Binance Hot Wallet)
    address = "0x28C6c06298d514Db089934071355E5743bf21d60"
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "balance",
        "network": "mainnet",
        "address": address
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract balance info
    balance_info = result.get("balance_info", {})
    if "balance_formatted" in balance_info:
        print(f"\n💰 Balance: {balance_info['balance_formatted']}")
        print(f"📊 Transaction Count: {balance_info.get('transaction_count', 0)}")
        print(f"🏷️  Account Type: {balance_info.get('account_type', 'unknown')}")
    
    return result


async def example_token_analysis():
    """Example: Analyze a BEP-20 token"""
    print("\n" + "="*60)
    print("EXAMPLE 3: BEP-20 Token Analysis")
    print("="*60)
    
    # Example: BUSD token address on BSC
    token_address = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "token_info",
        "network": "mainnet",
        "token_address": token_address
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract token info
    token_info = result.get("token_info", {})
    if "standard" in token_info:
        print(f"\n🪙 Token Standard: {token_info.get('standard', 'Unknown')}")
        print(f"📝 Name: {token_info.get('name', 'N/A')}")
        print(f"🏷️  Symbol: {token_info.get('symbol', 'N/A')}")
        print(f"🔢 Decimals: {token_info.get('decimals', 'N/A')}")
    
    return result


async def example_gas_tracker():
    """Example: Track gas prices on BNB Chain"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Gas Price Tracking")
    print("="*60)
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "gas_tracker",
        "network": "mainnet"
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract gas info
    gas_info = result.get("gas_info", {})
    if "current_price_gwei" in gas_info:
        print(f"\n⛽ Current Gas Price: {gas_info['current_price_gwei']} Gwei")
        
        recommendations = gas_info.get("price_recommendations", {})
        print("\n📊 Recommended Gas Prices:")
        print(f"  🚀 Fast: {recommendations.get('fast', 0)} Gwei")
        print(f"  ⚡ Standard: {recommendations.get('standard', 0)} Gwei")
        print(f"  🐌 Slow: {recommendations.get('slow', 0)} Gwei")
        
        congestion = gas_info.get("network_characteristics", {}).get("congestion_level", "unknown")
        print(f"\n🌐 Network Congestion: {congestion}")
    
    return result


async def example_validator_info():
    """Example: Get BNB Chain validator information"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Validator Information")
    print("="*60)
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "validator_info",
        "network": "mainnet"
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract validator info
    validator_info = result.get("validator_info", {})
    if "consensus" in validator_info:
        print(f"\n🔐 Consensus: {validator_info['consensus']}")
        print(f"👥 Active Validators: {validator_info.get('validator_count', 'N/A')}")
        print(f"⏱️  Block Time: {validator_info.get('block_time', 'N/A')}")
    
    return result


async def example_staking_info():
    """Example: Get BNB staking information"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Staking Information")
    print("="*60)
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "staking_info",
        "network": "mainnet"
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract staking info
    staking_info = result.get("staking_info", {})
    if "mechanism" in staking_info:
        print(f"\n💎 Staking Mechanism: {staking_info['mechanism']}")
        print(f"🪙 Staking Token: {staking_info.get('staking_token', 'N/A')}")
        print(f"⏳ Unbonding Period: {staking_info.get('unbonding_period', 'N/A')}")
    
    return result


async def example_contract_verification():
    """Example: Verify a smart contract"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Contract Verification")
    print("="*60)
    
    # Example: PancakeSwap Router v2
    contract_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    
    registry = PluginRegistry()
    registry.discover()
    
    task = registry.create("bnb-chain", params={
        "operation": "contract_verify",
        "network": "mainnet",
        "contract_address": contract_address
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    # Extract verification info
    verification = result.get("contract_verification", {})
    if verification.get("is_contract"):
        print(f"\n✅ Contract verified at: {contract_address}")
        print(f"📦 Bytecode Size: {verification.get('bytecode_size_bytes', 0)} bytes")
        
        analysis = verification.get("analysis", {})
        print(f"🔍 Complexity: {analysis.get('complexity', 'unknown')}")
        print(f"🔗 Proxy: {analysis.get('possibly_proxy', False)}")
        
        explorer_url = verification.get("explorer_url", "")
        if explorer_url:
            print(f"\n🔗 View on BscScan: {explorer_url}")
    else:
        print(f"\n❌ Address is not a contract: {contract_address}")
    
    return result


async def example_comprehensive_analysis():
    """Example: Comprehensive analysis of an address"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Comprehensive Address Analysis")
    print("="*60)
    
    # Example address to analyze
    address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    
    registry = PluginRegistry()
    registry.discover()
    
    results = {}
    
    # Step 1: Check balance
    print("\n📊 Step 1: Checking balance...")
    balance_task = registry.create("bnb-chain", params={
        "operation": "balance",
        "network": "mainnet",
        "address": address
    })
    results["balance"] = await balance_task.run()
    
    balance_info = results["balance"].get("balance_info", {})
    is_contract = balance_info.get("is_contract", False)
    
    # Step 2: If it's a contract, verify it
    if is_contract:
        print("\n🔍 Step 2: Contract detected, verifying...")
        verify_task = registry.create("bnb-chain", params={
            "operation": "contract_verify",
            "network": "mainnet",
            "contract_address": address
        })
        results["verification"] = await verify_task.run()
    else:
        print("\n💼 Step 2: Regular wallet detected (not a contract)")
    
    # Step 3: Get current gas prices for reference
    print("\n⛽ Step 3: Checking current gas prices...")
    gas_task = registry.create("bnb-chain", params={
        "operation": "gas_tracker",
        "network": "mainnet"
    })
    results["gas"] = await gas_task.run()
    
    # Summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"\nAddress: {address}")
    print(f"Balance: {balance_info.get('balance_formatted', 'N/A')}")
    print(f"Type: {'Smart Contract' if is_contract else 'Wallet'}")
    print(f"Transactions: {balance_info.get('transaction_count', 0)}")
    
    if is_contract:
        verification = results.get("verification", {}).get("contract_verification", {})
        print(f"Contract Size: {verification.get('bytecode_size_bytes', 0)} bytes")
        print(f"Complexity: {verification.get('analysis', {}).get('complexity', 'unknown')}")
    
    gas_info = results.get("gas", {}).get("gas_info", {})
    print(f"\nCurrent Gas: {gas_info.get('current_price_gwei', 'N/A')} Gwei")
    
    return results


async def example_testnet_usage():
    """Example: Using BNB Chain testnet"""
    print("\n" + "="*60)
    print("EXAMPLE 9: BNB Chain Testnet Usage")
    print("="*60)
    
    registry = PluginRegistry()
    registry.discover()
    
    # Check testnet status
    task = registry.create("bnb-chain", params={
        "operation": "status",
        "network": "testnet"
    })
    
    result = await task.run()
    print(json.dumps(result, indent=2))
    
    print("\n🧪 Testnet is useful for:")
    print("  • Testing smart contracts before mainnet deployment")
    print("  • Experimenting with transactions without real BNB")
    print("  • Development and debugging")
    print("  • Getting free tBNB from the faucet")
    print("\n💧 Get testnet BNB: https://testnet.binance.org/faucet-smart")
    
    return result


async def run_all_examples():
    """Run all examples sequentially"""
    print("\n" + "="*60)
    print("BNB CHAIN SECURITY TOOLKIT - EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates all BNB Chain operations.")
    print("Note: Some operations require active internet connection.")
    print("="*60)
    
    try:
        # Run examples
        await example_chain_status()
        await asyncio.sleep(1)
        
        await example_balance_check()
        await asyncio.sleep(1)
        
        await example_token_analysis()
        await asyncio.sleep(1)
        
        await example_gas_tracker()
        await asyncio.sleep(1)
        
        await example_validator_info()
        await asyncio.sleep(1)
        
        await example_staking_info()
        await asyncio.sleep(1)
        
        await example_contract_verification()
        await asyncio.sleep(1)
        
        await example_comprehensive_analysis()
        await asyncio.sleep(1)
        
        await example_testnet_usage()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    print("Starting BNB Chain examples...")
    asyncio.run(run_all_examples())


if __name__ == "__main__":
    main()
