"""
Test suite for SentinelX advanced reporting functionality.
"""
import pytest
import tempfile
import yaml
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Test the conditional import behavior
try:
    from sentinelx.reporting import (
        ReportGenerator, SecurityReport, ReportSection
    )
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False

pytestmark = pytest.mark.skipif(not HAS_REPORTING, reason="Reporting module not available")

@pytest.fixture
def sample_report_section():
    """Fixture providing a sample report section."""
    return ReportSection(
        title="Test Vulnerability",
        content="<p>This is a test vulnerability finding.</p>",
        data={"severity": "high", "cvss": 8.5, "affected_files": ["test.php"]},
        severity="high"
    )

@pytest.fixture
def sample_security_report(sample_report_section):
    """Fixture providing a sample security report."""
    report = SecurityReport(
        title="Test Security Assessment",
        workflow_name="test_workflow",
        execution_time=datetime.now(),
        duration=120.5,
        status="completed"
    )
    report.sections.append(sample_report_section)
    report.summary = {
        "total_vulnerabilities": 5,
        "critical_issues": 1,
        "high_issues": 2,
        "medium_issues": 1,
        "low_issues": 1
    }
    return report

class TestReportSection:
    """Test ReportSection data structure."""
    
    def test_section_initialization(self):
        """Test ReportSection initialization."""
        section = ReportSection(
            title="Test Section",
            content="Test content",
            data={"key": "value"},
            severity="medium"
        )
        
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.data["key"] == "value"
        assert section.severity == "medium"
        assert section.chart_data is None
    
    def test_section_defaults(self):
        """Test ReportSection default values."""
        section = ReportSection(
            title="Minimal Section",
            content="Minimal content"
        )
        
        assert isinstance(section.data, dict)
        assert section.severity == "info"
        assert section.chart_data is None
    
    def test_section_with_chart_data(self):
        """Test ReportSection with chart data."""
        chart_data = {
            "data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}],
            "layout": {"title": "Test Chart"}
        }
        
        section = ReportSection(
            title="Chart Section",
            content="Section with chart",
            chart_data=chart_data
        )
        
        assert section.chart_data is not None
        assert "data" in section.chart_data
        assert "layout" in section.chart_data

class TestSecurityReport:
    """Test SecurityReport data structure."""
    
    def test_report_initialization(self):
        """Test SecurityReport initialization."""
        execution_time = datetime.now()
        report = SecurityReport(
            title="Test Report",
            workflow_name="test_workflow",
            execution_time=execution_time,
            duration=60.0,
            status="completed"
        )
        
        assert report.title == "Test Report"
        assert report.workflow_name == "test_workflow"
        assert report.execution_time == execution_time
        assert report.duration == 60.0
        assert report.status == "completed"
        assert isinstance(report.sections, list)
        assert isinstance(report.metadata, dict)
        assert isinstance(report.summary, dict)
    
    def test_report_defaults(self):
        """Test SecurityReport default values."""
        report = SecurityReport(
            title="Minimal Report",
            workflow_name="minimal_workflow",
            execution_time=datetime.now(),
            duration=0.0,
            status="pending"
        )
        
        assert len(report.sections) == 0
        assert len(report.metadata) == 0
        assert len(report.summary) == 0
    
    def test_report_with_sections(self, sample_report_section):
        """Test SecurityReport with sections."""
        report = SecurityReport(
            title="Report with Sections",
            workflow_name="test_workflow",
            execution_time=datetime.now(),
            duration=30.0,
            status="completed"
        )
        
        report.sections.append(sample_report_section)
        
        assert len(report.sections) == 1
        assert report.sections[0].title == "Test Vulnerability"
        assert report.sections[0].severity == "high"

