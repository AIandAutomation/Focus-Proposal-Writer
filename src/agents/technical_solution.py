"""
Technical Solution Agent Module
---------------------------------
This module provides the TechnicalSolutionAgent class, which generates a draft for the 
"Technical Approach" section of a proposal by breaking the process into modular steps.
The agent uses advanced prompting techniques with chain-of-thought reasoning to produce
high-quality, context-aware technical solutions.
"""

import openai
import logging
import json

class TechnicalSolutionAgent:
    def __init__(self, openai_api_key):
        """
        Initialize the TechnicalSolutionAgent with the provided OpenAI API key.
        
        :param openai_api_key: str - Your OpenAI API key.
        """
        openai.api_key = openai_api_key
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)
        
        # Industry to technology stack mappings for more intelligent recommendations
        self.industry_tech_stack = {
            "healthcare": ["HIPAA-compliant cloud services", "Electronic Health Record (EHR) systems", "HL7 FHIR"],
            "finance": ["Blockchain", "RegTech solutions", "Secure payment gateways", "Anti-fraud ML systems"],
            "government": ["FedRAMP certified solutions", "GovCloud", "Zero-trust architecture"],
            "education": ["Learning Management Systems", "Virtual classrooms", "Student analytics platforms"],
            "retail": ["Inventory management systems", "POS integration", "Customer loyalty platforms"],
        }

    def _detect_industry(self, text):
        """
        Detect the client's industry from the provided text using keyword analysis.
        
        :param text: str - Text describing the client or requirements.
        :return: str - The detected industry or "general" if none detected.
        """
        industry_keywords = {
            "healthcare": ["health", "hospital", "patient", "medical", "clinic", "care provider"],
            "finance": ["bank", "finance", "investment", "trading", "payment", "insurance"],
            "government": ["government", "federal", "agency", "public sector", "state", "municipal"],
            "education": ["school", "university", "college", "education", "student", "learning"],
            "retail": ["retail", "store", "shop", "e-commerce", "product", "inventory", "sell"]
        }
        
        text_lower = text.lower()
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return "general"

    def generate_technical_solution(self, classification, extracted_text, tone_settings, project_requirements=""):
        """
        Generate a comprehensive technical approach section for a proposal.
        
        :param classification: str - The client classification ("government" or "enterprise").
        :param extracted_text: str - Text extracted from relevant documents.
        :param tone_settings: dict - Tone settings (e.g., tone, style).
        :param project_requirements: str - Specific project requirements or constraints.
        :return: str - The combined technical solution draft.
        """
        return self.generate_technical_solution_modular(classification, extracted_text, tone_settings, project_requirements)

    def generate_technical_solution_modular(self, classification, extracted_text, tone_settings, project_requirements=""):
        """
        Generate a comprehensive draft for the "Technical Approach" section using a modular approach
        with advanced prompting and industry-specific insights.
        
        :param classification: str - The client classification ("government" or "enterprise").
        :param extracted_text: str - Text extracted from relevant documents.
        :param tone_settings: dict - Tone settings (e.g., tone, style).
        :param project_requirements: str - Specific project requirements or constraints.
        :return: str - The combined technical solution draft.
        """
        try:
            # Detect industry to provide more specific technical recommendations
            industry = self._detect_industry(extracted_text + " " + project_requirements)
            
            # Get relevant technology stack suggestions based on industry
            relevant_tech = self.industry_tech_stack.get(industry, [])
            tech_suggestions = ", ".join(relevant_tech) if relevant_tech else "No specific industry technologies detected"
            
            # Prepare the context for the AI model
            context = {
                "classification": classification,
                "tone": tone_settings.get('tone', 'Default'),
                "style": tone_settings.get('style', 'Default'),
                "industry": industry,
                "technology_suggestions": tech_suggestions,
                # Check if this is a requirements extraction or proposal structure task
                "is_requirements_task": "extract specific" in project_requirements.lower() or "requirements extraction" in project_requirements.lower(),
                "is_structure_task": "proposal structure" in project_requirements.lower() or "outline" in project_requirements.lower(),
                # Increase context for requirements tasks
                "project_requirements": project_requirements,
                "extracted_text_summary": extracted_text[:3000] if len(extracted_text) > 3000 else extracted_text
            }
            
            # Custom system prompt based on the task type
            if context["is_requirements_task"]:
                system_prompt = """
                You are an expert RFP analyst specializing in extracting concrete, specific requirements from RFP documents.
                Your goal is to identify ALL key requirements that would need to be addressed in a proposal response.
                For each requirement identified, create a clear, concise bullet point starting with a dash (-).
                Focus on extracting requirements related to:
                
                1. Technical capabilities and features
                2. Performance metrics and SLAs
                3. Compliance and regulatory needs
                4. Project deliverables and milestones
                5. Implementation and timeline constraints
                6. Budget and pricing constraints
                7. Team qualifications and experience
                
                Be specific and precise. Avoid vague or generic statements.
                Format each requirement as a single line starting with a dash (-)
                """
                
                user_prompt = f"""
                ## RFP Document Content
                {context['extracted_text_summary']}
                
                ## Extraction Instructions
                {context['project_requirements']}
                
                Carefully analyze the RFP content above and extract all specific requirements.
                Each requirement should be a single line starting with a dash (-).
                Be comprehensive and specific - these requirements will be used to build the proposal structure.
                """
                
            elif context["is_structure_task"]:
                system_prompt = """
                You are an expert proposal writer who specializes in creating effective proposal outlines that directly 
                address RFP requirements. Your goal is to create a comprehensive proposal structure with main sections 
                and bullet points that will guide the content creation process.
                
                Your outline should:
                1. Include 5-7 main sections that logically flow and cover all major RFP requirements
                2. Under each section, list 3-5 specific bullet points of content to address
                3. Ensure each bullet point clearly connects to specific RFP requirements
                4. Follow best practices for proposal structure (Executive Summary first, clear next steps at the end)
                5. Use clear, descriptive language for section titles and bullet points
                
                Format your response with main sections starting with a dash (-) and bullet points indented with an asterisk (*).
                """
                
                user_prompt = f"""
                ## Client Information
                - Classification: {context['classification']}
                - Industry: {context['industry']}
                
                ## RFP Context (Summary)
                {context['extracted_text_summary']}
                
                ## Proposal Structure Instructions
                {context['project_requirements']}
                
                Create a comprehensive proposal structure that directly addresses the requirements.
                Use main sections (starting with -) and bullet points (starting with *) under each section.
                Make sure each section and bullet point is relevant and specific to this particular RFP.
                """
                
            else:
                # Use the default technical solution system prompt
                system_prompt = """
                You are an expert technical solution architect with extensive experience creating detailed technical proposals
                for enterprise and government clients. You excel at:
                1. Understanding client requirements thoroughly
                2. Designing appropriate technical architectures
                3. Selecting the most suitable technologies
                4. Explaining technical concepts clearly to non-technical stakeholders
                5. Creating persuasive, logical solutions that address business problems
                
                Follow these steps when crafting a technical solution:
                1. Analyze requirements thoroughly
                2. Consider specific industry and client needs
                3. Select modern, appropriate technologies
                4. Structure your response with clear sections
                5. Explain WHY each technology choice is appropriate
                6. Include diagrams and visualizations when helpful (described in text)
                """
                
                # Standard technical solution prompt
                user_prompt = f"""
                ## Client Information
                - Classification: {context['classification']}
                - Industry: {context['industry']}
                - Tone/Style: {context['tone']}/{context['style']}
                
                ## Requirements Summary
                {context['extracted_text_summary']}
                
                ## Additional Project Requirements
                {context['project_requirements']}
                
                ## Industry-Specific Technology Suggestions
                {context['technology_suggestions']}
                
                Create a comprehensive technical proposal section that includes:
                
                1. **Requirements Analysis**: Restate and clarify the client's needs
                2. **Proposed Architecture**: High-level design with components and interactions
                3. **Technology Stack**: Specific technologies with justification for each choice
                4. **Implementation Approach**: How the solution will be built and delivered
                5. **Technical Differentiators**: Why our approach is superior
                
                Format your response with clear headings, bullet points for key features, and emphasize how the solution 
                aligns with {context['classification']} requirements and {context['industry']} industry best practices.
                """
            
            # Generate the complete technical solution in one comprehensive call
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            
            technical_solution = response.choices[0].message.content.strip()
            return technical_solution

        except Exception as e:
            self.logger.error(f"Error generating modular technical solution: {e}")
            return f"An error occurred while generating the technical solution: {str(e)[:100]}..."
