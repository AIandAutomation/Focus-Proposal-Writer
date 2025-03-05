"""
Timeline Agent Module
---------------------
This module provides the TimelineAgent class which generates a structured timeline or
implementation plan based on client classification, relevant SOW/RFP text, and tone settings.
"""

import openai
import logging

class TimelineAgent:
    def __init__(self, openai_api_key):
        """
        Initialize the TimelineAgent with the provided OpenAI API key.
        
        :param openai_api_key: str - Your OpenAI API key.
        """
        openai.api_key = openai_api_key
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def generate_timeline(self, classification, relevant_text, tone_settings, additional_context=""):
        """
        Generate a structured timeline or implementation plan for the proposal.
        
        This method builds a prompt using the client classification, relevant SOW or RFP text,
        tone settings, and any additional context. It then uses the OpenAI API to generate a timeline
        that includes potential milestones and estimated durations.
        
        :param classification: str - The client classification ("government" or "enterprise").
        :param relevant_text: str - Relevant text from the SOW or RFP.
        :param tone_settings: dict - Tone settings as provided by the ToneStyleAgent.
        :param additional_context: str - Optional additional project context or constraints.
        :return: str - The generated timeline as a structured string.
        """
        try:
            self.logger.info("Generating timeline using the OpenAI API.")
            
            # Extract key information for summarization if relevant_text is too long
            truncated_text = relevant_text[:3000] if len(relevant_text) > 3000 else relevant_text
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Using the mini model for faster responses
                messages=[
                    {"role": "system", "content": "You are an expert project manager specializing in creating detailed and realistic project timelines."},
                    {"role": "user", "content": f"""
                    Client Classification: {classification}
                    Tone: {tone_settings.get('tone', 'Default')}, Style: {tone_settings.get('style', 'Default')}
                    
                    Project Context:
                    {truncated_text}
                    
                    Additional Requirements:
                    {additional_context}
                    
                    Create a detailed project timeline with the following:
                    1. Clear phases with specific durations (in weeks)
                    2. Key milestones and deliverables for each phase
                    3. Dependencies between phases
                    4. Critical path activities
                    5. Risk factors that might affect the timeline
                    
                    Format the timeline in a structured, easy-to-read manner with clear headings and bullet points.
                    """
                    }
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            timeline_text = response.choices[0].message.content.strip()
            self.logger.info("Timeline generation completed successfully.")
            return timeline_text
            
        except Exception as e:
            self.logger.error(f"Error generating timeline: {e}")
            return f"An error occurred while generating the timeline: {str(e)[:100]}..."

# Example usage:
# if __name__ == "__main__":
#     agent = TimelineAgent("your_openai_api_key")
#     timeline = agent.generate_timeline(
#         classification="enterprise",
#         relevant_text="RFP details about project phases, deliverables, and deadlines.",
#         tone_settings={"tone": "Persuasive", "style": "Business-focused"}
#     )
#     print(timeline)
