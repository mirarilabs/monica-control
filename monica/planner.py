import monica
from .songwriter import por_lo_que_yo_te_quiero as song


def plan_song():
	s = song()
	print(f"song length: {len(s)}")
	print(s)
	duties, path = monica.keystra.fill_and_explore(s)
	print(f"duties length: {len(duties)}")
	print(f"path length: {len(path)}")
	print(duties)
	print(path)
	return duties, path

def test_all_keys():
	import config
	from monica.duty import Chord, Duty
	valid_positions = config.wagon["valid_positions"]
	chord = Chord.from_text("F3_F#3_G3_G#3_A3_A#3_B3_C4_C#4_D4_D#4_E4_F4_F#4_G4_G#4_A4_A#4_B4_C5_C#5_D5_D#5_E5_F5_F#5_G5_G#5_A5_A#5_B5_C6")
	duties: list[Duty] = []
	path: list[int] = [ 0 ]
	for i in range(valid_positions):
		duties.append(Duty(1000 * (2 * i    ), 1000, chord, 0))
		path.append(i)
		if i + 1 < valid_positions:
			duties.append(Duty(1000 * (2 * i + 1), 1000, None , 0))
			path.append(i + 1)
	return duties, path

def artisanal_chord_progression():
	from monica.duty import Chord, Duty
	times     = [0   , 1800, 2175, 3975, 4350, 6150, 6525, 8325, 8700, 10500, 10875, 12675, 13050, 14850, 15225, 17025, 17400]
	durations = [1800,  375, 1800,  375, 1800,  375, 1800,  375, 1800,   375,  1800,   375,  1800,   375,  1800,   375, 1800 ]
	chords: list[Chord | None] = [
			Chord.from_text("E4_G4_B4")
		,	None
		,	Chord.from_text("C4_E4_G4")
		,	None
		,	Chord.from_text("G4_B4_D5")
		,	None
		,	Chord.from_text("D4_F#4_A4")
		,	None
		,	Chord.from_text("E4_G4_B4")
		,	None
		,	Chord.from_text("C4_E4_G4")
		,	None
		,	Chord.from_text("G4_B4_D5")
		,	None
		,	Chord.from_text("D4_F#4_A4")
		,	None
		,	Chord.from_text("C6")
	]
	duties = [Duty(times[i], durations[i], chords[i], 0) for i in range(len(times))]
	path = [4, 4, 4, 4, 6, 6, 5, 5, 4, 4, 4, 4, 6, 6, 5, 5, 11, 11]
	return duties, path

