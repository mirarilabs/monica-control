from peripherals import *
import config


pump = StandardServo(**config.pump)
fingers = [StandardServo(**finger) for finger in config.fingers]
stepper = Stepper(**config.stepper)
lower_LS = Button(**config.lower_limit_switch)
upper_LS = Button(**config.upper_limit_switch)
encoder = FuzzyEncoder(**config.fuzzy_encoder)

fingers_rig = FingersRig(fingers, **config.fingers_rig)
servo_rig = ServoRig(stepper, lower_LS, upper_LS, encoder, **config.servo_rig)

