# SentinelX Social Engineering Toolkit Documentation

## Overview

The SentinelX Social Engineering Toolkit provides comprehensive capabilities for testing human security controls through simulated social engineering campaigns. This toolkit is designed for authorized security testing, penetration testing, and security awareness training.

## ⚠️ Legal and Ethical Notice

**FOR AUTHORIZED SECURITY TESTING AND AWARENESS TRAINING ONLY**

This toolkit must only be used for:
- Authorized penetration testing with explicit written permission
- Internal security awareness training programs  
- Red team exercises within your organization
- Educational purposes in controlled environments

Unauthorized use may violate local, state, and federal laws. Always obtain proper authorization before conducting any social engineering tests.

## Campaign Types

### 1. Phishing Campaigns
Traditional email-based social engineering attacks.

**Parameters:**
- `campaign_type`: "phishing"
- `template`: "generic", "business", "tech_support", "finance", "covid", "seasonal", "mixed"
- `target_info`: Employee and organization details
- `industry`: Target industry for context

**Features:**
- Multiple email templates for different scenarios
- Landing page configurations for credential harvesting
- Success metrics and tracking
- Industry-specific customization

### 2. Spear Phishing
Highly targeted, personalized phishing attacks against specific individuals.

**Parameters:**
- `campaign_type`: "spear_phishing"
- `target_info`: Detailed employee information
- `industry`: Industry context

**Features:**
- Personalized email content based on target analysis
- OSINT intelligence integration
- High-value target identification
- Custom attack vectors per target

### 3. Pretexting
Phone-based social engineering using fabricated scenarios.

**Parameters:**
- `campaign_type`: "pretexting"
- `target_info`: Organization details

**Scenarios:**
- IT Support Emergency
- Vendor Verification
- Executive Assistant
- Customer Service
- Survey/Research

### 4. Vishing (Voice Phishing)
Voice-based social engineering attacks via phone calls.

**Parameters:**
- `campaign_type`: "vishing"
- `target_info`: Organization and employee details

**Scenarios:**
- Bank Security Alerts
- Tech Support Scams
- Prize/Survey Notifications
- Government Agency Impersonation

### 5. Smishing (SMS Phishing)
Text message-based social engineering attacks.

**Parameters:**
- `campaign_type`: "smishing"
- `target_info`: Target information

**Templates:**
- Security Alerts
- Package Delivery Issues
- Financial Account Warnings
- Service Notifications

### 6. Baiting
Physical and digital bait attacks to entice target actions.

**Parameters:**
- `campaign_type`: "baiting"
- `target_info`: Environment details

**Types:**
- USB drop attacks
- Malicious charging stations
- Free software/documents
- Physical media distribution

### 7. Tailgating/Piggybacking
Physical security bypass through social manipulation.

**Parameters:**
- `campaign_type`: "tailgating"
- `target_info`: Physical location details

**Scenarios:**
- Delivery Person
- New Employee
- Maintenance Worker
- Vendor/Contractor

### 8. OSINT Intelligence Gathering
Comprehensive open source intelligence collection simulation.

**Parameters:**
- `campaign_type`: "osint"
- `target_info`: Organization details

**Intelligence Types:**
- Passive reconnaissance
- Social media intelligence
- Technical intelligence
- Human intelligence sources

### 9. Security Awareness Training
Interactive training content and simulated attacks.

**Parameters:**
- `campaign_type`: "awareness"
- `target_info`: Organization details
- `industry`: Training context

**Modules:**
- Email Security
- Social Engineering Awareness
- Physical Security
- Incident Response

### 10. Comprehensive Testing
Full-spectrum social engineering assessment.

**Parameters:**
- `campaign_type`: "comprehensive"
- All other parameters as needed

**Includes:**
- All campaign types
- Multi-vector testing
- Comprehensive reporting
- Detailed recommendations

## Usage Examples

### Basic Phishing Campaign
```python
from sentinelx.redteam.social_eng import SocialEngineering

# Create task
task = SocialEngineering(
    name="phishing_test",
    params={
        "campaign_type": "phishing",
        "template": "business",
        "industry": "technology",
        "target_info": {
            "company": "TechCorp Inc",
            "domain": "techcorp.com",
            "employees": [
                {"name": "John Doe", "email": "john.doe@techcorp.com", "position": "Manager"},
                {"name": "Jane Smith", "email": "jane.smith@techcorp.com", "position": "Developer"}
            ]
        }
    }
)

# Run campaign
results = await task.run()
```

