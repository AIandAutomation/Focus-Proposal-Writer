"""
Industry Analysis Agent Module
------------------------------
This module provides the IndustryAnalysisAgent class, which performs detailed analysis of
client documents to identify the industry context and generate industry-specific insights,
recommendations, and talking points that can enhance proposal credibility and relevance.
"""

import re
import logging
from collections import Counter

class IndustryAnalysisAgent:
    def __init__(self):
        """
        Initialize the IndustryAnalysisAgent with comprehensive industry insights and talking points.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)
            
        # Expanded industry dictionary with more sectors and detailed insights
        self.industry_data = {
            "healthcare": {
                "keywords": [
                    "healthcare", "hospital", "medical", "clinic", "patient", "physician", 
                    "ehr", "electronic health record", "hipaa", "health insurance", "medicare",
                    "medicaid", "telehealth", "telemedicine", "pharmaceutical", "clinical"
                ],
                "talking_points": [
                    "Ensuring HIPAA compliance and patient data security is paramount to any healthcare solution.",
                    "Modern healthcare organizations require seamless integration between clinical and administrative systems.",
                    "Healthcare providers are seeking technology that reduces administrative burden while improving patient outcomes.",
                    "Solutions that enhance patient engagement while maintaining privacy are highly valued in healthcare.",
                    "Interoperability with existing Electronic Health Record (EHR) systems is a critical requirement.",
                    "Telehealth capabilities have become essential in modern healthcare delivery models."
                ],
                "compliance_notes": "HIPAA, HITECH Act, FDA regulations for medical devices, state-specific healthcare regulations"
            },
            
            "finance": {
                "keywords": [
                    "finance", "bank", "investment", "insurance", "financial", "credit", 
                    "lending", "mortgage", "wealth management", "asset", "portfolio", 
                    "fintech", "payment", "transaction", "regulatory compliance", "trading"
                ],
                "talking_points": [
                    "Financial institutions require robust security measures that meet regulatory standards while enabling business agility.",
                    "Solutions must address the challenge of legacy system integration without disrupting critical financial operations.",
                    "Advanced analytics capabilities can help financial organizations leverage their data for competitive advantage.",
                    "Regulatory compliance including AML, KYC, and fraud detection should be built into any financial technology solution.",
                    "Real-time processing and high availability are non-negotiable for financial transaction systems.",
                    "Financial institutions are increasingly focused on improving customer experience through digital transformation."
                ],
                "compliance_notes": "SEC regulations, Gramm-Leach-Bliley Act, Dodd-Frank, PCI DSS, Basel frameworks"
            },
            
            "government": {
                "keywords": [
                    "government", "federal", "agency", "public sector", "state", "municipal", 
                    "department", "regulation", "compliance", "procurement", "civilian", 
                    "defense", "military", "public safety", "public works", "citizen service"
                ],
                "talking_points": [
                    "Government solutions must prioritize security, compliance, and accessibility requirements.",
                    "Demonstrating adherence to FedRAMP, FISMA, and other government security standards is essential.",
                    "Procurement processes in government require detailed documentation and compliance with specific contracting vehicles.",
                    "Government agencies often require solutions that can be customized to their unique workflows while maintaining security.",
                    "Solutions for government should emphasize long-term value, sustainability, and cost-effectiveness.",
                    "Citizen-facing systems must be designed for maximum accessibility and inclusiveness."
                ],
                "compliance_notes": "FISMA, FedRAMP, Section 508 accessibility, NIST frameworks, CMMC"
            },
            
            "education": {
                "keywords": [
                    "education", "school", "university", "college", "student", "campus", 
                    "learning", "academic", "faculty", "classroom", "curriculum", 
                    "e-learning", "lms", "learning management", "distance learning", "teacher"
                ],
                "talking_points": [
                    "Educational institutions need scalable solutions that support both in-person and remote learning environments.",
                    "Integration with existing Learning Management Systems (LMS) is typically a key requirement.",
                    "Solutions should be designed to enhance educational outcomes while simplifying administrative processes.",
                    "Student data privacy and FERPA compliance must be prioritized in educational technology solutions.",
                    "Accessibility features are essential to ensure equal access to educational resources.",
                    "Technology should enable data-driven decision making while protecting sensitive student information."
                ],
                "compliance_notes": "FERPA, COPPA (for K-12), state education privacy laws, accessibility requirements"
            },
            
            "retail": {
                "keywords": [
                    "retail", "store", "e-commerce", "merchandise", "inventory", "pos", 
                    "point of sale", "consumer", "shopping", "omnichannel", "supply chain", 
                    "logistics", "fulfillment", "customer experience", "loyalty", "pricing"
                ],
                "talking_points": [
                    "Modern retail requires seamless integration between online and offline channels for true omnichannel experiences.",
                    "Inventory management systems must provide real-time visibility across all sales channels and warehouses.",
                    "Customer data platforms that unify shopper information can drive personalization and increase loyalty.",
                    "Payment systems must be secure, flexible, and support diverse payment methods including mobile and contactless options.",
                    "Supply chain visibility and agility have become critical success factors for retailers.",
                    "Solutions should help retailers leverage data to optimize pricing, promotions, and inventory decisions."
                ],
                "compliance_notes": "PCI DSS, consumer protection regulations, ADA accessibility for e-commerce"
            },
            
            "manufacturing": {
                "keywords": [
                    "manufacturing", "factory", "production", "industrial", "supply chain", 
                    "inventory", "quality control", "assembly", "fabrication", "equipment", 
                    "maintenance", "iot", "sensors", "automation", "warehouse", "logistics"
                ],
                "talking_points": [
                    "Modern manufacturing operations require real-time visibility into production processes and supply chains.",
                    "IoT and sensor integration enable predictive maintenance and reduction in equipment downtime.",
                    "Solutions should help manufacturers improve quality control while optimizing production efficiency.",
                    "Supply chain resilience and visibility have become critical concerns for manufacturing operations.",
                    "Data integration across systems can provide valuable insights for continuous improvement initiatives.",
                    "Technology solutions should demonstrate clear ROI through operational efficiency and reduced downtime."
                ],
                "compliance_notes": "ISO standards, industry-specific quality standards, safety regulations, environmental compliance"
            },
            
            "technology": {
                "keywords": [
                    "technology", "software", "hardware", "it", "cloud", "saas", 
                    "digital transformation", "artificial intelligence", "machine learning", 
                    "development", "cybersecurity", "data center", "platform", "api", "integration"
                ],
                "talking_points": [
                    "Technology companies need solutions that can scale rapidly while maintaining security and compliance.",
                    "API-first architecture and strong integration capabilities are typically essential requirements.",
                    "Development and deployment automation can significantly improve time-to-market for technology products.",
                    "Robust security measures and compliance frameworks are critical for technology service providers.",
                    "Solutions should enable data-driven decision making while respecting privacy concerns.",
                    "Modern technology operations require tools that support both cloud-native and hybrid infrastructure."
                ],
                "compliance_notes": "Various framework compliance depending on sector served (HIPAA, PCI, SOC2, ISO 27001, GDPR)"
            }
        }

    def analyze_industry(self, extracted_text):
        """
        Analyze the extracted text to identify the client's industry and generate relevant insights.
        The method uses keyword frequency analysis to determine the most likely industry context
        and then returns tailored talking points and recommendations.
        
        :param extracted_text: str - The text extracted from client documents.
        :return: str - A detailed industry analysis with targeted talking points and recommendations.
        """
        if not extracted_text or not isinstance(extracted_text, str):
            self.logger.warning("Empty or invalid text provided for industry analysis.")
            return "Insufficient information to perform industry analysis."
            
        text_lower = extracted_text.lower()
        
        # Count keyword occurrences for each industry
        industry_scores = {}
        for industry, data in self.industry_data.items():
            industry_scores[industry] = 0
            for keyword in data["keywords"]:
                # Use regex to find whole word matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                industry_scores[industry] += len(matches)
        
        # Find the industry with the highest score
        if not industry_scores or max(industry_scores.values()) == 0:
            self.logger.info("No clear industry detected in the text.")
            return self._generate_general_analysis()
            
        # Get the top 2 industries (primary and secondary if available)
        sorted_industries = sorted(industry_scores.items(), key=lambda x: x[1], reverse=True)
        primary_industry = sorted_industries[0][0]
        
        # If there's a close secondary industry, include it in the analysis
        secondary_industry = None
        if len(sorted_industries) > 1 and sorted_industries[1][1] > 0:
            if sorted_industries[0][1] / max(1, sorted_industries[1][1]) < 2:  # If secondary is at least half as relevant
                secondary_industry = sorted_industries[1][0]
        
        return self._generate_industry_specific_analysis(primary_industry, secondary_industry)
    
    def _generate_industry_specific_analysis(self, primary_industry, secondary_industry=None):
        """
        Generate a detailed industry-specific analysis based on the detected industry.
        
        :param primary_industry: str - The main detected industry.
        :param secondary_industry: str - Optional secondary industry if relevant.
        :return: str - Formatted industry analysis.
        """
        primary_data = self.industry_data[primary_industry]
        
        # Select 3-4 most relevant talking points for primary industry
        primary_points = primary_data["talking_points"][:4]
        
        # Build the analysis
        analysis = f"## {primary_industry.capitalize()} Industry Analysis\n\n"
        analysis += "### Key Industry Insights\n"
        for point in primary_points:
            analysis += f"- {point}\n"
            
        analysis += f"\n### Compliance Considerations\n{primary_data['compliance_notes']}\n"
        
        # Add secondary industry insights if applicable
        if secondary_industry:
            secondary_data = self.industry_data[secondary_industry]
            analysis += f"\n### Additional {secondary_industry.capitalize()} Sector Considerations\n"
            # Include 2 talking points from secondary industry
            for point in secondary_data["talking_points"][:2]:
                analysis += f"- {point}\n"
        
        analysis += "\n### Recommendation for Proposal\n"
        analysis += f"This proposal should emphasize solutions specifically designed for the {primary_industry} "
        analysis += "sector, highlighting expertise in addressing the unique challenges and requirements of this industry. "
        if secondary_industry:
            analysis += f"Also consider including elements relevant to the {secondary_industry} sector where appropriate."
        
        return analysis
    
    def _generate_general_analysis(self):
        """
        Generate a general analysis when no specific industry is clearly detected.
        
        :return: str - General industry analysis.
        """
        general_analysis = """
## General Industry Analysis

No specific industry was clearly identified in the provided documents. Consider focusing on these universal business values in your proposal:

### Key Business Priorities
- Operational efficiency and cost optimization
- Security and risk management
- Digital transformation and modernization
- Data-driven decision making
- Customer experience enhancement
- Business continuity and resilience

### Recommendation for Proposal
Without a clear industry focus, emphasize adaptability of your solution to various business contexts and how it addresses fundamental business needs like efficiency, security, and ROI. Consider asking the client for additional information about their industry-specific requirements.
"""
        return general_analysis
