"""
Advanced reporting engine for SentinelX workflow results.
Generates professional reports in multiple formats (HTML, PDF, JSON, Markdown).
"""
from __future__ import annotations
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, Template
import markdown
from weasyprint import HTML, CSS
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

@dataclass
class ReportSection:
    """Represents a section in the security report."""
    title: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    chart_data: Optional[Dict[str, Any]] = None
    severity: str = "info"  # info, low, medium, high, critical

@dataclass 
class SecurityReport:
    """Comprehensive security assessment report."""
    title: str
    workflow_name: str
    execution_time: datetime
    duration: float
    status: str
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

class ReportGenerator:
    """Generates professional security reports from workflow results."""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.assets_dir = Path(__file__).parent / "assets"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure template and asset directories exist."""
        self.templates_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create default templates if they don't exist
        if not (self.templates_dir / "base_report.html").exists():
            self.create_default_templates()
    
    def create_default_templates(self):
        """Create default report templates."""
        # Create base HTML template
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { border-bottom: 3px solid #2c5aa0; padding-bottom: 20px; margin-bottom: 30px; }
        .title { color: #2c5aa0; font-size: 28px; font-weight: bold; margin: 0; }
        .subtitle { color: #666; font-size: 16px; margin: 5px 0 0 0; }
        .metadata { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metadata-item { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #2c5aa0; }
        .metadata-label { font-weight: bold; color: #2c5aa0; font-size: 12px; text-transform: uppercase; }
        .metadata-value { font-size: 16px; color: #333; margin-top: 5px; }
        .section { margin: 30px 0; padding: 20px; border-radius: 5px; border-left: 4px solid #ddd; }
        .section.critical { border-left-color: #dc3545; background-color: #fff5f5; }
        .section.high { border-left-color: #fd7e14; background-color: #fff8f0; }
        .section.medium { border-left-color: #ffc107; background-color: #fffbf0; }
        .section.low { border-left-color: #28a745; background-color: #f0fff4; }
        .section.info { border-left-color: #17a2b8; background-color: #f0f9ff; }
        .section-title { font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #333; }
        .vulnerability { margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .vuln-title { font-weight: bold; color: #dc3545; }
        .vuln-details { margin-top: 10px; color: #666; }
        .chart-container { margin: 20px 0; text-align: center; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .summary-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-number { font-size: 24px; font-weight: bold; }
        .summary-label { font-size: 12px; text-transform: uppercase; opacity: 0.8; }
        .status.completed { color: #28a745; font-weight: bold; }
        .status.failed { color: #dc3545; font-weight: bold; }
        .status.partial { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{{ report.title }}</h1>
            <p class="subtitle">Security Assessment Report - {{ report.workflow_name }}</p>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">Execution Time</div>
                <div class="metadata-value">{{ report.execution_time.strftime('%Y-%m-%d %H:%M:%S UTC') }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Duration</div>
                <div class="metadata-value">{{ "%.2f"|format(report.duration) }}s</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Status</div>
                <div class="metadata-value status {{ report.status }}">{{ report.status.title() }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Tasks Executed</div>
                <div class="metadata-value">{{ report.sections|length }}</div>
            </div>
        </div>

        {% if report.summary %}
        <div class="section info">
            <h2 class="section-title">Executive Summary</h2>
            <div class="summary-grid">
                {% for key, value in report.summary.items() %}
                <div class="summary-card">
                    <div class="summary-number">{{ value }}</div>
                    <div class="summary-label">{{ key.replace('_', ' ').title() }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% for section in report.sections %}
        <div class="section {{ section.severity }}">
            <h2 class="section-title">{{ section.title }}</h2>
            <div class="section-content">
                {{ section.content | safe }}
            </div>
            {% if section.chart_data %}
            <div class="chart-container">
                <div id="chart-{{ loop.index }}"></div>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    {% if report.sections|selectattr("chart_data")|list %}
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        {% for section in report.sections %}
        {% if section.chart_data %}
        Plotly.newPlot('chart-{{ loop.index }}', {{ section.chart_data|tojson }});
        {% endif %}
        {% endfor %}
    </script>
    {% endif %}
</body>
</html>'''
        
        with open(self.templates_dir / "base_report.html", "w") as f:
            f.write(base_template)
    
    def generate_from_workflow_result(self, workflow_result, title: str = None) -> SecurityReport:
        """Generate a security report from workflow execution results."""
        title = title or f"Security Assessment - {workflow_result.workflow_name}"
        
        report = SecurityReport(
            title=title,
            workflow_name=workflow_result.workflow_name,
            execution_time=datetime.utcnow(),
            duration=workflow_result.total_duration,
            status=workflow_result.status,
            metadata={
                "steps_completed": len(workflow_result.steps_completed),
                "total_steps": len(workflow_result.step_results) + len(workflow_result.errors),
                "error_count": len(workflow_result.errors)
            }
        )
        
        # Generate summary statistics
        total_vulns = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        # Process each workflow step result
        for step_name, step_result in workflow_result.step_results.items():
            section = self._process_step_result(step_name, step_result)
            report.sections.append(section)
            
            # Count vulnerabilities for summary
            if isinstance(step_result, dict) and "vulnerabilities" in step_result:
                vulns = step_result["vulnerabilities"]
                if isinstance(vulns, list):
                    total_vulns += len(vulns)
                    for vuln in vulns:
                        if isinstance(vuln, dict) and "severity" in vuln:
                            severity = vuln["severity"].lower()
                            if severity in severity_counts:
                                severity_counts[severity] += 1
        
        # Add summary
        report.summary = {
            "total_vulnerabilities": total_vulns,
            **severity_counts,
            "tasks_completed": len(workflow_result.steps_completed),
            "success_rate": f"{len(workflow_result.steps_completed) / max(1, len(workflow_result.steps_completed) + len(workflow_result.errors)) * 100:.1f}%"
        }
        
        return report
    
    def _process_step_result(self, step_name: str, step_result: Any) -> ReportSection:
        """Process individual step result into report section."""
        if not isinstance(step_result, dict):
            return ReportSection(
                title=step_name.replace("_", " ").title(),
                content=f"<pre>{json.dumps(step_result, indent=2, default=str)}</pre>",
                severity="info"
            )
        
        # Handle different task types
        if "vulnerabilities" in step_result:
            return self._process_vulnerability_result(step_name, step_result)
        elif "base_score" in step_result:
            return self._process_cvss_result(step_name, step_result)
        elif "shellcode" in step_result:
            return self._process_shellcode_result(step_name, step_result)
        else:
            return self._process_generic_result(step_name, step_result)
    
    def _process_vulnerability_result(self, step_name: str, result: Dict) -> ReportSection:
        """Process vulnerability scan results."""
        vulns = result.get("vulnerabilities", [])
        severity = "critical" if any(v.get("severity", "").lower() == "critical" for v in vulns) else "high"
        
        content = f"<p><strong>Total Vulnerabilities Found:</strong> {len(vulns)}</p>"
        
        if vulns:
            content += "<div class='vulnerabilities'>"
            for vuln in vulns[:10]:  # Limit to first 10 for readability
                content += f"""
                <div class="vulnerability">
                    <div class="vuln-title">{vuln.get('type', 'Unknown').replace('_', ' ').title()}</div>
                    <div class="vuln-details">
                        <strong>File:</strong> {vuln.get('file', 'N/A')}<br>
                        <strong>Line:</strong> {vuln.get('line', 'N/A')}<br>
                        <strong>Severity:</strong> {vuln.get('severity', 'N/A').title()}<br>
                        <strong>Description:</strong> {vuln.get('description', 'N/A')}
                    </div>
                </div>
                """
            if len(vulns) > 10:
                content += f"<p><em>... and {len(vulns) - 10} more vulnerabilities</em></p>"
            content += "</div>"
        
        # Create chart data for vulnerability distribution
        if vulns:
            severity_counts = {}
            for vuln in vulns:
                sev = vuln.get('severity', 'unknown').lower()
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            chart_data = [{
                'type': 'pie',
                'labels': list(severity_counts.keys()),
                'values': list(severity_counts.values()),
                'marker': {'colors': ['#dc3545', '#fd7e14', '#ffc107', '#28a745']}
            }]
        else:
            chart_data = None
        
        return ReportSection(
            title=f"{step_name.replace('_', ' ').title()} - Vulnerability Analysis",
            content=content,
            data=result,
            chart_data=chart_data,
            severity=severity
        )
    
    def _process_cvss_result(self, step_name: str, result: Dict) -> ReportSection:
        """Process CVSS scoring results."""
        score = result.get("base_score", 0)
        severity_map = {9.0: "critical", 7.0: "high", 4.0: "medium", 0.1: "low", 0: "info"}
        severity = next((sev for threshold, sev in severity_map.items() if score >= threshold), "info")
        
        content = f"""
        <div class="cvss-analysis">
            <p><strong>CVSS Base Score:</strong> {score} ({result.get('severity', 'Unknown')})</p>
            <p><strong>Vector:</strong> <code>{result.get('vector', 'N/A')}</code></p>
            
            <h4>Score Breakdown:</h4>
            <ul>
        """
        
        for metric, details in result.get("score_breakdown", {}).items():
            if isinstance(details, dict):
                content += f"<li><strong>{metric.replace('_', ' ').title()}:</strong> {details.get('value', 'N/A')} (Score: {details.get('score', 'N/A')})</li>"
        
        content += "</ul></div>"
        
        return ReportSection(
            title=f"{step_name.replace('_', ' ').title()} - CVSS Analysis",
            content=content,
            data=result,
            severity=severity
        )
    
    def _process_shellcode_result(self, step_name: str, result: Dict) -> ReportSection:
        """Process shellcode generation results."""
        content = f"""
        <div class="shellcode-analysis">
            <p><strong>Architecture:</strong> {result.get('arch', 'N/A')}</p>
            <p><strong>Payload Type:</strong> {result.get('payload', 'N/A')}</p>
            <p><strong>Size:</strong> {result.get('size', 'N/A')} bytes</p>
            
            <h4>Analysis:</h4>
            <ul>
                <li><strong>Null Bytes:</strong> {result.get('analysis', {}).get('null_bytes', 'N/A')}</li>
                <li><strong>Entropy:</strong> {result.get('analysis', {}).get('entropy', 'N/A')}</li>
                <li><strong>Printable Ratio:</strong> {result.get('analysis', {}).get('printable_ratio', 'N/A')}</li>
            </ul>
        </div>
        """
        
        return ReportSection(
            title=f"{step_name.replace('_', ' ').title()} - Shellcode Generation",
            content=content,
            data=result,
            severity="medium"
        )
    
    def _process_generic_result(self, step_name: str, result: Dict) -> ReportSection:
        """Process generic task results."""
        content = "<div class='generic-result'>"
        
        for key, value in result.items():
            if key in ["status", "summary", "analysis"]:
                content += f"<p><strong>{key.title()}:</strong> {value}</p>"
        
        content += f"<details><summary>Full Results</summary><pre>{json.dumps(result, indent=2, default=str)}</pre></details>"
        content += "</div>"
        
        return ReportSection(
            title=f"{step_name.replace('_', ' ').title()} - Analysis Results",
            content=content,
            data=result,
            severity="info"
        )
    
    def render_html(self, report: SecurityReport) -> str:
        """Render report as HTML."""
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template("base_report.html")
        return template.render(report=report)
    
    def render_markdown(self, report: SecurityReport) -> str:
        """Render report as Markdown."""
        md_content = f"""# {report.title}

