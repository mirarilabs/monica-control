from utils.music.note_frecuencies_int import *


TEMPO_BPM = 150.0

# Note durations
fn = 60.0/TEMPO_BPM;
hn = fn/2;
qn = fn/4;
en = fn/8;
sn = fn/16;


startup_tune = [
	(C4, hn),
	(G4, qn),
	(C5, hn)
]

death_tune = [
	(A3, fn + qn),
	(A3, fn),
	(A3, qn),
	(A3, fn + qn),
	(C3, fn),
	(B2, qn),
	(B2, fn),
	(A3, qn),
	(A3, fn),
	(C3, qn),
	(A3, fn + qn)
]

we_are_number_one = [
	(F5 , fn + hn),
	(C6 , hn),
	(B5 , qn),
	(C6 , qn),
	(B5 , qn),
	(C6 , qn),
	(B5 , hn),
	(C6 , hn),
	(Gs5, fn),
	(F5 , fn + hn),
	(F5 , hn),
	(Gs5, hn),
	(C6 , hn),
	(Cs6, fn),
	(Gs5, fn),
	(Cs6, fn),
	(Ds6, fn),
	(C6 , hn),
	(Cs6, hn),
	(C6 , hn),
	(Cs6, hn),
	(C6 , fn)
]

full_range_tune = [
	(A0, qn), (As0, qn), (B0, qn), (C1, qn), (Cs1, qn), (D1, qn), (Ds1, qn), (E1, qn), (F1, qn), (Fs1, qn), (G1, qn), (Gs1, qn),
	(A1, qn), (As1, qn), (B1, qn), (C2, qn), (Cs2, qn), (D2, qn), (Ds2, qn), (E2, qn), (F2, qn), (Fs2, qn), (G2, qn), (Gs2, qn),
	(A2, qn), (As2, qn), (B2, qn), (C3, qn), (Cs3, qn), (D3, qn), (Ds3, qn), (E3, qn), (F3, qn), (Fs3, qn), (G3, qn), (Gs3, qn),
	(A3, qn), (As3, qn), (B3, qn), (C4, qn), (Cs4, qn), (D4, qn), (Ds4, qn), (E4, qn), (F4, qn), (Fs4, qn), (G4, qn), (Gs4, qn),
	(A4, qn), (As4, qn), (B4, qn), (C5, qn), (Cs5, qn), (D5, qn), (Ds5, qn), (E5, qn), (F5, qn), (Fs5, qn), (G5, qn), (Gs5, qn),
	(A5, qn), (As5, qn), (B5, qn), (C6, qn), (Cs6, qn), (D6, qn), (Ds6, qn), (E6, qn), (F6, qn), (Fs6, qn), (G6, qn), (Gs6, qn),
	(A6, qn), (As6, qn), (B6, qn), (C7, qn), (Cs7, qn), (D7, qn), (Ds7, qn), (E7, qn), (F7, qn), (Fs7, qn), (G7, qn), (Gs7, qn),
	(A7, qn), (As7, qn), (B7, qn), (C8, qn)
]

