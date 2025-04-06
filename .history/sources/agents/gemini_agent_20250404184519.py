from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from dotenv import load_dotenv, set_key
import os
from google import genai

class GeminiAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        super().__init__(name, prompt_path, provider, verbose, browser)
        load_dotenv()
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)

    def process(self, prompt, speech_module):
        
    
    def show_answer(self):
        return super().show_answer()