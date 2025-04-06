import json
from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.agents.code_agent import CoderAgent
from sources.agents.file_agent import FileAgent
from sources.agents.browser_agent import BrowserAgent
from sources.tools.tools import Tools
from sources.agents.gemini_agent import GeminiAgent

class PlannerAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        """
        The planner agent is a special agent that divides and conquers the task.
        """
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "json": Tools()
        }
        self.tools['json'].tag = "json"
        self.browser = browser
        self.agents = {
            "coder": CoderAgent(name, "prompts/base/coder_agent.txt", provider, verbose=False),
            "file": FileAgent(name, "prompts/base/file_agent.txt", provider, verbose=False),
            "web": BrowserAgent(name, "prompts/base/browser_agent.txt", provider, verbose=False, browser=browser),
            "gemini": GeminiAgent(name, "prompts/base/browser_agent.txt", provider, verbose=False, browser=browser)
        }
        self.role = {
            "en": "Research, setup and code",
            "fr": "Recherche, configuration et codage",
            "zh": "研究，设置和编码",
        }
        self.type = "planner_agent"

    def parse_agent_tasks(self, text):
        tasks = []
        tasks_names = []

        lines = text.strip().split('\n')
        for line in lines:
            if line is None or len(line) == 0:
                continue
            line = line.strip()
            if '##' in line or line[0].isdigit():
                tasks_names.append(line)
                continue
        blocks, _ = self.tools["json"].load_exec_block(text)
        if blocks == None:
            # change -- force adapt
            return (None, None)
        for block in blocks:
            line_json = json.loads(block)
            if 'plan' in line_json:
                for task in line_json['plan']:
                    agent = {
                        'agent': task['agent'],
                        'id': task['id'],
                        'task': task['task']
                    }
                    if 'need' in task:
                        agent['need'] = task['need']
                    tasks.append(agent)
        if len(tasks_names) != len(tasks):
            names = [task['task'] for task in tasks]
            print(names)
            return zip(names, tasks)
        return zip(tasks_names, tasks)
    
    def force_return_json(self, text):
        text = self.format_llm_request(text)
        return text
    
    def make_prompt(self, task, needed_infos):
        if needed_infos is None:
            needed_infos = "No needed informations."
        prompt = f"""
        You are given the following informations:
        {needed_infos}
        Your task is:
        {task}
        """
        return prompt
    
    def show_plan(self, json_plan):
        agents_tasks = self.parse_agent_tasks(json_plan)
        pretty_print(f"--- Plan ---", color="output")
        for task_name, task in agents_tasks:
            pretty_print(f"{task}", color="output")
        pretty_print(f"--- End of Plan ---", color="output")

    def show_segregated_plan(self, json_response):
        parsed_json = json.loads(json_response)
        parsed_info = parsed_json['relevant_response']
        del parsed_json['relevant_response']
        return parsed_info, parsed_json
    
    def process(self, prompt, speech_module) -> str:
        ok = False
        agents_tasks = (None, None)
        while not ok:
            self.wait_message(speech_module)
            animate_thinking("Thinking...", color="status")
            self.memory.push('user', prompt)
            answer, _ = self.llm_request()
            pretty_print(answer.split('\n')[0], color="output")
            # formatted_p_answer = self.check_llm_response(answer, prompt)
            # initial_response = formatted_p_answer['relevant_response']
            # pretty_print(f'Extracted response: {initial_response}')
            # del formatted_p_answer['relevant_response']
            # tmp = self.agents['gemini'].process(prompt)
            # pretty_print(tmp)
            # relevant_information, answer = self.show_segregated_plan(self.agents['gemini'].process(prompt))
            # for item in answer['plan']:
            #     if item['agent'].lower() == 'file' or item['agent'].lower() == 'terminal':
            #         item['task'] += '\n'
            #         item['task'] += relevant_information
            try:     
                self.show_plan(answer)
            except:
                answer = self.force_return_json(answer)
                pretty_print(f'\n\nNew JSON formatted answer: {answer}\n\n')
                self.show_plan(answer)
            ok_str = input("Is the plan ok? (y/n): ")
            if ok_str == 'y':
                ok = True
            else:
                prompt = input("Please reformulate: ")

        agents_tasks = self.parse_agent_tasks(answer)
        prev_agent_answer = None
        for task_name, task in agents_tasks:
            pretty_print(f"I will {task_name}.", color="info")
            agent_prompt = self.make_prompt(task['task'], prev_agent_answer)
            pretty_print(f"Assigned agent {task['agent']} to {task_name}", color="info")
            if speech_module: speech_module.speak(f"I will {task_name}. I assigned the {task['agent']} agent to the task.")
            try:
                prev_agent_answer, _ = self.agents[task['agent'].lower()].process(agent_prompt, speech_module)
                pretty_print(f"-- Agent answer ---\n\n", color="output")
                self.agents[task['agent'].lower()].show_answer()
                pretty_print(f"\n\n", color="output")
            except Exception as e:
                raise e
        self.last_answer = prev_agent_answer
        return prev_agent_answer, ""

if __name__ == "__main__":
    from llm_provider import Provider
    server_provider = Provider("server", "deepseek-r1:14b", "192.168.1.100:5000")
    agent = PlannerAgent("deepseek-r1:14b", "jarvis", "prompts/planner_agent.txt", server_provider)
    ans = agent.process("Make a cool game to illustrate the current relation between USA and europe")