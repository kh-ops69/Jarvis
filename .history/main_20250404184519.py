#!/usr/bin python3

import sys
import signal
import argparse
import configparser

from sources.llm_provider import Provider
from sources.interaction import Interaction
from sources.agents import Agent, CoderAgent, CasualAgent, FileAgent, PlannerAgent, BrowserAgent, GeminiAgent
from sources.browser import Browser, create_driver

import warnings
warnings.filterwarnings("ignore")

config = configparser.ConfigParser()
config.read('config.ini')

def handleInterrupt(signum, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handler=handleInterrupt)

    # checking pre requisites 
    provider = Provider(provider_name=config["MAIN"]["provider_name"],
                        model=config["MAIN"]["provider_model"],
                        server_address=config["MAIN"]["provider_server_address"],
                        is_local=config.getboolean('MAIN', 'is_local'))

    browser = Browser(create_driver(headless=config.getboolean('MAIN', 'headless_browser')))
    personality_folder = "jarvis" if config.getboolean('MAIN', 'jarvis_personality') else "base"

    agents = [
        CasualAgent(name=config["MAIN"]["agent_name"],
                    prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
                    provider=provider, verbose=False),
        CoderAgent(name="coder",
                   prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
                   provider=provider, verbose=False),
        FileAgent(name="File Agent",
                  prompt_path=f"prompts/{personality_folder}/file_agent.txt",
                  provider=provider, verbose=False),
        BrowserAgent(name="Browser",
                     prompt_path=f"prompts/{personality_folder}/browser_agent.txt",
                     provider=provider, verbose=False, browser=browser),
        PlannerAgent(name="Planner",
                     prompt_path=f"prompts/{personality_folder}/planner_agent.txt",
                     provider=provider, verbose=False, browser=browser),
        GeminiAgent()
    ]

    interaction = Interaction(agents,
                              tts_enabled=config.getboolean('MAIN', 'speak'),
                              stt_enabled=config.getboolean('MAIN', 'listen'),
                              recover_last_session=config.getboolean('MAIN', 'recover_last_session'))
    try:
        while interaction.is_active:
            interaction.get_user()
            if interaction.think():
               # try:
               interaction.show_answer()
                # except:
                #     interaction.get_user()
    except Exception as e:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()
        raise e
    finally:
        if config.getboolean('MAIN', 'save_session'):
            interaction.save_session()


if __name__ == "__main__":
    main()
