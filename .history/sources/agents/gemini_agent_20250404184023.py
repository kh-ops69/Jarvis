from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent

class GeminiAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        super().__init__(name, prompt_path, provider, verbose, browser)
        self.api_key = 