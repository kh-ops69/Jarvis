from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from dotenv import load_dotenv, set_key
import os
from google import genai
import re

class GeminiAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        super().__init__(name, prompt_path, provider, verbose, browser)
        load_dotenv()
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)
        self.instruction_prompt_path = prompt_path
        self.role = {
            "en": "files",
            "fr": "fichiers",
            "zh": "文件",
        }
        self.type = "gemini_agent"

    def clean_json_response(self, response_text):
        """Cleans API response text by removing unwanted characters before JSON parsing."""
        # Remove leading "json" text if present
        response_text = re.sub(r'^\s*json\s*', '', response_text, flags=re.IGNORECASE)

        # Remove triple quotes if present
        response_text = re.sub(r"'''|\"\"\"", "", response_text)

        # Strip extra spaces, newlines
        response_text = response_text.strip()

        return response_text

    def process(self, prompt):
        # Call Gemini API
        with open(self.instruction_prompt_path, 'r') as instruction_file:
            instruction_text = instruction_file.read()
        formatted_prompt = "Here is the user's query: "+prompt
        final_input = instruction_text+'\n'+formatted_prompt
        response = self.client.models.generate_content(contents=final_input, model='gemini-2.0-flash')
        cleaned_response = self.clean_json_response(response.text)
        return cleaned_response
    
    def show_answer(self):
        return super().show_answer()