#!/usr/bin/env python3
"""
Smart Contract Security Audit Example

This example demonstrates a comprehensive smart contract security audit
using multiple SentinelX tasks in sequence.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry
from sentinelx.core.task import TaskError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartContractAuditor:
    """Comprehensive smart contract security auditor."""
    
    def __init__(self, context: Context):
        self.context = context
        self.results = {}
        
    async def analyze_contract(self, contract_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis of a smart contract.
        
        Args:
            contract_path: Path to the Solidity contract file
            
        Returns:
            Dictionary containing all analysis results
        """
        logger.info(f"Starting comprehensive audit of {contract_path}")
        
        # Validate contract exists
        if not Path(contract_path).exists():
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
        
        # Step 1: Static Analysis with Slither
        await self._run_slither_analysis(contract_path)
        
        # Step 2: Symbolic Execution with Mythril
        await self._run_mythril_analysis(contract_path)
        
        # Step 3: Calculate CVSS scores for findings
        await self._calculate_cvss_scores()
        
        # Step 4: Generate comprehensive report
        report = self._generate_audit_report()
        
        return report
    
    async def _run_slither_analysis(self, contract_path: str):
        """Run Slither static analysis."""
        logger.info("Running Slither static analysis...")
        
        try:
            task = PluginRegistry.create(
                "slither",
                contract_path=contract_path,
                format="json"
            )
            
            result = await task.execute(self.context)
            self.results['slither'] = result
            
            logger.info(f"Slither analysis completed. Found {result.get('vulnerabilities_found', 0)} issues")
            
        except TaskError as e:
            logger.warning(f"Slither analysis failed: {e}")
            self.results['slither'] = {"status": "failed", "error": str(e)}
    
    async def _run_mythril_analysis(self, contract_path: str):
        """Run Mythril symbolic execution."""
        logger.info("Running Mythril symbolic execution...")
        
        try:
            task = PluginRegistry.create(
                "mythril",
                contract_path=contract_path,
                timeout=600,
                max_depth=12
            )
            
            result = await task.execute(self.context)
            self.results['mythril'] = result
            
            logger.info(f"Mythril analysis completed. Found {result.get('issues_found', 0)} issues")
            
        except TaskError as e:
            logger.warning(f"Mythril analysis failed: {e}")
            self.results['mythril'] = {"status": "failed", "error": str(e)}
    
    async def _calculate_cvss_scores(self):
        """Calculate CVSS scores for identified vulnerabilities."""
        logger.info("Calculating CVSS scores for vulnerabilities...")
        
        vulnerabilities = []
        
        # Collect vulnerabilities from all tools
        if 'slither' in self.results and 'results' in self.results['slither']:
            slither_vulns = self.results['slither']['results'].get('vulnerabilities', [])
            vulnerabilities.extend(slither_vulns)
        
        if 'mythril' in self.results and 'results' in self.results['mythril']:
            mythril_issues = self.results['mythril']['results'].get('issues', [])
            vulnerabilities.extend(mythril_issues)
        
        # Calculate CVSS scores
        cvss_results = []
        
        for vuln in vulnerabilities:
            try:
                # Map vulnerability to CVSS vector
                cvss_vector = self._map_vulnerability_to_cvss(vuln)
                
                if cvss_vector:
                    task = PluginRegistry.create("cvss", vector=cvss_vector)
                    result = await task.execute(self.context)
                    
                    cvss_results.append({
                        "vulnerability": vuln,
                        "cvss_vector": cvss_vector,
                        "base_score": result.get('base_score'),
                        "severity": result.get('severity')
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to calculate CVSS for vulnerability: {e}")
                continue
        
        self.results['cvss_scores'] = cvss_results
        logger.info(f"Calculated CVSS scores for {len(cvss_results)} vulnerabilities")
    
    def _map_vulnerability_to_cvss(self, vulnerability: Dict) -> str:
        """
        Map a vulnerability to a CVSS 3.1 vector string.
        
        This is a simplified mapping - in practice, you'd want more sophisticated
        logic based on the specific vulnerability type and context.
        """
        # Default CVSS vector for smart contract vulnerabilities
        base_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U"
        
        # Determine impact based on vulnerability type
        vuln_type = vulnerability.get('type', '').lower()
        vuln_severity = vulnerability.get('severity', '').lower()
        
        if 'reentrancy' in vuln_type:
            return f"{base_vector}/C:H/I:H/A:H"  # High impact for reentrancy
        elif 'integer overflow' in vuln_type:
            return f"{base_vector}/C:H/I:H/A:L"  # High confidentiality/integrity impact
        elif 'unchecked call' in vuln_type:
            return f"{base_vector}/C:L/I:H/A:L"  # Mainly integrity impact
        elif vuln_severity == 'high':
            return f"{base_vector}/C:H/I:H/A:H"
        elif vuln_severity == 'medium':
            return f"{base_vector}/C:L/I:L/A:L"
        elif vuln_severity == 'low':
            return f"{base_vector}/C:N/I:L/A:N"
        else:
            return f"{base_vector}/C:L/I:L/A:N"  # Default low impact
    
    def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        logger.info("Generating comprehensive audit report...")
        
        # Aggregate statistics
        stats = {
            "total_vulnerabilities": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 0,
            "low_vulnerabilities": 0,
            "tools_used": [],
            "analysis_duration": 0
        }
        
        # Process results from each tool
        tools_results = {}
        
        for tool_name, result in self.results.items():
            if tool_name == 'cvss_scores':
                continue
                
            if result.get('status') == 'completed':
                stats['tools_used'].append(tool_name)
                stats['analysis_duration'] += result.get('duration', 0)
                
                # Count vulnerabilities
                if tool_name == 'slither':
                    vulns = result.get('results', {}).get('vulnerabilities', [])
                    stats['total_vulnerabilities'] += len(vulns)
                    
                elif tool_name == 'mythril':
                    issues = result.get('results', {}).get('issues', [])
                    stats['total_vulnerabilities'] += len(issues)
                
                tools_results[tool_name] = result
        
        # Process CVSS scores
        cvss_scores = self.results.get('cvss_scores', [])
        for score_info in cvss_scores:
            severity = score_info.get('severity', '').lower()
            if severity == 'critical':
                stats['critical_vulnerabilities'] += 1
            elif severity == 'high':
                stats['high_vulnerabilities'] += 1
            elif severity == 'medium':
                stats['medium_vulnerabilities'] += 1
            elif severity == 'low':
                stats['low_vulnerabilities'] += 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations(stats, tools_results)
        
        return {
            "audit_summary": stats,
            "tool_results": tools_results,
            "cvss_analysis": cvss_scores,
            "recommendations": recommendations,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    def _generate_recommendations(self, stats: Dict, results: Dict) -> List[str]:
        """Generate security recommendations based on audit results."""
        recommendations = []
        
        if stats['critical_vulnerabilities'] > 0:
            recommendations.append(
                "🚨 CRITICAL: Address critical vulnerabilities immediately before deployment"
            )
        
        if stats['high_vulnerabilities'] > 0:
            recommendations.append(
                "⚠️  HIGH: Resolve high-severity vulnerabilities before production"
            )
        
        if stats['total_vulnerabilities'] == 0:
            recommendations.append(
                "✅ GOOD: No vulnerabilities detected by static analysis tools"
            )
            recommendations.append(
                "💡 Consider additional testing: unit tests, integration tests, formal verification"
            )
        
        if stats['medium_vulnerabilities'] > 5:
            recommendations.append(
                "📋 MEDIUM: Consider code refactoring to address medium-severity issues"
            )
        
        # Tool-specific recommendations
        if 'slither' in results:
            recommendations.append(
                "🔍 Run Slither with additional detectors for comprehensive analysis"
            )
        
        if 'mythril' in results:
            recommendations.append(
                "⚡ Consider increasing Mythril analysis depth for deeper symbolic execution"
            )
        
        recommendations.extend([
            "🧪 Implement comprehensive test suite with high code coverage",
            "🔐 Consider professional security audit for high-value contracts",
            "📊 Implement monitoring and alerting for deployed contracts",
            "🔄 Establish regular security review process for code updates"
        ])
        
        return recommendations

# Example usage functions
async def audit_sample_contract():
    """Audit a sample contract."""
    # Create a sample vulnerable contract for demonstration
    sample_contract = Path("vulnerable_token.sol")
    sample_contract.write_text("""
pragma solidity ^0.8.0;

contract VulnerableToken {
    mapping(address => uint256) public balances;
    mapping(address => bool) public isOwner;
    
    constructor() {
        isOwner[msg.sender] = true;
        balances[msg.sender] = 1000000;
    }
    
    // Vulnerable: Reentrancy attack possible
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount; // State update after external call
    }
    
    // Vulnerable: Integer overflow (if using older Solidity)
    function mint(address to, uint256 amount) public {
        require(isOwner[msg.sender], "Not owner");
        balances[to] += amount; // Potential overflow
    }
    
    // Vulnerable: Unchecked external call
    function transfer(address to, uint256 amount) public returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        // Vulnerable: Unchecked call return value
        to.call(abi.encodeWithSignature("tokenReceived(uint256)", amount));
        
        return true;
    }
}
""")
    
    try:
        # Load context and create auditor
        context = Context.load("config.yaml")
        auditor = SmartContractAuditor(context)
        
        # Run comprehensive audit
        audit_report = await auditor.analyze_contract(str(sample_contract))
        
        # Display results
        print("\n" + "=" * 60)
        print("SMART CONTRACT SECURITY AUDIT REPORT")
        print("=" * 60)
        
        summary = audit_report['audit_summary']
        print(f"\n📊 AUDIT SUMMARY:")
        print(f"   Total Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"   Critical: {summary['critical_vulnerabilities']}")
        print(f"   High: {summary['high_vulnerabilities']}")
        print(f"   Medium: {summary['medium_vulnerabilities']}")
        print(f"   Low: {summary['low_vulnerabilities']}")
        print(f"   Tools Used: {', '.join(summary['tools_used'])}")
        print(f"   Analysis Duration: {summary['analysis_duration']:.2f}s")
        
        print(f"\n🔍 DETAILED FINDINGS:")
        for tool_name, result in audit_report['tool_results'].items():
            print(f"\n{tool_name.upper()} ANALYSIS:")
            if result.get('status') == 'completed':
                print(f"   ✅ Status: Completed")
                if 'results' in result:
                    tool_result = result['results']
                    if 'vulnerabilities' in tool_result:
                        for vuln in tool_result['vulnerabilities'][:3]:  # Show first 3
                            print(f"   • {vuln.get('type', 'Unknown')}: {vuln.get('description', 'No description')}")
                    elif 'issues' in tool_result:
                        for issue in tool_result['issues'][:3]:  # Show first 3
                            print(f"   • {issue.get('title', 'Unknown')}: {issue.get('description', 'No description')}")
            else:
                print(f"   ❌ Status: {result.get('status', 'Unknown')}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        print(f"\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(audit_report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Save detailed report
        report_file = Path("audit_report.json")
        report_file.write_text(json.dumps(audit_report, indent=2))
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        return audit_report
        
    finally:
        # Clean up
        if sample_contract.exists():
            sample_contract.unlink()

async def main():
    """Main example runner."""
    print("SentinelX Smart Contract Security Audit Example")
    print("=" * 50)
    
    # Discover available tasks
    PluginRegistry.discover()
    
    # Run comprehensive audit
    await audit_sample_contract()
    
    print("\n" + "=" * 50)
    print("Audit example completed!")

if __name__ == "__main__":
    asyncio.run(main())