class TestReportGenerator:
    """Test ReportGenerator functionality."""
    
    def test_generator_initialization(self):
        """Test ReportGenerator initialization."""
        generator = ReportGenerator()
        
        assert generator.templates_dir.name == "templates"
        assert generator.assets_dir.name == "assets"
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock the generator to use our temp directory
            generator = ReportGenerator()
            generator.templates_dir = temp_path / "templates"
            generator.assets_dir = temp_path / "assets"
            
            generator.ensure_directories()
            
            assert generator.templates_dir.exists()
            assert generator.assets_dir.exists()
    
    def test_generate_summary_basic(self, sample_security_report):
        """Test basic summary generation."""
        generator = ReportGenerator()
        summary = generator.generate_summary(sample_security_report)
        
        assert "total_sections" in summary
        assert summary["total_sections"] == 1
        assert "severity_counts" in summary
        assert "high" in summary["severity_counts"]
        assert summary["severity_counts"]["high"] == 1
    
    def test_generate_summary_multiple_sections(self):
        """Test summary generation with multiple sections."""
        report = SecurityReport(
            title="Multi-section Report",
            workflow_name="test",
            execution_time=datetime.now(),
            duration=60.0,
            status="completed"
        )
        
        # Add sections with different severities
        severities = ["critical", "high", "medium", "low", "info"]
        for severity in severities:
            section = ReportSection(
                title=f"{severity.title()} Issue",
                content=f"<p>{severity.title()} severity issue</p>",
                severity=severity
            )
            report.sections.append(section)
        
        generator = ReportGenerator()
        summary = generator.generate_summary(report)
        
        assert summary["total_sections"] == 5
        assert len(summary["severity_counts"]) == 5
        for severity in severities:
            assert summary["severity_counts"][severity] == 1
    
    def test_create_vulnerability_chart(self):
        """Test vulnerability chart creation."""
        generator = ReportGenerator()
        
        severity_counts = {
            "critical": 2,
            "high": 5,
            "medium": 3,
            "low": 1,
            "info": 0
        }
        
        chart_data = generator.create_vulnerability_chart(severity_counts)
        
        assert "data" in chart_data
        assert len(chart_data["data"]) == 1  # One trace
        trace = chart_data["data"][0]
        assert trace["type"] == "bar"
        assert "x" in trace
        assert "y" in trace
        assert "layout" in chart_data
    
    def test_create_timeline_chart(self):
        """Test timeline chart creation."""
        generator = ReportGenerator()
        
        report = SecurityReport(
            title="Timeline Report",
            workflow_name="test",
            execution_time=datetime.now(),
            duration=120.0,
            status="completed"
        )
        
        # Add sections with timestamps
        for i in range(3):
            section = ReportSection(
                title=f"Task {i+1}",
                content=f"<p>Task {i+1} completed</p>",
                data={"timestamp": datetime.now().isoformat(), "duration": 30 + i*10}
            )
            report.sections.append(section)
        
        chart_data = generator.create_timeline_chart(report)
        
        assert "data" in chart_data
        assert len(chart_data["data"]) == 1
        trace = chart_data["data"][0]
        assert trace["type"] == "scatter"
        assert "layout" in chart_data
    
    def test_render_markdown(self, sample_security_report):
        """Test Markdown rendering."""
        generator = ReportGenerator()
        markdown_content = generator.render_markdown(sample_security_report)
        
        assert "# Test Security Assessment" in markdown_content
        assert "test_workflow" in markdown_content
        assert "## Executive Summary" in markdown_content
        assert "## Detailed Results" in markdown_content
        assert "### Test Vulnerability" in markdown_content
        assert "Total Vulnerabilities" in markdown_content
    
    def test_render_markdown_no_summary(self):
        """Test Markdown rendering without summary."""
        report = SecurityReport(
            title="No Summary Report",
            workflow_name="test",
            execution_time=datetime.now(),
            duration=30.0,
            status="completed"
        )
        
        generator = ReportGenerator()
        markdown_content = generator.render_markdown(report)
        
        assert "# No Summary Report" in markdown_content
        assert "## Detailed Results" in markdown_content
    
    @patch('sentinelx.reporting.Environment')
    def test_render_html(self, mock_env, sample_security_report):
        """Test HTML rendering."""
        # Mock Jinja2 environment and template
        mock_template = Mock()
        mock_template.render.return_value = "<html><body>Test Report</body></html>"
        mock_env_instance = Mock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env.return_value = mock_env_instance
        
        generator = ReportGenerator()
        html_content = generator.render_html(sample_security_report)
        
        assert html_content == "<html><body>Test Report</body></html>"
        mock_template.render.assert_called_once_with(report=sample_security_report)
    
    def test_export_json(self, sample_security_report):
        """Test JSON export."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            generator = ReportGenerator()
            generator.export_json(sample_security_report, tmp_path)
            
            assert tmp_path.exists()
            with open(tmp_path, 'r') as f:
                data = json.load(f)
            
            assert data["title"] == "Test Security Assessment"
            assert data["workflow_name"] == "test_workflow"
            assert data["status"] == "completed"
            assert len(data["sections"]) == 1
            assert data["sections"][0]["title"] == "Test Vulnerability"
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    @patch('sentinelx.reporting.HTML')
    def test_export_pdf(self, mock_html_class, sample_security_report):
        """Test PDF export."""
        # Mock weasyprint HTML class
        mock_html_instance = Mock()
        mock_html_class.return_value = mock_html_instance
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            generator = ReportGenerator()
            
            # Mock the render_html method
            with patch.object(generator, 'render_html', return_value="<html>test</html>"):
                generator.export_pdf(sample_security_report, tmp_path)
            
            mock_html_class.assert_called_once()
            mock_html_instance.write_pdf.assert_called_once()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_export_report_html(self, sample_security_report):
        """Test HTML report export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            generator = ReportGenerator()
            
            # Mock HTML rendering
            with patch.object(generator, 'render_html', return_value="<html>test</html>"):
                generator.export_report(sample_security_report, output_path, "html")
            
            html_file = output_path.with_suffix('.html')
            assert html_file.exists()
            content = html_file.read_text()
            assert content == "<html>test</html>"
    
    def test_export_report_markdown(self, sample_security_report):
        """Test Markdown report export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            generator = ReportGenerator()
            generator.export_report(sample_security_report, output_path, "markdown")
            
            md_file = output_path.with_suffix('.md')
            assert md_file.exists()
            content = md_file.read_text()
            assert "# Test Security Assessment" in content
    
    def test_export_report_json(self, sample_security_report):
        """Test JSON report export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            generator = ReportGenerator()
            generator.export_report(sample_security_report, output_path, "json")
            
            json_file = output_path.with_suffix('.json')
            assert json_file.exists()
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            assert data["title"] == "Test Security Assessment"
    
    @patch('sentinelx.reporting.HTML')
    def test_export_report_pdf(self, mock_html_class, sample_security_report):
        """Test PDF report export."""
        mock_html_instance = Mock()
        mock_html_class.return_value = mock_html_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            generator = ReportGenerator()
            
            with patch.object(generator, 'render_html', return_value="<html>test</html>"):
                generator.export_report(sample_security_report, output_path, "pdf")
            
            mock_html_instance.write_pdf.assert_called_once()
    
    def test_export_report_unsupported_format(self, sample_security_report):
        """Test export with unsupported format."""
        generator = ReportGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            with pytest.raises(ValueError, match="Unsupported format: xml"):
                generator.export_report(sample_security_report, output_path, "xml")

class TestReportingEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_report(self):
        """Test handling of empty report."""
        report = SecurityReport(
            title="Empty Report",
            workflow_name="empty",
            execution_time=datetime.now(),
            duration=0.0,
            status="completed"
        )
        
        generator = ReportGenerator()
        summary = generator.generate_summary(report)
        
        assert summary["total_sections"] == 0
        assert summary["severity_counts"] == {}
    
    def test_report_with_none_values(self):
        """Test report handling with None values."""
        report = SecurityReport(
            title="Report with Nones",
            workflow_name="test",
            execution_time=None,
            duration=0.0,
            status="unknown"
        )
        
        section = ReportSection(
            title="Section with None",
            content="Test content",
            data={"value": None},
            chart_data=None
        )
        report.sections.append(section)
        
        generator = ReportGenerator()
        markdown_content = generator.render_markdown(report)
        
        assert "Report with Nones" in markdown_content
        assert "Section with None" in markdown_content
    
    def test_invalid_chart_data(self):
        """Test handling of invalid chart data."""
        generator = ReportGenerator()
        
        # Test with invalid severity counts
        invalid_counts = {"unknown_severity": 5}
        chart_data = generator.create_vulnerability_chart(invalid_counts)
        
        # Should still create valid chart structure
        assert "data" in chart_data
        assert "layout" in chart_data
    
    def test_large_report_handling(self):
        """Test handling of reports with many sections."""
        report = SecurityReport(
            title="Large Report",
            workflow_name="large_test",
            execution_time=datetime.now(),
            duration=300.0,
            status="completed"
        )
        
        # Add many sections
        for i in range(100):
            section = ReportSection(
                title=f"Section {i}",
                content=f"<p>Content for section {i}</p>",
                data={"index": i},
                severity="info" if i % 2 == 0 else "low"
            )
            report.sections.append(section)
        
        generator = ReportGenerator()
        summary = generator.generate_summary(report)
        
        assert summary["total_sections"] == 100
        assert summary["severity_counts"]["info"] == 50
        assert summary["severity_counts"]["low"] == 50

class TestReportingIntegration:
    """Integration tests for reporting functionality."""
    
    @pytest.mark.integration
    def test_full_report_workflow(self):
        """Test complete report generation workflow."""
        # Create a comprehensive report
        report = SecurityReport(
            title="Integration Test Report",
            workflow_name="integration_test",
            execution_time=datetime.now(),
            duration=180.5,
            status="completed"
        )
        
        # Add various sections
        severities = ["critical", "high", "medium", "low"]
        for i, severity in enumerate(severities):
            section = ReportSection(
                title=f"{severity.title()} Finding {i+1}",
                content=f"<p>This is a {severity} severity finding with detailed information.</p>",
                data={
                    "cvss_score": 9.0 - (i * 2),
                    "affected_components": [f"component_{i}", f"module_{i}"],
                    "remediation": f"Fix {severity} issue by updating component_{i}"
                },
                severity=severity
            )
            report.sections.append(section)
        
        report.summary = {
            "total_vulnerabilities": len(severities),
            "critical_issues": 1,
            "high_issues": 1,
            "medium_issues": 1,
            "low_issues": 1,
            "scan_coverage": "95%",
            "time_to_complete": "3 minutes"
        }
        
        generator = ReportGenerator()
        
        # Test all export formats
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "integration_report"
            
            # Export as JSON
            generator.export_report(report, base_path, "json")
            json_file = base_path.with_suffix('.json')
            assert json_file.exists()
            
            # Export as Markdown
            generator.export_report(report, base_path, "markdown")
            md_file = base_path.with_suffix('.md')
            assert md_file.exists()
            
            # Verify content
            json_content = json.loads(json_file.read_text())
            md_content = md_file.read_text()
            
            assert json_content["title"] == "Integration Test Report"
            assert len(json_content["sections"]) == 4
            assert "Integration Test Report" in md_content
            assert "Critical Finding 1" in md_content
