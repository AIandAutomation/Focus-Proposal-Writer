"""
Tone & Style Agent Module
--------------------------
This module provides the ToneStyleAgent class, which sets the tone and style
for the proposal based on the client classification (government or enterprise).
"""

class ToneStyleAgent:
    def __init__(self):
        """
        Initialize ToneStyleAgent with default tone settings for government and enterprise clients.
        """
        # Default tone settings can be easily extended or modified as needed.
        self.tone_settings = {
            "government": {
                "tone": "Formal",
                "style": "Compliance-focused",
                "description": "A formal tone with an emphasis on compliance and regulatory details."
            },
            "enterprise": {
                "tone": "Persuasive",
                "style": "Business-focused",
                "description": "A persuasive tone designed to appeal to business objectives and ROI."
            }
        }

    def get_tone_settings(self, classification_result):
        """
        Retrieve the tone style settings based on the provided classification result.
        
        :param classification_result: str - Classification result ("government" or "enterprise").
        :return: dict - A dictionary containing tone style settings.
        """
        # Convert classification_result to lowercase for consistency.
        key = classification_result.lower()
        # Return the corresponding tone settings; default to 'enterprise' if key is not found.
        return self.tone_settings.get(key, self.tone_settings["enterprise"])
