from monica.duty import Chord, Duty


SKID_NONE = 0
SKID_OCTA = 7


def song1():
	chords: list[Chord] = [
			Chord.from_text("B3_D4_F#4")
		,	Chord.from_text("G3_B3_D4")
		,	Chord.from_text("D3_F#3_A3")
		,	Chord.from_text("A3_C#4_E4")
		,	Chord.from_text("B3_D4_F#4")
		,	Chord.from_text("G3_B3_D4")
		,	Chord.from_text("D3_F#3_A3")
		,	Chord.from_text("A3_C#4_E4")
		,	Chord.from_text("A5")
	]
	return [Duty(i * 2175, 1800, chords[i]) for i in range(len(chords))]

def song2():
	return [Duty(0, 1000, Chord.from_text("F3"))]

def song3():
	return [Duty(0, 1000, Chord.from_text("C4"))]

def song4():
	return [Duty(0, 1000, Chord.from_text("C6"))]

def song5():
	return [
			Duty(0, 1000, Chord.from_text("F3"))
		,	Duty(2000, 1000, Chord.from_text("C6"))
	]

def song6():
	chords: list[Chord] = [
			Chord.from_text("F3")
		,	Chord.from_text("C6")
		,	Chord.from_text("F3")
		,	Chord.from_text("C6")
		,	Chord.from_text("C5")
	]
	return [Duty(i * 2000, 1000, chords[i]) for i in range(len(chords))]
 
def por_lo_que_yo_te_quiero():
	tempo = 1500
	base_wait = 150
	progression: list = [
			("D4_F4_A4"		, tempo		, 0)
		,	("D4_F4_A#3"	, tempo		, 0)
		,	("C4_E4_G4"		, tempo		, 100)
		,	("C5_F4_A4"		, tempo		, 100)
		,	("D4_G4_A#4"	, tempo		, 50)
		,	("D5_F4_A4"		, tempo		, 100)
		,	("D4_E4_G#4_B4"	, tempo		, 0)
		,	("C#4_E4_G4_A4"	, tempo		, 0)

		,	("D4_F4_A4"		, tempo		, 100)
		,	("D4_F4_A#4"	, tempo		, 100)
		,	("C4_E4_G3"		, tempo		, 0)
		,	("C4_F4_A3"		, tempo		, 100)
		,	("D4_G4_A#3"	, tempo		, 100)
		,	("D4_F4_A4"		, tempo		, 100)
		,	("D4_E4_G#4_B4"	, 750		, 0)
		,	("E4_A4_C#5"	, 750		, 0)
		,	("D4_F4_A4"		, tempo		, 0)
	]
	
	duties = []
	start_time = 0
	for i in range(len(progression)):
		post_wait = base_wait + progression[i][2]
		duties.append(Duty(start_time, progression[i][1] - post_wait, Chord.from_text(progression[i][0])))
		start_time += progression[i][1]
	
	return duties

def monica_showcase():
	"""
	New showcase song that demonstrates cart movement and musical variety
	Features: single notes, chords, different positions, rhythmic patterns
	"""
	from monica.duty import Chord, Duty
	
	# Musical progression with timing and position changes
	# Format: (chord_text, start_time, duration, description)
	musical_sequence = [
		# Opening - Low register exploration (positions 0-2)
		("F3", 0, 800, "Single low note - start position"),
		(None, 800, 200, "Breath"),
		("G3_B3", 1000, 1000, "Simple chord"),
		(None, 2000, 300, "Move to next position"),
		
		("A3", 2300, 600, "Single note higher"),
		("A3_C4_E4", 2900, 1200, "Major chord"),
		(None, 4100, 400, "Breath and move"),
		
		# Middle register - more complex (positions 3-5)
		("C4_E4_G4", 4500, 800, "C major chord"),
		("D4", 5300, 400, "Single note"),
		("E4", 5700, 400, "Single note"),
		("F4_A4_C5", 6100, 1000, "F major chord"),
		(None, 7100, 300, "Breath"),
		
		# Rhythmic section - quick changes (positions 6-8)
		("G4", 7400, 300, "Quick single"),
		("A4", 7700, 300, "Quick single"),
		("B4", 8000, 300, "Quick single"),
		("C5", 8300, 600, "Sustained single"),
		(None, 8900, 200, "Quick breath"),
		
		("G4_B4_D5", 9100, 800, "G major chord"),
		("A4_C5_E5", 9900, 800, "A minor chord"),
		(None, 10700, 400, "Move to high register"),
		
		# High register showcase (positions 9-11)
		("B4_D5_F5", 11100, 1000, "High chord"),
		("C5", 12100, 500, "High single note"),
		("D5", 12600, 500, "Higher single"),
		("E5", 13100, 800, "Even higher"),
		(None, 13900, 300, "Final breath"),
		
		# Grand finale - full range sweep
		("F5_A5_C6", 14200, 1200, "Highest chord"),
		("C6", 15400, 1000, "Highest single note"),
		(None, 16400, 500, "Final pause"),
		
		# Ending - return to middle
		("C4_E4_G4_C5", 16900, 1500, "Final chord - wide voicing"),
	]
	
	# Convert to Duty objects
	duties = []
	for chord_text, start_time, duration, description in musical_sequence:
		if chord_text is None:
			# Silence/breath
			duty = Duty.silence(start_time, duration)
		else:
			# Musical content
			chord = Chord.from_text(chord_text)
			duty = Duty(start_time, duration, chord)
		duties.append(duty)
		print(f"  {start_time:5d}ms: {description}")
	
	print(f"Monica showcase song created: {len(duties)} duties, {duties[-1].end_ms/1000:.1f} seconds")
	return duties

