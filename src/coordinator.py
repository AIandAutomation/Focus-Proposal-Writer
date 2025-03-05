"""
Coordinator Agent Module
--------------------------
This module provides the CoordinatorAgent class, which orchestrates the proposal
drafting process by receiving requests from the Streamlit UI, determining the necessary
actions, and calling the appropriate agents. It handles classification logic first to set
the tone and style, then calls subsequent agents (TechnicalSolutionAgent, TimelineAgent,
PricingAgent, IndustryAnalysisAgent, UserFeedbackAgent) as needed, and merges their outputs
into a unified structure.
"""

import logging
import traceback
from functools import lru_cache

# Import agents from the agents directory
from src.agents.classification import ClassificationAgent
from src.agents.tone_style import ToneStyleAgent
from src.agents.technical_solution import TechnicalSolutionAgent
from src.agents.timeline import TimelineAgent
from src.agents.pricing import PricingAgent
from src.agents.industry_analysis import IndustryAnalysisAgent
from src.agents.user_feedback import UserFeedbackAgent

class CoordinatorAgent:
    def __init__(self, openai_api_key):
        """
        Initialize the CoordinatorAgent by instantiating all necessary agents.
        
        :param openai_api_key: str - API key for OpenAI, used by agents that require language model access.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        self.logger.info("Initializing CoordinatorAgent and all sub-agents")
        
        # Store the API key
        self.openai_api_key = openai_api_key
        
        # Create a cache to store results and avoid redundant API calls
        self.cache = {}
        
        # Initialize all agents with error handling
        try:
            self.classifier = ClassificationAgent()
            self.tone_agent = ToneStyleAgent()
            self.technical_agent = TechnicalSolutionAgent(openai_api_key)
            self.timeline_agent = TimelineAgent(openai_api_key)
            self.pricing_agent = PricingAgent()
            self.industry_agent = IndustryAnalysisAgent()
            self.feedback_agent = UserFeedbackAgent(openai_api_key)
            self.logger.info("All agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to initialize agent system: {str(e)}")

    @lru_cache(maxsize=32)
    def _get_classification_and_tone(self, client_text):
        """
        Get classification and tone settings based on client text.
        This method is cached to avoid redundant processing.
        
        :param client_text: str - Information about the client.
        :return: tuple - (classification_result, tone_settings)
        """
        self.logger.info("Classifying client and determining tone")
        try:
            classification_result = self.classifier.classify(client_text)
            tone_settings = self.tone_agent.get_tone_settings(classification_result)
            self.logger.info(f"Classification: {classification_result}, Tone: {tone_settings.get('tone', 'Default')}")
            return classification_result, tone_settings
        except Exception as e:
            self.logger.error(f"Error in classification process: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Return defaults in case of an error
            return "enterprise", self.tone_agent.get_tone_settings("enterprise")

    def process_request(self, request_type, **kwargs):
        """
        Process a request from the Streamlit UI and call the appropriate agent method.
        
        Supported request types:
        - "generate_technical_section"
        - "generate_timeline"
        - "generate_pricing"
        - "apply_user_feedback"
        - "analyze_industry"
        
        :param request_type: str - Type of request.
        :param kwargs: dict - Additional parameters required for the specific request.
        :return: dict - A unified dictionary containing the results of the operation.
        """
        self.logger.info(f"Processing request: {request_type}")
        results = {"status": "success", "message": "Request processed successfully"}
        
        try:
            # Validate required parameters based on request type
            self._validate_request_parameters(request_type, kwargs)
            
            if request_type == "generate_technical_section":
                results.update(self._handle_technical_section_request(kwargs))
                
            elif request_type == "generate_timeline":
                results.update(self._handle_timeline_request(kwargs))
                
            elif request_type == "generate_pricing":
                results.update(self._handle_pricing_request(kwargs))
                
            elif request_type == "apply_user_feedback":
                results.update(self._handle_feedback_request(kwargs))
                
            elif request_type == "analyze_industry":
                results.update(self._handle_industry_analysis_request(kwargs))
                
            else:
                error_msg = f"Unsupported request type: {request_type}"
                self.logger.error(error_msg)
                results = {"status": "error", "message": error_msg}
                
        except ValueError as e:
            error_msg = f"Invalid request parameters: {str(e)}"
            self.logger.error(error_msg)
            results = {"status": "error", "message": error_msg}
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            results = {"status": "error", "message": error_msg}
            
        return results

    def _validate_request_parameters(self, request_type, kwargs):
        """
        Validate that the required parameters are provided for a given request type.
        
        :param request_type: str - Type of request.
        :param kwargs: dict - Parameters provided for the request.
        :raises ValueError: If required parameters are missing.
        """
        required_params = {
            "generate_technical_section": ["client_text", "extracted_text"],
            "generate_timeline": ["client_text", "relevant_text"],
            "generate_pricing": ["pricing_details"],
            "apply_user_feedback": ["current_draft", "user_feedback"],
            "analyze_industry": ["extracted_text"]
        }
        
        if request_type not in required_params:
            raise ValueError(f"Unknown request type: {request_type}")
            
        missing_params = [param for param in required_params[request_type] if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

    def _handle_technical_section_request(self, kwargs):
        """
        Handle a request to generate a technical section.
        
        :param kwargs: dict - Request parameters.
        :return: dict - Results of the operation.
        """
        self.logger.info("Generating technical section")
        
        client_text = kwargs.get("client_text")
        extracted_text = kwargs.get("extracted_text", "")
        project_requirements = kwargs.get("project_requirements", "")
        
        # Get classification and tone settings
        classification_result, tone_settings = self._get_classification_and_tone(client_text)
        
        # Also get industry analysis to enhance the technical solution
        industry_analysis = self.industry_agent.analyze_industry(extracted_text)
        
        # Generate technical solution with enhanced context
        technical_solution = self.technical_agent.generate_technical_solution(
            classification_result, 
            extracted_text, 
            tone_settings, 
            project_requirements + "\n\nIndustry Analysis: " + industry_analysis
        )
        
        return {
            "classification": classification_result,
            "tone_settings": tone_settings,
            "industry_analysis": industry_analysis,
            "technical_solution": technical_solution
        }

    def _handle_timeline_request(self, kwargs):
        """
        Handle a request to generate a timeline.
        
        :param kwargs: dict - Request parameters.
        :return: dict - Results of the operation.
        """
        self.logger.info("Generating project timeline")
        
        client_text = kwargs.get("client_text")
        relevant_text = kwargs.get("relevant_text", "")
        additional_context = kwargs.get("additional_context", "")
        
        # Get classification and tone settings
        classification_result, tone_settings = self._get_classification_and_tone(client_text)
        
        # Generate timeline
        timeline = self.timeline_agent.generate_timeline(
            classification_result, relevant_text, tone_settings, additional_context
        )
        
        return {
            "classification": classification_result,
            "tone_settings": tone_settings,
            "timeline": timeline
        }

    def _handle_pricing_request(self, kwargs):
        """
        Handle a request to generate a pricing table.
        
        :param kwargs: dict - Request parameters.
        :return: dict - Results of the operation.
        """
        self.logger.info("Generating pricing table")
        
        pricing_details = kwargs.get("pricing_details", [])
        if not pricing_details:
            raise ValueError("Pricing details cannot be empty")
            
        pricing_table = self.pricing_agent.generate_pricing_table(pricing_details)
        
        return {"pricing_table": pricing_table}

    def _handle_feedback_request(self, kwargs):
        """
        Handle a request to apply user feedback to a draft.
        
        :param kwargs: dict - Request parameters.
        :return: dict - Results of the operation.
        """
        self.logger.info("Applying user feedback to existing draft")
        
        current_draft = kwargs.get("current_draft", "")
        user_feedback = kwargs.get("user_feedback", "")
        
        if not current_draft:
            raise ValueError("Current draft cannot be empty")
        if not user_feedback:
            raise ValueError("User feedback cannot be empty")
            
        revised_draft = self.feedback_agent.incorporate_feedback(current_draft, user_feedback)
        
        return {"revised_draft": revised_draft}

    def _handle_industry_analysis_request(self, kwargs):
        """
        Handle a request to analyze industry information.
        
        :param kwargs: dict - Request parameters.
        :return: dict - Results of the operation.
        """
        self.logger.info("Analyzing industry information")
        
        extracted_text = kwargs.get("extracted_text", "")
        
        industry_analysis = self.industry_agent.analyze_industry(extracted_text)
        
        return {"industry_analysis": industry_analysis}

# Example usage:
# if __name__ == "__main__":
#     coordinator = CoordinatorAgent("your_openai_api_key")
#     tech_result = coordinator.process_request(
#         "generate_technical_section",
#         client_text="Information about a federal agency...",
#         extracted_text="Document content describing project scope and challenges...",
#         project_requirements="Must adhere to strict government guidelines."
#     )
#     print(tech_result)