### Spear Phishing Campaign
```python
task = SocialEngineering(
    name="spear_phishing_executives",
    params={
        "campaign_type": "spear_phishing", 
        "industry": "finance",
        "target_info": {
            "company": "SecureBank",
            "employees": [
                {
                    "name": "Alice Johnson",
                    "position": "CEO",
                    "email": "alice.johnson@securebank.com",
                    "interests": ["fintech", "leadership"],
                    "recent_activity": ["Speaking at FinTech Summit 2024"]
                }
            ]
        }
    }
)
```

### Comprehensive Assessment
```python
task = SocialEngineering(
    name="full_assessment",
    params={
        "campaign_type": "comprehensive",
        "template": "mixed",
        "industry": "healthcare",
        "include_osint": True,
        "target_info": {
            "company": "HealthCare Solutions",
            "domain": "healthcaresolutions.com",
            "size": "medium",
            "location": "New York",
            "employees": [...],  # Detailed employee list
            "technology": {
                "email": "Office 365",
                "os": ["Windows 10", "macOS"],
                "security": ["Defender", "Firewall"]
            }
        }
    }
)
```

## Target Information Structure

### Organization Details
```python
target_info = {
    "company": "Company Name",
    "domain": "company.com", 
    "website": "https://www.company.com",
    "industry": "technology",
    "size": "large",  # small, medium, large
    "location": "City, State",
    "revenue": "$100M+",
}
```

### Employee Information
```python
employees = [
    {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "position": "Senior Manager",
        "department": "IT",
        "phone": "+1-555-123-4567",
        "interests": ["cybersecurity", "golf"],
        "social_media": {
            "linkedin": "linkedin.com/in/johndoe",
            "twitter": "@johndoe"
        },
        "recent_activity": ["Posted about new project on LinkedIn"],
        "connections": ["Industry peers", "Former colleagues"]
    }
]
```

### Technology Stack
```python
technology = {
    "email": "Office 365",
    "os": ["Windows 10", "Windows 11", "macOS"],
    "security": ["Windows Defender", "CrowdStrike", "Proofpoint"],
    "cloud": ["Microsoft 365", "AWS", "Salesforce"],
    "collaboration": ["Teams", "Slack", "Zoom"]
}
```

## Output Structure

### Campaign Results
```python
results = {
    "campaign_type": "phishing",
    "timestamp": "2024-01-15T10:30:00",
    "target_analysis": {
        "organization_profile": {...},
        "employee_analysis": {...},
        "vulnerability_assessment": {...}
    },
    "campaigns": {
        "phishing": {
            "email_templates": [...],
            "landing_pages": [...],
            "success_indicators": [...]
        }
    },
    "osint_intelligence": {...},
    "success_metrics": {
        "primary_metrics": {...},
        "secondary_metrics": {...}
    },
    "countermeasures": {
        "technical_controls": [...],
        "procedural_controls": [...],
        "awareness_measures": [...]
    },
    "security_recommendations": {
        "immediate_actions": [...],
        "short_term_improvements": [...],
        "long_term_strategy": [...]
    }
}
```

## Success Metrics

### Phishing/Spear Phishing Metrics
- **Click Rate**: Percentage of users who clicked malicious links
- **Credential Submission**: Percentage who entered credentials  
- **Attachment Opening**: Percentage who opened malicious attachments
- **Reporting Rate**: Percentage who reported suspicious email

### Vishing/Smishing Metrics
- **Response Rate**: Percentage who responded to calls/SMS
- **Information Disclosure**: Percentage who shared sensitive info
- **Callback Rate**: Percentage who called back suspicious numbers
- **Verification Attempts**: Percentage who tried to verify caller

### Physical Security Metrics
- **Success Rate**: Percentage of successful attempts
- **Information Gathered**: Type and amount of info obtained
- **Access Gained**: Level of physical/system access achieved
- **Detection Rate**: Percentage of attempts that were detected

