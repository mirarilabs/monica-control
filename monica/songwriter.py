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
	# Add volume variations: soft start, building, peak, gentle ending
	volumes = [40, 50, 60, 70, 80, 75, 65, 55, 90]  # Peak on final high note
	return [Duty(i * 2175, 1800, chords[i], volume_percent=volumes[i]) for i in range(len(chords))]

def song2():
	return [Duty(0, 1000, Chord.from_text("F3"), volume_percent=50)]

def song3():
	return [Duty(0, 1000, Chord.from_text("C4"), volume_percent=60)]

def song4():
	return [Duty(0, 1000, Chord.from_text("C6"), volume_percent=70)]

def song5():
	return [
			Duty(0, 1000, Chord.from_text("F3"), volume_percent=40)
		,	Duty(2000, 1000, Chord.from_text("C6"), volume_percent=80)
	]

def song6():
	chords: list[Chord] = [
			Chord.from_text("F3")
		,	Chord.from_text("C6")
		,	Chord.from_text("F3")
		,	Chord.from_text("C6")
		,	Chord.from_text("C5")
	]
	# Volume variations for range test: crescendo pattern
	volumes = [50, 70, 60, 80, 75]
	return [Duty(i * 2000, 1000, chords[i], volume_percent=volumes[i]) for i in range(len(chords))]
 
def por_lo_que_yo_te_quiero():
	tempo = 1500
	base_wait = 150
	# Format: (chord_text, duration, wait, volume_percent)
	progression: list = [
			("D4_F4_A4"		, tempo		, 0, 40)  # Soft start
		,	("D4_F4_A#3"	, tempo		, 0, 45)  # Building
		,	("C4_E4_G4"		, tempo		, 100, 60)  # Crescendo
		,	("C5_F4_A4"		, tempo		, 100, 70)  # Forte
		,	("D4_G4_A#4"	, tempo		, 50, 65)  # Slight decrease
		,	("D5_F4_A4"		, tempo		, 100, 75)  # Building again
		,	("D4_E4_G#4_B4"	, tempo		, 0, 50)  # Softer
		,	("C#4_E4_G4_A4"	, tempo		, 0, 55)  # Gentle

		,	("D4_F4_A4"		, tempo		, 100, 70)  # Return to forte
		,	("D4_F4_A#4"	, tempo		, 100, 75)  # Building
		,	("C4_E4_G3"		, tempo		, 0, 60)  # Lower register, softer
		,	("C4_F4_A3"		, tempo		, 100, 70)  # Building
		,	("D4_G4_A#3"	, tempo		, 100, 80)  # Peak volume
		,	("D4_F4_A4"		, tempo		, 100, 85)  # Fortissimo
		,	("D4_E4_G#4_B4"	, 750		, 0, 70)  # Gentle ending
		,	("E4_A4_C#5"	, 750		, 0, 60)  # Softer
		,	("D4_F4_A4"		, tempo		, 0, 50)  # Final soft chord
	]
	
	duties = []
	start_time = 0
	for i in range(len(progression)):
		post_wait = base_wait + progression[i][2]
		volume_percent = progression[i][3]
		duties.append(Duty(start_time, progression[i][1] - post_wait, Chord.from_text(progression[i][0]), volume_percent=volume_percent))
		start_time += progression[i][1]
	
	return duties

def monica_showcase():
	"""
	New showcase song that demonstrates cart movement and musical variety
	Features: single notes, chords, different positions, rhythmic patterns
	"""
	from monica.duty import Chord, Duty
	
	# Musical progression with timing, position changes, and volume dynamics
	# Format: (chord_text, start_time, duration, volume_percent, description)
	musical_sequence = [
		# Opening - Low register exploration (positions 0-2) - Soft start
		("F3", 0, 800, 30, "Single low note - soft start"),
		(None, 800, 200, None, "Breath"),
		("G3_B3", 1000, 1000, 40, "Simple chord - building"),
		(None, 2000, 300, None, "Move to next position"),
		
		("A3", 2300, 600, 50, "Single note higher - normal volume"),
		("A3_C4_E4", 2900, 1200, 60, "Major chord - crescendo"),
		(None, 4100, 400, None, "Breath and move"),
		
		# Middle register - more complex (positions 3-5) - Building intensity
		("C4_E4_G4", 4500, 800, 70, "C major chord - forte"),
		("D4", 5300, 400, 60, "Single note - mezzo"),
		("E4", 5700, 400, 70, "Single note - forte"),
		("F4_A4_C5", 6100, 1000, 80, "F major chord - fortissimo"),
		(None, 7100, 300, None, "Breath"),
		
		# Rhythmic section - quick changes (positions 6-8) - Dynamic contrast
		("G4", 7400, 300, 50, "Quick single - piano"),
		("A4", 7700, 300, 60, "Quick single - mezzo"),
		("B4", 8000, 300, 70, "Quick single - forte"),
		("C5", 8300, 600, 85, "Sustained single - fortissimo"),
		(None, 8900, 200, None, "Quick breath"),
		
		("G4_B4_D5", 9100, 800, 75, "G major chord - forte"),
		("A4_C5_E5", 9900, 800, 65, "A minor chord - mezzo-forte"),
		(None, 10700, 400, None, "Move to high register"),
		
		# High register showcase (positions 9-11) - Peak intensity
		("B4_D5_F5", 11100, 1000, 90, "High chord - maximum volume"),
		("C5", 12100, 500, 85, "High single note - forte"),
		("D5", 12600, 500, 90, "Higher single - fortissimo"),
		("E5", 13100, 800, 95, "Even higher - peak volume"),
		(None, 13900, 300, None, "Final breath"),
		
		# Grand finale - full range sweep - Climax
		("F5_A5_C6", 14200, 1200, 100, "Highest chord - maximum fortissimo"),
		("C6", 15400, 1000, 95, "Highest single note - sustained"),
		(None, 16400, 500, None, "Final pause"),
		
		# Ending - return to middle - Gentle conclusion
		("C4_E4_G4_C5", 16900, 1500, 70, "Final chord - wide voicing, mezzo-forte"),
	]
	
	# Convert to Duty objects
	duties = []
	for chord_text, start_time, duration, volume_percent, description in musical_sequence:
		if chord_text is None:
			# Silence/breath
			duty = Duty.silence(start_time, duration, volume_percent)
		else:
			# Musical content
			chord = Chord.from_text(chord_text)
			duty = Duty(start_time, duration, chord, volume_percent=volume_percent)
		duties.append(duty)
		volume_str = f" (vol: {volume_percent}%)" if volume_percent is not None else ""
		print(f"  {start_time:5d}ms: {description}{volume_str}")
	
	print(f"Monica showcase song created: {len(duties)} duties, {duties[-1].end_ms/1000:.1f} seconds")
	return duties

