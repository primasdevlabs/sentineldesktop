import subprocess
from sentinel.core.events import Events

class TTSModule:
    def __init__(self, balcon_path, voice=None, volume=100, speed=0):
        self.balcon_path = balcon_path
        self.voice = voice
        self.volume = volume
        self.speed = speed
        self.process = None
        Events.subscribe(Events.ASSISTANT_RESPONSE, self.speak)
        Events.subscribe(Events.STATUS_CHANGED, self.handle_status_interrupt)

    def handle_status_interrupt(self, status):
        if status == "Listening":
            self.stop()

    def speak(self, text):
        self.stop()
        cmd = [self.balcon_path, "-t", text]
        if self.voice: cmd.extend(["-n", self.voice])
        cmd.extend(["-v", str(self.volume), "-s", str(self.speed)])
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            Events.emit(Events.ERROR_OCCURRED, message=f"TTS Failed: {e}")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
