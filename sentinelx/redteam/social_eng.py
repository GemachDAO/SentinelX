from __future__ import annotations
import asyncio
import json
import random
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.task import Task

class SocialEngineering(Task):
    """Social engineering campaign generation and simulation"""
    
    async def run(self):
        """Generate social engineering campaigns and analysis"""
        campaign_type = self.params.get("campaign_type", "phishing")  # phishing, pretexting, spear_phishing, awareness
        target_info = self.params.get("target_info", {})
        template_type = self.params.get("template", "generic")
        analysis_only = self.params.get("analysis_only", True)  # Don't actually send emails
        
        try:
            results = {
                "campaign_type": campaign_type,
                "timestamp": datetime.now().isoformat(),
                "target_analysis": {},
                "generated_content": {},
                "delivery_vectors": [],
                "success_metrics": {}
            }
            
            if campaign_type == "phishing":
                phishing_campaign = await self._generate_phishing_campaign(target_info, template_type)
                results["phishing_campaign"] = phishing_campaign
                
            elif campaign_type == "spear_phishing":
                spear_campaign = await self._generate_spear_phishing(target_info, template_type)
                results["spear_phishing_campaign"] = spear_campaign
                
            elif campaign_type == "pretexting":
                pretext_campaign = await self._generate_pretexting_campaign(target_info)
                results["pretexting_campaign"] = pretext_campaign
                
            elif campaign_type == "awareness":
                awareness_test = await self._generate_awareness_test(target_info)
                results["awareness_test"] = awareness_test
                
            elif campaign_type == "comprehensive":
                results["phishing_campaign"] = await self._generate_phishing_campaign(target_info, template_type)
                results["spear_phishing_campaign"] = await self._generate_spear_phishing(target_info, template_type)
                results["pretexting_campaign"] = await self._generate_pretexting_campaign(target_info)
                results["awareness_test"] = await self._generate_awareness_test(target_info)
                
            # Add general social engineering analysis
            results["social_eng_analysis"] = await self._analyze_social_engineering_risks(target_info)
            
            # Add disclaimer
            results["disclaimer"] = "This tool is for authorized security testing and awareness training only"
            
            return results
            
        except Exception as e:
            return {"error": f"Social engineering campaign generation failed: {str(e)}"}
            
    async def _generate_phishing_campaign(self, target_info: Dict[str, Any], template: str) -> Dict[str, Any]:
        """Generate phishing email campaign"""
        campaign = {
            "template_type": template,
            "email_templates": [],
            "landing_pages": [],
            "delivery_methods": [],
            "tracking_metrics": []
        }
        
        # Email templates based on type
        if template == "generic":
            templates = await self._get_generic_phishing_templates()
        elif template == "business":
            templates = await self._get_business_phishing_templates()
        elif template == "tech_support":
            templates = await self._get_tech_support_templates()
        elif template == "finance":
            templates = await self._get_finance_phishing_templates()
        else:
            templates = await self._get_generic_phishing_templates()
            
        campaign["email_templates"] = templates
        
        # Generate landing page suggestions
        campaign["landing_pages"] = [
            {
                "type": "credential_harvest",
                "description": "Fake login page to capture credentials",
                "url_pattern": "https://secure-login-verify.com/auth"
            },
            {
                "type": "malware_download",
                "description": "Fake software update or document download",
                "url_pattern": "https://updates-center.com/download"
            },
            {
                "type": "survey_scam",
                "description": "Fake survey to collect personal information",
                "url_pattern": "https://customer-feedback-rewards.com/survey"
            }
        ]
        
        # Delivery methods
        campaign["delivery_methods"] = [
            "Direct email",
            "Spoofed sender address",
            "Compromised email account",
            "Social media messaging",
            "SMS phishing (smishing)"
        ]
        
        # Tracking metrics for awareness testing
        campaign["tracking_metrics"] = [
            "Email open rate",
            "Link click rate", 
            "Credential submission rate",
            "Malware download rate",
            "User reporting rate"
        ]
        
        return campaign
        
    async def _generate_spear_phishing(self, target_info: Dict[str, Any], template: str) -> Dict[str, Any]:
        """Generate targeted spear phishing campaign"""
        campaign = {
            "target_analysis": {},
            "personalized_content": {},
            "attack_vectors": [],
            "social_media_intel": {}
        }
        
        # Analyze target information
        if target_info:
            campaign["target_analysis"] = {
                "name": target_info.get("name", "Unknown"),
                "title": target_info.get("title", "Unknown"),
                "company": target_info.get("company", "Unknown"),
                "email": target_info.get("email", "Unknown"),
                "interests": target_info.get("interests", []),
                "recent_activities": target_info.get("recent_activities", [])
            }
            
            # Generate personalized content
            campaign["personalized_content"] = await self._create_personalized_content(target_info)
            
        # Common spear phishing vectors
        campaign["attack_vectors"] = [
            {
                "vector": "Business Email Compromise",
                "description": "Impersonate CEO/executive requesting urgent action",
                "effectiveness": "High"
            },
            {
                "vector": "Vendor Impersonation",
                "description": "Impersonate known vendor/supplier",
                "effectiveness": "Medium-High"
            },
            {
                "vector": "Conference/Event Phishing",
                "description": "Use recent conference attendance for context",
                "effectiveness": "Medium"
            },
            {
                "vector": "LinkedIn Connection Abuse",
                "description": "Reference mutual connections or recent posts",
                "effectiveness": "Medium"
            }
        ]
        
        # Social media intelligence gathering
        campaign["social_media_intel"] = {
            "linkedin_data": "Professional background and connections",
            "twitter_data": "Recent tweets and interests",
            "facebook_data": "Personal interests and activities",
            "instagram_data": "Photos and location data",
            "privacy_score": "Medium - some information publicly available"
        }
        
        return campaign
        
    async def _generate_pretexting_campaign(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pretexting scenarios"""
        campaign = {
            "scenarios": [],
            "psychological_triggers": [],
            "information_gathering": {},
            "execution_phases": []
        }
        
        # Common pretexting scenarios
        campaign["scenarios"] = [
            {
                "scenario": "IT Support Impersonation",
                "description": "Impersonate IT support requesting password reset",
                "psychological_trigger": "Authority and urgency",
                "information_needed": "Employee ID, computer details",
                "success_rate": "Medium-High"
            },
            {
                "scenario": "HR Investigation",
                "description": "Claim to be from HR investigating policy violation",
                "psychological_trigger": "Fear and authority",
                "information_needed": "Employee handbook, manager details",
                "success_rate": "Medium"
            },
            {
                "scenario": "Vendor/Supplier Call",
                "description": "Pretend to be from known vendor needing account update",
                "psychological_trigger": "Familiarity and routine",
                "information_needed": "Vendor relationships, account details",
                "success_rate": "High"
            },
            {
                "scenario": "Emergency Contact",
                "description": "Claim family emergency requiring immediate assistance",
                "psychological_trigger": "Emotional manipulation",
                "information_needed": "Personal information, family details",
                "success_rate": "Medium"
            }
        ]
        
        # Psychological triggers
        campaign["psychological_triggers"] = [
            "Authority (impersonating authority figures)",
            "Urgency (creating time pressure)",
            "Fear (threatening consequences)",
            "Curiosity (offering exclusive information)",
            "Greed (promising rewards or benefits)",
            "Social proof (claiming others have complied)",
            "Reciprocity (doing a favor first)"
        ]
        
        # Information gathering techniques
        campaign["information_gathering"] = {
            "osint_sources": [
                "Company website and directory",
                "Social media profiles",
                "LinkedIn connections",
                "News articles and press releases",
                "Job postings and descriptions"
            ],
            "reconnaissance_techniques": [
                "Dumpster diving (physical)",
                "Social media stalking",
                "Website enumeration",
                "Employee directory harvesting",
                "Conference and event attendance"
            ]
        }
        
        # Execution phases
        campaign["execution_phases"] = [
            {
                "phase": "Information Gathering",
                "description": "Collect background information about target",
                "duration": "1-2 weeks"
            },
            {
                "phase": "Pretext Development",
                "description": "Create believable scenario and backstory",
                "duration": "2-3 days"
            },
            {
                "phase": "Initial Contact",
                "description": "Make first contact to establish rapport",
                "duration": "1 day"
            },
            {
                "phase": "Information Extraction",
                "description": "Extract sensitive information or gain access",
                "duration": "1-2 days"
            }
        ]
        
        return campaign
        
    async def _generate_awareness_test(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security awareness testing scenarios"""
        test = {
            "test_scenarios": [],
            "training_opportunities": [],
            "success_metrics": {},
            "remediation_plan": {}
        }
        
        # Awareness test scenarios
        test["test_scenarios"] = [
            {
                "test_type": "Phishing Email",
                "description": "Send simulated phishing email to test response",
                "expected_behavior": "Report email to security team",
                "pass_criteria": "Email reported within 24 hours"
            },
            {
                "test_type": "USB Drop",
                "description": "Drop USB drives in parking lot/common areas",
                "expected_behavior": "Turn in USB to security without plugging in",
                "pass_criteria": "USB turned in without insertion"
            },
            {
                "test_type": "Tailgating Test",
                "description": "Test physical access controls and tailgating awareness",
                "expected_behavior": "Challenge unknown individuals or request badge",
                "pass_criteria": "Proper challenge procedure followed"
            },
            {
                "test_type": "Social Engineering Call",
                "description": "Make pretexting call requesting sensitive information",
                "expected_behavior": "Verify caller identity and refuse to provide info",
                "pass_criteria": "Information not disclosed, incident reported"
            }
        ]
        
        # Training opportunities
        test["training_opportunities"] = [
            {
                "topic": "Email Security",
                "content": "Identifying phishing emails and safe email practices"
            },
            {
                "topic": "Social Engineering Awareness",
                "content": "Common social engineering tactics and red flags"
            },
            {
                "topic": "Physical Security",
                "content": "Tailgating, clean desk policy, device security"
            },
            {
                "topic": "Incident Reporting",
                "content": "How and when to report security incidents"
            }
        ]
        
        # Success metrics
        test["success_metrics"] = {
            "phishing_click_rate": "Target: <5%",
            "reporting_rate": "Target: >90%",
            "time_to_report": "Target: <2 hours",
            "repeat_offenders": "Target: <1%"
        }
        
        # Remediation plan
        test["remediation_plan"] = {
            "immediate_actions": [
                "Additional training for users who failed tests",
                "Review and update security policies",
                "Implement technical controls (email filtering, etc.)"
            ],
            "long_term_actions": [
                "Regular ongoing awareness training",
                "Simulated phishing campaigns",
                "Culture change initiatives"
            ]
        }
        
        return test
        
    async def _analyze_social_engineering_risks(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social engineering risks and vulnerabilities"""
        analysis = {
            "risk_factors": [],
            "vulnerability_assessment": {},
            "mitigation_strategies": [],
            "risk_score": 0
        }
        
        # Analyze risk factors
        risk_factors = []
        risk_score = 0
        
        if target_info.get("public_profile"):
            risk_factors.append("High public profile increases targeting likelihood")
            risk_score += 20
            
        if target_info.get("social_media_active"):
            risk_factors.append("Active social media presence provides reconnaissance data")
            risk_score += 15
            
        if target_info.get("executive_level"):
            risk_factors.append("Executive level position makes attractive target")
            risk_score += 25
            
        if target_info.get("access_level") == "high":
            risk_factors.append("High access level increases attack impact")
            risk_score += 20
            
        # Default risk factors
        if not risk_factors:
            risk_factors = [
                "All employees are potential social engineering targets",
                "Human element is often the weakest link in security",
                "Social engineering attacks are becoming more sophisticated"
            ]
            risk_score = 50
            
        analysis["risk_factors"] = risk_factors
        analysis["risk_score"] = min(risk_score, 100)
        
        # Vulnerability assessment
        analysis["vulnerability_assessment"] = {
            "human_factors": [
                "Lack of security awareness training",
                "Pressure to be helpful and responsive",
                "Trust in authority figures",
                "Desire to avoid confrontation"
            ],
            "organizational_factors": [
                "Lack of verification procedures",
                "Inadequate incident reporting processes",
                "Poor security culture",
                "Insufficient technical controls"
            ],
            "technical_factors": [
                "Weak email filtering",
                "Lack of multi-factor authentication",
                "Inadequate access controls",
                "Missing security monitoring"
            ]
        }
        
        # Mitigation strategies
        analysis["mitigation_strategies"] = [
            {
                "strategy": "Security Awareness Training",
                "description": "Regular training on social engineering tactics",
                "effectiveness": "High"
            },
            {
                "strategy": "Verification Procedures",
                "description": "Implement callback verification for sensitive requests",
                "effectiveness": "High"
            },
            {
                "strategy": "Technical Controls",
                "description": "Email filtering, web blocking, endpoint protection",
                "effectiveness": "Medium-High"
            },
            {
                "strategy": "Incident Response Plan",
                "description": "Clear procedures for reporting and responding to incidents",
                "effectiveness": "Medium"
            },
            {
                "strategy": "Simulated Phishing",
                "description": "Regular phishing simulations to test and train",
                "effectiveness": "High"
            }
        ]
        
        return analysis
        
    async def _get_generic_phishing_templates(self) -> List[Dict[str, str]]:
        """Get generic phishing email templates"""
        return [
            {
                "subject": "Urgent: Account Security Alert",
                "body": "Your account has been compromised. Click here to secure it immediately.",
                "sender": "security@company.com",
                "urgency": "High"
            },
            {
                "subject": "Action Required: Update Your Password",
                "body": "Your password will expire in 24 hours. Update now to avoid account lockout.",
                "sender": "it-support@company.com",
                "urgency": "Medium"
            },
            {
                "subject": "Invoice Payment Overdue",
                "body": "Your invoice payment is overdue. Please review the attached invoice.",
                "sender": "billing@vendor.com",
                "urgency": "Medium"
            }
        ]
        
    async def _get_business_phishing_templates(self) -> List[Dict[str, str]]:
        """Get business-focused phishing templates"""
        return [
            {
                "subject": "Quarterly Report - Confidential",
                "body": "Please review the attached quarterly report before tomorrow's meeting.",
                "sender": "ceo@company.com",
                "urgency": "High"
            },
            {
                "subject": "New HR Policy - Immediate Compliance Required",
                "body": "New HR policy requires immediate acknowledgment. Click to view.",
                "sender": "hr@company.com",
                "urgency": "High"
            }
        ]
        
    async def _get_tech_support_templates(self) -> List[Dict[str, str]]:
        """Get technical support phishing templates"""
        return [
            {
                "subject": "System Maintenance - Action Required",
                "body": "System maintenance requires password verification. Click to verify.",
                "sender": "techsupport@company.com",
                "urgency": "Medium"
            },
            {
                "subject": "Software Update Available",
                "body": "Critical software update available. Download now for security.",
                "sender": "updates@company.com",
                "urgency": "Medium"
            }
        ]
        
    async def _get_finance_phishing_templates(self) -> List[Dict[str, str]]:
        """Get finance-focused phishing templates"""
        return [
            {
                "subject": "Wire Transfer Approval Needed",
                "body": "Urgent wire transfer requires your approval. Click to review.",
                "sender": "finance@company.com",
                "urgency": "High"
            },
            {
                "subject": "Expense Report Submission Deadline",
                "body": "Expense report deadline is tomorrow. Submit now to avoid delay.",
                "sender": "accounting@company.com",
                "urgency": "Medium"
            }
        ]
        
    async def _create_personalized_content(self, target_info: Dict[str, Any]) -> Dict[str, str]:
        """Create personalized content based on target information"""
        content = {}
        
        name = target_info.get("name", "")
        company = target_info.get("company", "")
        title = target_info.get("title", "")
        interests = target_info.get("interests", [])
        
        if name:
            content["greeting"] = f"Dear {name},"
        else:
            content["greeting"] = "Dear Team Member,"
            
        if company:
            content["company_reference"] = f"As a valued {company} employee"
        else:
            content["company_reference"] = "As a valued team member"
            
        if title:
            content["title_reference"] = f"Given your role as {title}"
        else:
            content["title_reference"] = "Given your important role"
            
        if interests:
            content["interest_hook"] = f"We noticed your interest in {', '.join(interests[:2])}"
        else:
            content["interest_hook"] = "We have exclusive information that may interest you"
            
        return content
