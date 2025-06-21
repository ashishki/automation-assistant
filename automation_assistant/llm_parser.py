# automation_assistant/llm_parser.py

"""
LLMParser: converts a natural language prompt into a structured workflow plan.
"""
import os
import json
import openai

class LLMParser:
    def __init__(self):
        # Initialize OpenAI API key from environment variable
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def parse(self, prompt: str) -> dict:
        """
        Send the user prompt to the OpenAI ChatCompletion endpoint
        and parse the returned text as JSON into a Python dict.

        Args:
            prompt (str): The natural language instruction.

        Returns:
            dict: The parsed workflow plan.

        Raises:
            openai.error.OpenAIError: If the API call fails.
            ValueError: If the returned text is not valid JSON or not a dict.
        """
        # Call the ChatCompletion API with a system prompt structure
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        # Extract the text from the first choice
        raw_text = response.choices[0].text.strip()

        # Attempt to parse the JSON text into a dict
        try:
            plan = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from LLM: {e}")

        # Ensure the parsed object is a dict
        if not isinstance(plan, dict):
            raise ValueError("Parsed plan is not a dict")

        return plan
