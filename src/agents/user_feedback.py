"""
User Feedback Agent Module
--------------------------
This module provides the UserFeedbackAgent class, which integrates user feedback into an existing
proposal section. The agent constructs a prompt combining the current draft and the user's suggestions,
and then uses a language model (via the OpenAI API) to generate a revised version of the proposal.
"""

import openai
import logging

class UserFeedbackAgent:
    def __init__(self, openai_api_key):
        """
        Initialize the UserFeedbackAgent with the provided OpenAI API key.
        
        :param openai_api_key: str - Your OpenAI API key.
        """
        openai.api_key = openai_api_key
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def incorporate_feedback(self, current_draft, user_feedback):
        """
        Incorporate user feedback into the current proposal draft.
        
        This method constructs a prompt that includes the current draft and the user-provided feedback.
        It then uses the OpenAI API to generate a revised version of the proposal section that integrates
        the user's suggestions seamlessly.
        
        :param current_draft: str - The existing draft of the proposal section.
        :param user_feedback: str - The feedback provided by the user.
        :return: str - The revised proposal section incorporating the feedback.
        """
        try:
            self.logger.info("Incorporating user feedback into the proposal section using the OpenAI API.")
            
            # Set up a context-rich system message
            system_message = """
            You are an expert proposal writer with extensive experience in incorporating feedback effectively.
            When revising content:
            1. Maintain the original document structure
            2. Implement requested changes with precision
            3. Improve clarity and persuasiveness
            4. Maintain consistent tone and style throughout
            5. Highlight the most important changes you've made in a summary at the end
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"""
                    Current Proposal Section:
                    ```
                    {current_draft}
                    ```
                    
                    User Feedback:
                    ```
                    {user_feedback}
                    ```
                    
                    Please revise the proposal section to incorporate this feedback thoughtfully and cohesively.
                    """}
                ],
                max_tokens=1200,
                temperature=0.7,
            )
            
            revised_draft = response.choices[0].message.content.strip()
            self.logger.info("User feedback incorporated successfully.")
            return revised_draft
            
        except Exception as e:
            self.logger.error(f"Error incorporating user feedback: {e}")
            return f"Error incorporating feedback: {str(e)[:100]}... Please try again with more specific instructions."
