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

