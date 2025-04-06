import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import datetime
import uuid
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.utility import timer_decorator, pretty_print

class Memory():
    """
    Memory is a class for managing the conversation memory
    It provides a method to compress the memory (experimental, use with caution).
    """
    def __init__(self, system_prompt: str,
                 recover_last_session: bool = False,
                 memory_compression: bool = True):
        self.memory = []
        self.memory = [{'role': 'system', 'content': system_prompt}]
        
        self.session_time = datetime.datetime.now()
        self.session_id = str(uuid.uuid4())
        self.conversation_folder = f"conversations/"
        self.session_recovered = False
        if recover_last_session:
            self.load_memory()
            self.session_recovered = True
        # memory compression system
        self.model = "pszemraj/led-base-book-summary"
        self.device = self.get_cuda_device()
        self.memory_compression = memory_compression
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model)
    
    def get_filename(self) -> str:
        return f"memory_{self.session_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    
    def save_memory(self, agent_type: str = "casual_agent") -> None:
        """Save the session memory to a file."""
        if not os.path.exists(self.conversation_folder):
            os.makedirs(self.conversation_folder)
        save_path = os.path.join(self.conversation_folder, agent_type)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        filename = self.get_filename()
        path = os.path.join(save_path, filename)
        json_memory = json.dumps(self.memory)
        with open(path, 'w') as f:
            f.write(json_memory)
    
    def find_last_session_path(self, path) -> str:
        """Find the last session path."""
        saved_sessions = []
        for filename in os.listdir(path):
            if filename.startswith('memory_'):
                date = filename.split('_')[1]
                saved_sessions.append((filename, date))
        saved_sessions.sort(key=lambda x: x[1], reverse=True)
        if len(saved_sessions) > 0:
            return saved_sessions[0][0]
        return None

    def load_memory(self, agent_type: str = "casual_agent") -> None:
        """Load the memory from the last session."""
        pretty_print(f"Loading {agent_type} past memories... ", color="status")
        if self.session_recovered == True:
            return
        save_path = os.path.join(self.conversation_folder, agent_type)
        if not os.path.exists(save_path):
            pretty_print("No memory to load.", color="success")
            return
        filename = self.find_last_session_path(save_path)
        if filename is None:
            pretty_print("Last session memory not found.", color="warning")
            return
        path = os.path.join(save_path, filename)
        with open(path, 'r') as f:
            self.memory = json.load(f)
        if self.memory[-1]['role'] == 'user':
            self.memory.pop()
        self.compress()
        pretty_print("Session recovered successfully", color="success")
    
    def reset(self, memory: list) -> None:
        self.memory = memory
    
    def push(self, role: str, content: str) -> None:
        """Push a message to the memory."""
        if self.memory_compression and role == 'assistant':
            self.compress()
        curr_idx = len(self.memory)
        if self.memory[curr_idx-1]['content'] == content:
            pretty_print("Warning: same message have been pushed twice to memory", color="error")
        self.memory.append({'role': role, 'content': content})
    
    def clear(self) -> None:
        self.memory = []
    
    def get(self) -> list:
        return self.memory

    def get_cuda_device(self) -> str:
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"

    def summarize(self, text: str, min_length: int = 64) -> str:
        """
        Summarize the text using the AI model.
        Args:
            text (str): The text to summarize
            min_length (int, optional): The minimum length of the summary. Defaults to 64.
        Returns:
            str: The summarized text
        """
        if self.tokenizer is None or self.model is None:
            return text
        if len(text) < min_length*1.5:
            return text
        max_length = len(text) // 2 if len(text) > min_length*2 else min_length*2
        input_text = "summarize: " + text
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = self.model.generate(
            inputs['input_ids'],
            max_length=max_length,  # Maximum length of the summary
            min_length=min_length,  # Minimum length of the summary
            length_penalty=1.0,  # Adjusts length preference
            num_beams=4,  # Beam search for better quality
            early_stopping=True  # Stop when all beams finish
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summary.replace('summary:', '')
        return summary
    
    @timer_decorator
    def compress(self) -> str:
        """
        Compress the memory using the AI model.
        """
        for i in range(len(self.memory)):
            if i < 3:
                continue
            if self.memory[i]['role'] == 'system':
                continue
            if len(self.memory[i]['content']) > 128:
                self.memory[i]['content'] = self.summarize(self.memory[i]['content'])

if __name__ == "__main__":
    memory = Memory("You are a helpful assistant.",
                    recover_last_session=False, memory_compression=True)
    
    sample_text = """
The error you're encountering:
cuda.cu:52:10: fatal error: helper_functions.h: No such file or directory
 #include <helper_functions.h>
indicates that the compiler cannot find the helper_functions.h file. This is because the #include <helper_functions.h> directive is looking for the file in the system's include paths, but the file is either not in those paths or is located in a different directory.
1. Use #include "helper_functions.h" Instead of #include <helper_functions.h>
Angle brackets (< >) are used for system or standard library headers.
Quotes (" ") are used for local or project-specific headers.
If helper_functions.h is in the same directory as cuda.cu, change the include directive to:
3. Verify the File Exists
Double-check that helper_functions.h exists in the specified location. If the file is missing, you'll need to obtain or recreate it.
4. Use the Correct CUDA Samples Path (if applicable)
If helper_functions.h is part of the CUDA Samples, ensure you have the CUDA Samples installed and include the correct path. For example, on Linux, the CUDA Samples are typically located in /usr/local/cuda/samples/common/inc. You can include this path like so:
Use #include "helper_functions.h" for local files.
Use the -I flag to specify the directory containing helper_functions.h.
Ensure the file exists in the specified location.
    """
    
    memory.push('user', "why do i get this error?")
    memory.push('assistant', sample_text)
    print("\n---\nmemory before:", memory.get())
    memory.compress()
    print("\n---\nmemory after:", memory.get())
    memory.save_memory()
    