"""
Pricing Agent Module
--------------------
This module provides the PricingAgent class, which constructs a pricing table
based on provided project scope details such as role, hourly rate, and estimated hours.
"""

import logging

class PricingAgent:
    def __init__(self):
        """
        Initialize the PricingAgent and configure logging.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def generate_pricing_table(self, pricing_details):
        """
        Generate a cleanly formatted pricing table based on the provided project scope details.

        :param pricing_details: list of dictionaries. Each dictionary should include:
            - "role": str - The role description.
            - "hourly_rate": number - The hourly rate for the role.
            - "estimated_hours": number - The estimated number of hours.
        :return: str - A formatted pricing table showing role, hourly rate, estimated hours, and total cost.
                 If the input data is insufficient or invalid, an error message is returned.
        """
        if not pricing_details or not isinstance(pricing_details, list):
            self.logger.error("No pricing data provided or invalid data format.")
            return "Insufficient pricing data provided."

        # Create table header
        header = f"{'Role':<20} {'Hourly Rate':<15} {'Estimated Hours':<18} {'Total Cost':<15}\n"
        header += "-" * 70 + "\n"
        table_lines = [header]

        # Process each pricing detail entry
        for detail in pricing_details:
            try:
                role = detail.get("role", "N/A")
                hourly_rate = float(detail.get("hourly_rate", 0))
                estimated_hours = float(detail.get("estimated_hours", 0))
                total_cost = hourly_rate * estimated_hours

                row = f"{role:<20} ${hourly_rate:<14.2f} {estimated_hours:<18.2f} ${total_cost:<14.2f}\n"
                table_lines.append(row)
            except Exception as e:
                self.logger.error(f"Error processing pricing detail {detail}: {e}")
                continue

        return "".join(table_lines)
