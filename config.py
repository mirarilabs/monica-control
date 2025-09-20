from utils.music.notes import name_2_note


# Physical measurements of the rail in different units
RAIL_WAGON_INTERVALS = 11
RAIL_STEPPER_STEPS = 20680
RAIL_ENCODER_UNITS = 387

STEPPER_2_ENCODER = RAIL_ENCODER_UNITS/RAIL_STEPPER_STEPS
WAGON_2_STEPPER = RAIL_STEPPER_STEPS/RAIL_WAGON_INTERVALS
WAGON_2_ENCODER = RAIL_ENCODER_UNITS/RAIL_WAGON_INTERVALS
ENCODER_2_STEPPER = 1/STEPPER_2_ENCODER
ENCODER_2_WAGON = 1/WAGON_2_ENCODER
STEPPER_2_WAGON = 1/WAGON_2_STEPPER


events = {
		"awake_interval_ms"		: 20
}

controller = {
		"volume_percent"		: 50  # Default volume as percentage (0-100% user range, maps to 30-70% servo)
}

pump = {
		"pin"					: 7
	,	"min_duty"				: 1500
	,	"max_duty"				: 8600
	,	"max_flight_time"		: 0.33
	,	"pwm_freq"				: 50
	,	"named_positions"		: { "Home" : 0, "Silence" : 0 }  # Keep only essential named positions
}

fingers = [
	{"pin": 0, "min_duty": 2200, "max_duty": 4700, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 0, "Right" : 1 }},
	{"pin": 1, "min_duty": 2200, "max_duty": 4600, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 0, "Right" : 1 }},
	{"pin": 2, "min_duty": 1800, "max_duty": 4400, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 0, "Right" : 1 }},
	{"pin": 3, "min_duty": 2000, "max_duty": 4700, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 0, "Right" : 1 }},
	{"pin": 4, "min_duty": 1900, "max_duty": 4800, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 1, "Right" : 0 }},
	{"pin": 5, "min_duty": 2000, "max_duty": 4500, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 1, "Right" : 0 }},
	{"pin": 6, "min_duty": 2000, "max_duty": 4500, "max_flight_time": 0.16, "pwm_freq": 50, "named_positions": { "Home" : 0.5, "Left" : 1, "Right" : 0 }},
]

stepper = {
		"pin_mode0"				: 11
	,	"pin_mode1"				: 14
	,	"pin_mode2"				: 15
	,	"stepping_mode"			: 16

	,	"pin_engage"			: 10
	,	"pin_dir"				: 13
	,	"pin_step"				: 12
	
	,	"dir_0_is_positive"		: False
	
	,	"cruise_speed"			: 35000
	,	"accel"					: 250000
	,	"interval_ms"			: 4
}

lower_limit_switch = {
		"pin"					: 17
	,	"poll_interval_ms"		: 50
}

upper_limit_switch = {
		"pin"					: 16
	,	"poll_interval_ms"		: 50
}

fuzzy_encoder = {
	"rotary_encoder_config" : {
			"pin_x"					: 18
		,	"pin_y"					: 19
		,	"clicks_per_turn"		: 20
		,	"clockwise"				: True
		,	"default_to_last_diff"	: True
	}
	,	"base_tolerance"		: 6
	,	"uncertain_tolerance"	: 0
}

fingers_rig = {
		"move_wait_ms"			: 50
}

servo_rig = {
		"homing_max_track"		: RAIL_STEPPER_STEPS
	,	"homing_prudent_track"	: WAGON_2_STEPPER
	,	"homing_vel"			: 1000
	,	"homing_margin"			: 300
	,	"homing_reengage_ms"	: 200
	,	"stepper_2_encoder"		: STEPPER_2_ENCODER
	,	"encoder_update_ms"		: 25
}

keyboard = {
		"start"					: name_2_note("F3")
	,	"end"					: name_2_note("C6")
}

wagon = {
		"structure"				: [[0, 2], [4, 6], [8, 10], [12, 14], [1, 3], [5, 7], [9, 11]]
	,	"valid_positions"		: RAIL_WAGON_INTERVALS + 1
	,	"wagon_2_stepper"		: WAGON_2_STEPPER
}

keystra = {
		"notes_bonus"			: 10
	,	"skid_bonus"			: 3
	,	"move_penalty"			: 1
	,	"time_penalty"			: 1
}