## Countermeasures and Defenses

### Technical Controls
- Email security gateways with advanced threat protection
- Multi-factor authentication for all accounts
- Endpoint detection and response (EDR) solutions
- Web filtering and URL reputation checking
- Network segmentation and zero-trust architecture

### Procedural Controls
- Incident response procedures for social engineering
- Verification protocols for sensitive requests
- Visitor management and escort procedures
- Information classification and handling policies
- Regular security awareness training programs

### Awareness Measures
- Regular communication about current threats
- Recognition and reward programs for reporting
- Leadership engagement in security culture
- Department-specific training based on risk
- Scenario-based training exercises

## Best Practices

### Planning Phase
1. **Obtain Written Authorization**: Always get explicit permission
2. **Define Scope**: Clear boundaries and limitations
3. **Set Objectives**: Specific, measurable goals
4. **Risk Assessment**: Identify potential impacts
5. **Communication Plan**: Stakeholder notification strategy

### Execution Phase
1. **Start Small**: Begin with low-risk scenarios
2. **Monitor Closely**: Track responses and escalations
3. **Document Everything**: Detailed logs and evidence
4. **Be Prepared**: Have incident response ready
5. **Respect Boundaries**: Stay within authorized scope

### Reporting Phase
1. **Comprehensive Analysis**: Detailed findings and metrics
2. **Risk Prioritization**: Focus on high-impact vulnerabilities
3. **Actionable Recommendations**: Practical next steps
4. **Executive Summary**: High-level business impact
5. **Training Integration**: Link to awareness programs

## Integration with Other SentinelX Modules

### OSINT Integration
- Leverage `threatmodel` module for target analysis
- Use `audit` capabilities for technical reconnaissance
- Integrate with `ai` module for content generation

### Forensic Analysis
- Use `forensic` module to analyze attack artifacts
- Chain analysis for advanced persistent simulations
- Memory analysis of compromised systems

### Exploit Integration
- Combine with `exploit` module for technical attacks
- Multi-stage attack simulation capabilities
- Payload delivery through social engineering

## Advanced Features

### AI-Powered Content Generation
The toolkit can leverage the SentinelX AI module for:
- Dynamic email content generation
- Persona development for pretexting
- Real-time conversation adaptation
- Behavioral analysis and adaptation

### OSINT Automation
- Automated target reconnaissance
- Social media profile analysis
- Public information gathering
- Threat intelligence integration

### Campaign Management
- Multi-phase campaign orchestration
- Timing and scheduling optimization
- Success rate tracking and analysis
- Adaptive campaign modification

## Security Considerations

### Data Protection
- Minimize collection of personal information
- Secure storage of test results
- Regular data purging procedures
- Encryption of sensitive test data

### Operational Security
- Controlled testing environments
- Limited access to testing tools
- Audit trails for all activities
- Incident response procedures

### Legal Compliance
- Regular review of legal requirements
- Documentation of authorization
- Compliance with privacy regulations
- Industry-specific considerations

## Training and Certification

### Recommended Training
- Social engineering fundamentals
- Legal and ethical considerations
- Technical tool proficiency
- Incident response procedures

### Certification Programs
- Certified Ethical Hacker (CEH)
- GIAC Social Engineering Penetration Tester (GPEN)
- Offensive Security Certified Professional (OSCP)
- Social Engineering Framework certification

## Troubleshooting

### Common Issues
1. **Low Response Rates**: Improve personalization and timing
2. **High Detection Rates**: Adjust sophistication and frequency
3. **Technical Failures**: Check infrastructure and tools
4. **Legal Concerns**: Review authorization and scope

### Performance Optimization
- A/B testing of different approaches
- Timing optimization based on target behavior
- Template effectiveness analysis
- Continuous improvement based on metrics

## Future Enhancements

### Planned Features
- Machine learning-powered personalization
- Real-time campaign adaptation
- Advanced behavioral analytics
- Integration with threat intelligence feeds

### Community Contributions
- Template sharing and collaboration
- Best practice documentation
- Case study contributions
- Tool enhancement suggestions

---

*This documentation is part of the SentinelX Security Framework. For updates and additional resources, visit the project repository.*