**Workflow:** {report.workflow_name}  
**Execution Time:** {report.execution_time.strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Duration:** {report.duration:.2f}s  
**Status:** {report.status.title()}  

## Executive Summary

"""
        
        for key, value in report.summary.items():
            md_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        md_content += "\n## Detailed Results\n\n"
        
        for section in report.sections:
            md_content += f"### {section.title}\n\n"
            # Convert HTML to markdown-friendly format
            content = section.content.replace('<p>', '').replace('</p>', '\n\n')
            content = content.replace('<strong>', '**').replace('</strong>', '**')
            content = content.replace('<code>', '`').replace('</code>', '`')
            md_content += content + "\n\n"
        
        return md_content
    
    def export_pdf(self, report: SecurityReport, output_path: Path) -> None:
        """Export report as PDF."""
        html_content = self.render_html(report)
        
        # Create CSS for PDF
        css_content = """
        @page { size: A4; margin: 2cm; }
        body { font-size: 12px; line-height: 1.4; }
        .container { box-shadow: none; padding: 0; }
        .chart-container { page-break-inside: avoid; }
        """
        
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_content)]
        )
    
    def export_json(self, report: SecurityReport, output_path: Path) -> None:
        """Export report as JSON."""
        report_dict = {
            "title": report.title,
            "workflow_name": report.workflow_name,
            "execution_time": report.execution_time.isoformat(),
            "duration": report.duration,
            "status": report.status,
            "metadata": report.metadata,
            "summary": report.summary,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "data": section.data,
                    "severity": section.severity
                }
                for section in report.sections
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
    
    def export_report(self, report: SecurityReport, output_path: Path, format: str = "html") -> None:
        """Export report in specified format."""
        output_path = Path(output_path)
        
        if format.lower() == "html":
            html_content = self.render_html(report)
            with open(output_path.with_suffix('.html'), 'w') as f:
                f.write(html_content)
        elif format.lower() == "pdf":
            self.export_pdf(report, output_path.with_suffix('.pdf'))
        elif format.lower() == "markdown" or format.lower() == "md":
            md_content = self.render_markdown(report)
            with open(output_path.with_suffix('.md'), 'w') as f:
                f.write(md_content)
        elif format.lower() == "json":
            self.export_json(report, output_path.with_suffix('.json'))
        else:
            raise ValueError(f"Unsupported format: {format}")
