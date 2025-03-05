"""
Classification Agent Module
-----------------------------
This module provides the ClassificationAgent class that performs advanced classification 
of client organizations into detailed categories beyond just "government" or "enterprise".
It uses a comprehensive keyword matching system with weighted scoring to determine the
most likely client type, industry, and size.
"""

import re
import logging

class ClassificationAgent:
    def __init__(self):
        """
        Initialize the ClassificationAgent with an enhanced classification system that includes:
        - Client type (government, enterprise, non-profit, academic)
        - Industry sector 
        - Organization size
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)
            
        # Enhanced government keywords with subcategories
        self.government_keywords = {
            "federal": ["federal", "national", "united states", "federal agency", "u.s. government"],
            "state": ["state government", "state agency", "state of"],
            "local": ["municipal", "county", "city of", "local government", "town"],
            "military": ["defense", "military", "army", "navy", "air force", "marines", "dod", "defense department"],
            "general": ["public sector", "government", "govt", "g2g", "g2b"]
        }
        
        # Enhanced enterprise keywords with industry types
        self.enterprise_keywords = {
            "corporate": ["private", "corporation", "inc", "llc", "company", "business", "enterprise"],
            "finance": ["bank", "financial", "investment", "insurance", "capital", "wealth", "fintech"],
            "healthcare": ["healthcare", "hospital", "medical", "health system", "clinic", "pharma"],
            "technology": ["tech", "software", "it company", "technology", "digital", "tech firm"],
            "retail": ["retail", "store", "e-commerce", "consumer goods", "shopping"],
            "manufacturing": ["manufacturing", "factory", "production", "industrial"]
        }
        
        # Additional organization types
        self.other_org_keywords = {
            "non_profit": ["non-profit", "nonprofit", "ngo", "foundation", "charity", "501c"],
            "academic": ["university", "school", "college", "education", "academy", "institute"]
        }
        
        # Size indicators
        self.size_keywords = {
            "small": ["small business", "startup", "small company", "fewer than 50", "small team"],
            "medium": ["medium-sized", "growing company", "mid-size"],
            "large": ["large enterprise", "corporation", "fortune 500", "global", "multinational", "enterprise"],
            "government_large": ["federal", "department", "agency"]
        }

    def classify(self, text):
        """
        Classify the client organization based on the provided text data, using enhanced
        matching algorithms to determine client type, industry, and size.
        
        :param text: str - Text data describing the client organization.
        :return: str - Main classification ("government" or "enterprise") for backward compatibility.
                       The detailed classification is logged but not returned.
        """
        if not text or not isinstance(text, str):
            self.logger.warning("Empty or invalid text provided for classification.")
            return "enterprise"  # Default to enterprise for empty or invalid inputs
            
        text_lower = text.lower()
        
        # Score calculation for each category
        gov_score = self._calculate_category_score(text_lower, self.government_keywords)
        enterprise_score = self._calculate_category_score(text_lower, self.enterprise_keywords)
        other_score = self._calculate_category_score(text_lower, self.other_org_keywords)
        
        # Determine primary classification
        max_score = max(gov_score, enterprise_score, other_score)
        if max_score == 0:
            self.logger.info("No clear classification indicators found. Defaulting to 'enterprise'.")
            primary_class = "enterprise"
        elif max_score == gov_score:
            primary_class = "government"
        elif max_score == other_score:
            # For backward compatibility, treat non-profits and academic as "enterprise"
            primary_class = "enterprise"
            self.logger.info(f"Classified as non-government organization (non-profit or academic)")
        else:
            primary_class = "enterprise"
        
        # Determine size
        size = self._determine_size(text_lower, primary_class)
        
        # Log detailed classification but return simple class for backward compatibility
        self.logger.info(f"Classification: {primary_class}, Size: {size}")
        return primary_class

    def _calculate_category_score(self, text, category_dict):
        """
        Calculate a score for a category based on keyword matches.
        
        :param text: str - Lowercase text to analyze.
        :param category_dict: dict - Dictionary of subcategories and their keywords.
        :return: int - Score for this category.
        """
        score = 0
        for subcategory, keywords in category_dict.items():
            for keyword in keywords:
                # Look for word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text)
                score += len(matches)
                
        return score

    def _determine_size(self, text, primary_class):
        """
        Determine the organization size based on keywords.
        
        :param text: str - Lowercase text to analyze.
        :param primary_class: str - Primary classification (government or enterprise).
        :return: str - Size classification.
        """
        size_scores = {}
        
        for size, keywords in self.size_keywords.items():
            score = 0
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text)
                score += len(matches)
            size_scores[size] = score
        
        # Special case: government organizations are typically considered large
        if primary_class == "government" and size_scores.get("government_large", 0) > 0:
            return "large"
            
        # Find the size with the highest score
        max_score = 0
        max_size = "medium"  # Default to medium if no clear size indicators
        
        for size, score in size_scores.items():
            if size != "government_large" and score > max_score:
                max_score = score
                max_size = size
                
        return max_size
