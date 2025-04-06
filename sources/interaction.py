
from sources.text_to_speech import Speech
from sources.utility import pretty_print
from sources.router import AgentRouter
from sources.speech_to_text import AudioTranscriber, AudioRecorder

class Interaction:
    """
    Interaction is a class that handles the interaction between the user and the agents.
    """
    def __init__(self, agents,
                 tts_enabled: bool = True,
                 stt_enabled: bool = True,
                 recover_last_session: bool = False):
        self.agents = agents
        self.current_agent = None
        self.router = AgentRouter(self.agents)
        self.speech = Speech(enable=tts_enabled)
        self.is_active = True
        self.last_query = None
        self.last_answer = None
        self.ai_name = self.find_ai_name()
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        if stt_enabled:
            self.transcriber = AudioTranscriber(self.ai_name, verbose=False)
            self.recorder = AudioRecorder()
        if recover_last_session:
            self.load_last_session()
        if tts_enabled:
            self.speech.speak("Hello, we are online and ready. What can I do for you ?")
    
    def find_ai_name(self) -> str:
        """Find the name of the default AI. It is required for STT as a trigger word."""
        ai_name = "jarvis"
        for agent in self.agents:
            if agent.type == "casual_agent":
                ai_name = agent.agent_name
                break
        return ai_name
    
    def load_last_session(self):
        """Recover the last session."""
        for agent in self.agents:
            agent.memory.load_memory(agent.type)
    
    def save_session(self):
        """Save the current session."""
        for agent in self.agents:
            agent.memory.save_memory(agent.type)

    def is_active(self) -> bool:
        return self.is_active
    
    def read_stdin(self) -> str:
        """Read the input from the user."""
        buffer = ""

        PROMPT = "\033[1;35m➤➤➤ \033[0m"
        while not buffer:
            try:
                buffer = input(PROMPT)
            except EOFError:
                return None
            if buffer == "exit" or buffer == "goodbye":
                return None
        return buffer
    
    def transcription_job(self) -> str:
        """Transcribe the audio from the microphone."""
        self.recorder = AudioRecorder(verbose=True)
        self.transcriber = AudioTranscriber(self.ai_name, verbose=True)
        self.transcriber.start()
        self.recorder.start()
        self.recorder.join()
        self.transcriber.join()
        query = self.transcriber.get_transcript()
        return query

    def get_user(self) -> str:
        """Get the user input from the microphone or the keyboard."""
        if self.stt_enabled:
            query = "TTS transcription of user: " + self.transcription_job()
        else:
            query = self.read_stdin()
        if query is None:
            self.is_active = False
            self.last_query = "Goodbye (exit requested by user, dont think, make answer very short)"
            return None
        self.last_query = query
        return query
    
    def think(self) -> bool:
        """Request AI agents to process the user input."""
        if self.last_query is None or len(self.last_query) == 0:
            return False
        agent = self.router.select_agent(self.last_query)
        pretty_print(agent)
        if agent is None:
            return False
        if self.current_agent != agent and self.last_answer is not None:
            ## get last history from previous agent
            self.current_agent.memory.push('user', self.last_query)
            self.current_agent.memory.push('assistant', self.last_answer)
        self.current_agent = agent
        tmp = self.last_answer
        self.last_answer, _ = agent.process(self.last_query, self.speech)
        if self.last_answer == tmp:
            self.last_answer = None
        return True
    
    def show_answer(self) -> None:
        """Show the answer to the user."""
        if self.last_query is None:
            return
        if self.current_agent is not None:
            self.current_agent.show_answer()
        if self.tts_enabled and self.last_answer:
            self.speech.speak(self.last_answer)

