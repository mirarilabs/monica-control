import device
import config
import monica
import uasyncio
from time import ticks_ms, ticks_add, ticks_diff
from .planner import plan_song as plan_method


async def home_all():
	device.pump.go_home()
	await device.pump.wait("ReachedHome")
	device.pump.go_to(0)  # Set to 0% volume (silence)
	device.fingers_rig.go_home()
	await device.fingers_rig.cautionary_wait()
	device.servo_rig.go_home()
	await device.stepper.wait("Homed")

async def play_song_coro():
	device.pump.go_to(volume_percent)
	print(f"Setting pump to {volume_percent}% volume")
	await device.pump.wait("ReachedTarget")
	duties, path = plan_method()

	# Go to initial position
	position = path[0]
	steps = monica.wagon.calculate_steps(position)
	device.stepper.set_target(steps)
	print("Waiting for stepper to reach initial position")
	await device.stepper.wait("ReachedTarget")

	print("Playing song")
	song_start_ms = ticks_ms()
	for i in range(len(duties)):
		duty = duties[i]
		next_pos = path[i + 1] # next_pos will make sense when the IK has functionality for moving in a set duration
		next_steps = monica.wagon.calculate_steps(next_pos)
		device.stepper.set_target(next_steps)
		
		if duty.chord is None:
			device.fingers_rig.go_home()
		else:
			fingerings = monica.wagon.calculate_fingerings(duty.chord, position)
			device.fingers_rig.play(fingerings)

		# wait till duty is over
		duty_end_ms = ticks_add(song_start_ms, duty.end_ms)
		wait_ms = ticks_diff(duty_end_ms, ticks_ms())
		print(f"Waiting for {wait_ms} ms to duty completion")
		await uasyncio.sleep_ms(wait_ms)

		position = next_pos

def cancel_song():
	print("Cancelling song")
	if play_song_task:
		play_song_task.cancel() #type: ignore
	device.fingers_rig.go_home()
	device.pump.go_to(0)  # Set to 0% volume (silence)
	print("Song cancelled")
	device.servo_rig._encoder_timer.deinit()
	print("Hacky: ServoRig _encoder_timer deinitialized from here")

async def play_song_with_plan(duties, path, volume_override=None):
	"""Play a song with pre-planned duties and path"""
	await home_all()
	
	# Set volume (use override or default)
	target_volume = volume_override if volume_override is not None else volume_percent
	device.pump.go_to(target_volume)
	print(f"Setting pump to {target_volume}% volume")
	await device.pump.wait("ReachedTarget")

	# Go to initial position
	position = path[0]
	steps = monica.wagon.calculate_steps(position)
	device.stepper.set_target(steps)
	print("Waiting for stepper to reach initial position")
	await device.stepper.wait("ReachedTarget")

	print("Playing song")
	song_start_ms = ticks_ms()
	current_volume = target_volume
	
	for i in range(len(duties)):
		duty = duties[i]
		next_pos = path[i + 1]
		next_steps = monica.wagon.calculate_steps(next_pos)
		device.stepper.set_target(next_steps)
		
		# Handle volume change if specified in duty
		if duty.volume_percent is not None and duty.volume_percent != current_volume:
			device.pump.go_to(duty.volume_percent)
			current_volume = duty.volume_percent
			print(f"Volume changed to {current_volume}%")
		
		if duty.chord is None:
			device.fingers_rig.go_home()
		else:
			fingerings = monica.wagon.calculate_fingerings(duty.chord, position)
			device.fingers_rig.play(fingerings)

		# wait till duty is over
		duty_end_ms = ticks_add(song_start_ms, duty.end_ms)
		wait_ms = ticks_diff(duty_end_ms, ticks_ms())
		print(f"Waiting for {wait_ms} ms to duty completion")
		await uasyncio.sleep_ms(wait_ms)

		position = next_pos

	print("Song finished")
	
	# Disable encoder monitoring during cleanup to prevent false cancellations
	device.servo_rig._encoder_timer.deinit()
	print("Encoder monitoring disabled for cleanup")
	
	device.pump.go_to(0)  # Set to 0% volume (silence)
	device.fingers_rig.go_home()
	await device.fingers_rig.cautionary_wait()
	device.stepper.set_target(0)
	await device.stepper.wait("ReachedTarget")
	await home_all()

async def run():
	await home_all()
	play_song_task = uasyncio.create_task(play_song_coro())
	device.stepper.register_callback("SensorCancel", cancel_song)
	await play_song_task #type: ignore
	print("Song finished")
	
	# Disable encoder monitoring during cleanup to prevent false cancellations
	device.servo_rig._encoder_timer.deinit()
	print("Encoder monitoring disabled for cleanup")
	
	device.pump.go_to(0)  # Set to 0% volume (silence)
	device.fingers_rig.go_home()
	await device.fingers_rig.cautionary_wait()
	device.stepper.set_target(0)
	await device.stepper.wait("ReachedTarget")
	await home_all()


volume_percent = config.controller["volume_percent"]

play_song_task = None

