# SentinelX Advanced Features Guide

This guide covers the advanced features of SentinelX including Docker deployment, performance monitoring, and advanced reporting capabilities.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Performance Monitoring](#performance-monitoring)
3. [Advanced Reporting](#advanced-reporting)
4. [Configuration Management](#configuration-management)
5. [Integration Patterns](#integration-patterns)
6. [Security Considerations](#security-considerations)

## Docker Deployment

SentinelX provides comprehensive Docker support for sandboxed execution and scalable deployments.

### Container-based Task Execution

Run security tasks in isolated Docker containers for enhanced security:

```bash
# Setup Docker environment
sentinelx docker setup

# Run task in container
sentinelx docker run slither -p "{contract_path: 'MyToken.sol'}"

# Cleanup containers
sentinelx docker cleanup
```

### Configuration

```yaml
# config.yaml
sentinelx:
  docker:
    enabled: true
    base_image: "python:3.9-slim"
    network: "bridge"
    memory_limit: "2g"
    cpu_limit: "2"
    timeout: 3600
    auto_cleanup: true
    
    # Custom images for specific tasks
    task_images:
      slither: "trailofbits/slither:latest"
      mythril: "mythril/myth:latest"
      
    # Volume mounts
    volumes:
      - "${PWD}/contracts:/contracts:ro"
      - "${PWD}/output:/output:rw"
    
    # Environment variables
    environment:
      - "PYTHONPATH=/app"
      - "DEBIAN_FRONTEND=noninteractive"
```

### Custom Docker Images

Create specialized images for your tasks:

```dockerfile
# Dockerfile.security-tools
FROM python:3.9-slim

# Install security tools
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python security tools
RUN pip install slither-analyzer mythril

# Install SentinelX
COPY . /app
WORKDIR /app
RUN pip install -e .

# Set entrypoint
ENTRYPOINT ["sentinelx"]
```

### Orchestration with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  sentinelx:
    build: .
    volumes:
      - ./contracts:/app/contracts:ro
      - ./output:/app/output:rw
      - ./config:/app/config:ro
    environment:
      - SENTINELX_CONFIG=/app/config/config.yaml
    command: ["run", "slither", "-p", "{contract_path: '/app/contracts/MyToken.sol'}"]
    
  sentinelx-worker:
    build: .
    volumes:
      - ./contracts:/app/contracts:ro
      - ./output:/app/output:rw
    environment:
      - SENTINELX_WORKER=true
    command: ["worker", "start"]
```

## Performance Monitoring

Monitor and optimize task performance with built-in profiling tools.

### Performance Profiling

```bash
# Profile a single task
sentinelx perf profile slither -p "{contract_path: 'MyToken.sol'}" --iterations 5

# Profile multiple tasks
sentinelx perf profile slither,mythril -p "{contract_path: 'MyToken.sol'}"

# Profile with custom metrics
sentinelx perf profile slither --metrics cpu,memory,io --output profile_report.json
```

### Benchmark Suite

```bash
# Run benchmark suite
sentinelx perf benchmark --suite smart_contract_analysis

# Custom benchmark
sentinelx perf benchmark --tasks slither,mythril --test-data benchmark_contracts/

# Comparative benchmarking
sentinelx perf benchmark --compare-with previous_results.json
```

### Performance Configuration

```yaml
# config.yaml
sentinelx:
  performance:
    profiling_enabled: true
    benchmark_enabled: true
    metrics_collection: true
    
    # Profiling settings
    profiling:
      sample_rate: 0.1  # 10% sampling
      include_memory: true
      include_cpu: true
      include_io: true
      
    # Benchmark settings
    benchmark:
      iterations: 10
      warmup_iterations: 2
      timeout: 1800
      
    # Metrics retention
    metrics:
      retention_days: 90
      aggregation_interval: 3600  # 1 hour
      storage_backend: "file"  # file, influxdb, prometheus
```

### Performance Optimization

```python
# examples/performance_optimization.py
import asyncio
from sentinelx.performance import PerformanceProfiler, BenchmarkSuite
from sentinelx.core.context import Context

async def optimize_task_performance():
    """Example of performance optimization workflow."""
    
    context = Context.load("config.yaml")
    profiler = PerformanceProfiler(context)
    
    # Profile current performance
    baseline_results = await profiler.profile_task(
        "slither",
        iterations=10,
        contract_path="MyToken.sol"
    )
    
    # Analyze bottlenecks
    bottlenecks = profiler.analyze_bottlenecks(baseline_results)
    
    # Apply optimizations
    optimizations = profiler.suggest_optimizations(bottlenecks)
    
    # Test optimized performance
    optimized_results = await profiler.profile_task(
        "slither",
        iterations=10,
        contract_path="MyToken.sol",
        optimizations=optimizations
    )
    
    # Compare results
    improvement = profiler.compare_results(baseline_results, optimized_results)
    
    print(f"Performance improvement: {improvement['percentage']:.1f}%")
    print(f"Execution time reduced by: {improvement['time_saved']:.2f}s")
```

## Advanced Reporting

Generate comprehensive security reports with visualizations and executive summaries.

### Report Generation

```bash
# Generate HTML report
sentinelx report generate results.json --format html --template security_audit

# Generate PDF report
sentinelx report generate results.json --format pdf --template executive_summary

# Generate custom report
sentinelx report generate results.json --template custom_template.html --output audit_report.html
```

### Report Templates

Create custom report templates:

```html
<!-- templates/security_audit.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Security Audit Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .critical { color: #d32f2f; font-weight: bold; }
        .high { color: #ff9800; font-weight: bold; }
        .medium { color: #ffc107; }
        .low { color: #4caf50; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Audit Report</h1>
        <p>Generated: {{ timestamp }}</p>
        <p>Target: {{ target }}</p>
    </div>
    
    <h2>Executive Summary</h2>
    <div class="summary">
        <p>Total Vulnerabilities: {{ total_vulnerabilities }}</p>
        <p class="critical">Critical: {{ critical_count }}</p>
        <p class="high">High: {{ high_count }}</p>
        <p class="medium">Medium: {{ medium_count }}</p>
        <p class="low">Low: {{ low_count }}</p>
    </div>
    
    <h2>Vulnerability Details</h2>
    {% for vulnerability in vulnerabilities %}
    <div class="vulnerability {{ vulnerability.severity }}">
        <h3>{{ vulnerability.title }}</h3>
        <p><strong>Severity:</strong> {{ vulnerability.severity }}</p>
        <p><strong>CVSS Score:</strong> {{ vulnerability.cvss_score }}</p>
        <p><strong>Description:</strong> {{ vulnerability.description }}</p>
        <p><strong>Remediation:</strong> {{ vulnerability.remediation }}</p>
    </div>
    {% endfor %}
    
    <h2>Recommendations</h2>
    <ul>
    {% for recommendation in recommendations %}
        <li>{{ recommendation }}</li>
    {% endfor %}
    </ul>
    
    <div class="chart">
        <canvas id="vulnerabilityChart"></canvas>
    </div>
    
    <script>
        // Chart.js visualization code
        const ctx = document.getElementById('vulnerabilityChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [{{ critical_count }}, {{ high_count }}, {{ medium_count }}, {{ low_count }}],
                    backgroundColor: ['#d32f2f', '#ff9800', '#ffc107', '#4caf50']
                }]
            }
        });
    </script>
</body>
</html>
```

### Report Configuration

```yaml
# config.yaml
sentinelx:
  reporting:
    default_format: "html"
    template_directory: "./templates"
    output_directory: "./reports"
    
    # Report settings
    include_charts: true
    include_executive_summary: true
    include_technical_details: true
    include_remediation: true
    
    # Branding
    organization_name: "Your Organization"
    organization_logo: "./assets/logo.png"
    report_footer: "Confidential - Internal Use Only"
    
    # Chart settings
    charts:
      vulnerability_distribution: true
      severity_trends: true
      tool_comparison: true
      risk_matrix: true
    
    # Export options
    export:
      formats: ["html", "pdf", "json", "csv"]
      attachments: true
      compression: true
```

### Programmatic Report Generation

```python
# examples/report_generation.py
from sentinelx.reporting import ReportGenerator, SecurityReport
from sentinelx.core.context import Context

async def generate_custom_report():
    """Generate a custom security report."""
    
    context = Context.load("config.yaml")
    generator = ReportGenerator(context)
    
    # Load analysis results
    results = [
        {
            "task": "slither",
            "vulnerabilities": [
                {
                    "title": "Reentrancy Vulnerability",
                    "severity": "high",
                    "cvss_score": 7.5,
                    "description": "Contract is vulnerable to reentrancy attacks",
                    "remediation": "Use reentrancy guards and checks-effects-interactions pattern"
                }
            ]
        }
    ]
    
    # Generate report
    report = generator.generate_report(
        results=results,
        template="security_audit",
        format="html",
        include_charts=True,
        include_executive_summary=True
    )
    
    # Save report
    report.save("comprehensive_audit_report.html")
    
    # Generate executive summary
    exec_summary = generator.generate_executive_summary(report)
    exec_summary.save("executive_summary.pdf")
    
    print(f"Report generated: {report.filepath}")
    print(f"Executive summary: {exec_summary.filepath}")
```

## Configuration Management

Advanced configuration management for complex deployments.

### Environment-specific Configurations

```bash
# Development environment
sentinelx config set --env dev --key debug --value true

# Production environment  
sentinelx config set --env prod --key docker.enabled --value true

# Staging environment
sentinelx config set --env staging --key performance.profiling_enabled --value true
```

### Configuration Validation

```yaml
# config_schema.yaml
sentinelx:
  type: object
  properties:
    debug:
      type: boolean
      default: false
    timeout:
      type: integer
      minimum: 1
      maximum: 86400
    docker:
      type: object
      properties:
        enabled:
          type: boolean
          default: false
        memory_limit:
          type: string
          pattern: "^[0-9]+[kmg]$"
  required: ["timeout"]
```

### Configuration Templates

```bash
# Generate configuration template
sentinelx config template --type basic > config.yaml

# Generate advanced configuration
sentinelx config template --type advanced --include-docker --include-performance > advanced_config.yaml

# Validate configuration
sentinelx config validate config.yaml
```

## Integration Patterns

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install SentinelX
        run: |
          pip install sentinelx
          
      - name: Run Security Scan
        run: |
          sentinelx workflow run .github/workflows/security_workflow.yaml
          
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: security-scan-results
          path: ./scan_results/
```

### API Integration

```python
# examples/api_integration.py
from sentinelx.core.api import SentinelXAPI
from sentinelx.core.context import Context

async def api_integration_example():
    """Example of API integration."""
    
    # Initialize API client
    api = SentinelXAPI(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Submit analysis job
    job = await api.submit_job(
        task="slither",
        parameters={"contract_path": "MyToken.sol"},
        priority="high"
    )
    
    # Monitor job status
    while job.status not in ["completed", "failed"]:
        await asyncio.sleep(5)
        job = await api.get_job_status(job.id)
        print(f"Job {job.id} status: {job.status}")
    
    # Get results
    if job.status == "completed":
        results = await api.get_job_results(job.id)
        print(f"Analysis completed: {results['summary']}")
```

### Webhook Integration

```python
# examples/webhook_integration.py
from fastapi import FastAPI, BackgroundTasks
from sentinelx.core.registry import PluginRegistry

app = FastAPI()

@app.post("/webhook/security-scan")
async def security_scan_webhook(
    payload: dict,
    background_tasks: BackgroundTasks
):
    """Webhook endpoint for triggering security scans."""
    
    # Extract information from webhook payload
    repository = payload.get("repository", {})
    commit = payload.get("head_commit", {})
    
    # Schedule security scan
    background_tasks.add_task(
        run_security_scan,
        repository_url=repository.get("clone_url"),
        commit_hash=commit.get("id")
    )
    
    return {"status": "accepted", "message": "Security scan scheduled"}

async def run_security_scan(repository_url: str, commit_hash: str):
    """Run security scan on repository."""
    
    # Clone repository
    repo_path = f"./repos/{commit_hash}"
    subprocess.run(["git", "clone", repository_url, repo_path])
    
    # Run SentinelX workflow
    workflow_result = await run_workflow(
        "comprehensive_security_scan.yaml",
        variables={"repository_path": repo_path}
    )
    
    # Send results via webhook
    await send_results_webhook(workflow_result)
```

## Security Considerations

### Secure Configuration

```yaml
# config.yaml - Security hardening
sentinelx:
  security:
    # Sandboxing
    sandbox_enabled: true
    sandbox_type: "docker"  # docker, firejail, chroot
    
    # Resource limits
    max_memory: "4g"
    max_cpu: "4"
    max_disk: "10g"
    max_network_bandwidth: "100m"
    
    # Access controls
    allowed_file_extensions: [".sol", ".py", ".js", ".ts"]
    blocked_file_patterns: ["*.exe", "*.bat", "*.sh"]
    max_file_size: "100MB"
    
    # Network security
    network_isolation: true
    allowed_domains: ["github.com", "pypi.org"]
    proxy_enabled: false
    
    # Logging and monitoring
    audit_logging: true
    log_file: "/var/log/sentinelx/audit.log"
    log_level: "INFO"
    
    # Encryption
    encrypt_results: true
    encryption_key: "${SENTINELX_ENCRYPTION_KEY}"
```

### Best Practices

1. **Principle of Least Privilege**
   - Run tasks with minimal required permissions
   - Use dedicated service accounts
   - Implement proper access controls

2. **Input Validation**
   - Validate all input parameters
   - Sanitize file paths and URLs
   - Implement size and format limits

3. **Secure Communication**
   - Use HTTPS for all API communications
   - Implement proper authentication
   - Use encrypted channels for sensitive data

4. **Audit and Monitoring**
   - Enable comprehensive logging
   - Monitor for suspicious activities
   - Implement alerting for security events

5. **Regular Updates**
   - Keep SentinelX and dependencies updated
   - Monitor security advisories
   - Implement automated security scanning

### Compliance Integration

```python
# examples/compliance_integration.py
from sentinelx.compliance import ComplianceChecker
from sentinelx.core.context import Context

async def compliance_check_example():
    """Example of compliance checking."""
    
    context = Context.load("config.yaml")
    checker = ComplianceChecker(context)
    
    # Check SOC 2 compliance
    soc2_results = await checker.check_soc2_compliance(
        scan_results="audit_results.json"
    )
    
    # Check GDPR compliance
    gdpr_results = await checker.check_gdpr_compliance(
        data_flows="data_flow_analysis.json"
    )
    
    # Generate compliance report
    compliance_report = checker.generate_compliance_report([
        soc2_results,
        gdpr_results
    ])
    
    compliance_report.save("compliance_report.pdf")
```

This advanced features guide provides comprehensive coverage of SentinelX's advanced capabilities, enabling organizations to implement enterprise-grade security analysis workflows with proper monitoring, reporting, and compliance integration.
