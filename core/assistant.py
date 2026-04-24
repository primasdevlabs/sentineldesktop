import yaml
import logging
from .events import Events
from .conversation_manager import ConversationManager
from .memory_manager import MemoryManager

class Assistant:
    def __init__(self, config_path="sentinel/config/config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.status = "Idle"
        self.modules = {}
        self.skills = []
        
        # Initialize Memory and Conversation
        self.memory = MemoryManager()
        self.conversation_manager = ConversationManager(self.config, self.memory)
        
        Events.subscribe(Events.WAKE_WORD_DETECTED, self.handle_wake_word)
        Events.subscribe(Events.DOUBLE_CLAP_DETECTED, self.handle_wake_word)
        Events.subscribe(Events.USER_SPOKEN_TEXT, self.handle_user_text)
        Events.subscribe(Events.INTENT_DETECTED, self.handle_intent)
        Events.subscribe(Events.ERROR_OCCURRED, self.handle_error)

    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def setup_logging(self):
        log_file = self.config['logging']['file']
        level = getattr(logging, self.config['logging']['level'])
        logging.basicConfig(filename=log_file, level=level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("Assistant")

    def register_module(self, name, module_instance):
        self.modules[name] = module_instance

    def register_skill(self, skill_instance):
        # Inject memory into skills
        skill_instance.memory = self.memory
        self.skills.append(skill_instance)

    def handle_wake_word(self):
        self.update_status("Listening")
        if "stt" in self.modules:
            self.modules["stt"].listen()

    def handle_user_text(self, text):
        self.logger.info(f"User: {text}")

    def handle_intent(self, intent_data):
        intent_name = intent_data.get('intent', {}).get('name')
        text = intent_data.get("text", "")
        self.logger.info(f"Intent: {intent_name} | Text: {text}")
        self.update_status("Thinking")
        
        # Handle manual name setting
        if "call me" in text.lower():
            name = text.lower().split("call me")[-1].strip().capitalize()
            self.memory.set("user_name", name)
            self.speak(f"Got it. I will call you {name} from now on.")
            return

        if text.lower() in ["stop", "never mind", "cancel", "shutup"]:
            self.conversation_manager.clear_context()
            if "tts" in self.modules: self.modules["tts"].stop()
            self.update_status("Idle")
            return

        handled = False
        if intent_name and intent_name != "":
            for skill in self.skills:
                if skill.match_intent(intent_name):
                    skill.handle_intent(intent_data)
                    handled = True
                    break
        
        if not handled:
            self.conversation_manager.get_response(text)

    def handle_error(self, message):
        self.logger.error(message)

    def update_status(self, status):
        self.status = status
        Events.emit(Events.STATUS_CHANGED, status=status)

    def speak(self, text):
        # Always personalize core responses
        p_text = self.memory.personalize_text(text)
        Events.emit(Events.ASSISTANT_RESPONSE, text=p_text)

    def start(self):
        self.logger.info("Sentinel starting...")
        for module in self.modules.values():
            if hasattr(module, "start"): module.start()
        
        # Personal Greeting on Startup
        user_name = self.memory.get("user_name")
        if user_name:
            self.speak(f"Good morning, {user_name}. Sentinel is active and ready.")
        else:
            self.speak("Systems active. Before we begin, what should I call you?")

    def stop(self):
        for module in self.modules.values():
            if hasattr(module, "stop"): module.stop()
