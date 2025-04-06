import json, re
from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.agents.code_agent import CoderAgent
from sources.agents.file_agent import FileAgent
from sources.agents.browser_agent import BrowserAgent
from sources.tools.tools import Tools
from sources.agents.gemini_agent import GeminiAgent
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas

class PlannerAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        """
        The planner agent is a special agent that divides and conquers the task.
        """
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "json": Tools()
        }
        self.formats = ['pdf', 'txt', 'text']
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
        """
        Parse JSON-formatted agent task definitions from the given string.

        Args:
            text (str): A JSON string with a "plan" list of tasks.

        Returns:
            list of tuples: Each tuple contains (task_name, task_dict)
        """
        try:
            # If it's a dict already (not a raw string), skip parsing
            if isinstance(text, dict):
                data = text
            else:
                data = json.loads(text)
        except json.JSONDecodeError as e:
            print("❌ Failed to parse JSON:", e)
            return None

        tasks = []

        if "plan" in data:
            for task in data["plan"]:
                task_name = task.get("task", "Unnamed Task")
                tasks.append((task_name, task))
            return tasks

        return None
    
    def parse_agents(self, text):
        """
        Parse JSON-formatted agent task definitions from the given string.

        Args:
            text (str): A JSON string with a "plan" list of tasks.

        Returns:
            list of tuples: Each tuple contains (task_name, task_dict)
        """
        try:
            # If it's a dict already (not a raw string), skip parsing
            if isinstance(text, dict):
                data = text
            else:
                data = json.loads(text)
        except json.JSONDecodeError as e:
            print("❌ Failed to parse JSON:", e)
            return None

        agents = []

        if "plan" in data:
            for task in data["plan"]:
                agent_name = task.get("agent", "Unnamed agent")
                agents.append(agent_name)
            return agents

        return None
    
    def force_return_json(self, text, prompt):
        text = self.format_llm_request(text, prompt)
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
    

    def extract_outer_json(self, text):
        """
        Extracts the first valid outermost JSON object from a string.
        Removes any characters before or after the JSON.
        """
        match = re.search(r'\{(?:[^{}]|(?R))*\}', text, re.DOTALL)
        return match.group(0) if match else None
    
    def show_plan(self, json_plan):
        # json_plan = self.extract_outer_json(json_plan)
        agents_tasks = self.parse_agent_tasks(json_plan)
        pretty_print(f'\nAgent Tasks: {agents_tasks}\n')
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
            initial_answer, _ = self.llm_request()
            # answer = self.format_llm_request(answer, prompt)
            # pretty_print(answer.split('\n')[0], color="output")
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
            answer = self.force_return_json(initial_answer, prompt)
            # pretty_print(f'\n\nNew JSON formatted answer: {answer}\n\n')
            answer = json.loads (answer)
            for agent_description in answer['plan']:
                if agent_description['agent'].lower() == 'web':
                    agent_description['agent'] = 'Gemini'
            try:
                self.show_plan(answer)
            except:
                answer = self.force_return_json(initial_answer, prompt)
                self.show_plan(answer)
            ok_str = input("Is the plan ok? (y/n): ")
            if ok_str == 'y':
                ok = True
            else:
                prompt = input("Please reformulate: ")

        agents_tasks = self.parse_agent_tasks(answer)
        agents = self.parse_agents(answer[0])
        prev_agent_answer = None
        tasks_completed = []
        for agent, (task_name, task) in zip(agents, agents_tasks):
            tasks_completed.append(agent.lower())
            pretty_print(f"I will {task_name}.", color="info")
            agent_prompt = self.make_prompt(task['task'], prev_agent_answer)
            pretty_print(f"Assigned agent {task['agent']} to {task_name}", color="info")
            if tasks_completed[0] == 'gemini':
                extracted_answer = self.extract_answer(self.last_answer, prompt)
                for element in self.formats:
                    if element in prompt:
                        if element == 'txt' or element == 'text':
                            filename = input('Please enter filename')
                            with open(f'{filename}.txt', 'w') as file:
                                file.write(extracted_answer)
                        elif element == 'pdf':
                            c = canvas.Canvas("output.pdf")
                            # Create a TextObject
                            text_object = c.beginText(100, 750)
                            text_object.setFont("Helvetica", 12)

                            # Split and wrap manually by lines
                            for line in extracted_answer.split('\n'):
                                text_object.textLine(line)

                            c.drawText(text_object)
                            c.save()
                    return
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