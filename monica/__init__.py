import config
import device
from utils.music.keyboard import Keyboard
from .wagon import Wagon
from .keystra import Keystra
from .controller import run


keyboard = Keyboard(**config.keyboard)
flight_time = device.stepper._ik_agent.flight_time
wagon = Wagon(keyboard, flight_time, **config.wagon)
keystra = Keystra(wagon, **config.keystra)

