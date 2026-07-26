; N.B. Path without the last slash / !!!
#define loki_path 			#"/Users/j/Documents/PROJECTs/CORDELIA/_INSTR/sonvs/samps-loki"#
#define loki_release_atk	#.005#

	instr loki
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		aenv cossegr 1, idur, .95, irel, 0
	)

; IF RANGE DYN
if idyn < ampdbfs(-13) then
	Sdyn init "0-30"
elseif  idyn < ampdbfs(-11) then
	Sdyn init "31-60"
elseif  idyn < ampdbfs(-9) then
	Sdyn init "61-90"
elseif	idyn < ampdbfs(-5) then
	Sdyn init "91-110"
else
	Sdyn init "111-127"
endif


inote = 69 + 12 * log2(icps / A4)
; IF IN RANGE:
	if inote <= 11 && inote > 0 then
			irootnote = 9
			Snote_name init "A-1"
	elseif inote <= 14 && inote > 11 then
			irootnote = 12
			Snote_name init "C0"
	elseif inote <= 17 && inote > 14 then
			irootnote = 15
			Snote_name init "Eb0"
	elseif inote <= 20 && inote > 17 then
			irootnote = 18
			Snote_name init "Gb0"
	elseif inote <= 23 && inote > 20 then
			irootnote = 21
			Snote_name init "A0"
	elseif inote <= 26 && inote > 23 then
			irootnote = 24
			Snote_name init "C1"
	elseif inote <= 29 && inote > 26 then
			irootnote = 27
			Snote_name init "Eb1"
	elseif inote <= 32 && inote > 29 then
			irootnote = 30
			Snote_name init "Gb1"
	elseif inote <= 35 && inote > 32 then
			irootnote = 33
			Snote_name init "A1"
	elseif inote <= 38 && inote > 35 then
			irootnote = 36
			Snote_name init "C2"
	elseif inote <= 41 && inote > 38 then
			irootnote = 39
			Snote_name init "Eb2"
	elseif inote <= 44 && inote > 41 then
			irootnote = 42
			Snote_name init "Gb2"
	elseif inote <= 47 && inote > 44 then
			irootnote = 45
			Snote_name init "A2"
	elseif inote <= 50 && inote > 47 then
			irootnote = 48
			Snote_name init "C3"
	elseif inote <= 53 && inote > 50 then
			irootnote = 51
			Snote_name init "Eb3"
	elseif inote <= 56 && inote > 53 then
			irootnote = 54
			Snote_name init "Gb3"
	elseif inote <= 59 && inote > 56 then
			irootnote = 57
			Snote_name init "A3"
	elseif inote <= 62 && inote > 59 then
			irootnote = 60
			Snote_name init "C4"
	elseif inote <= 65 && inote > 62 then
			irootnote = 63
			Snote_name init "Eb4"
	elseif inote <= 68 && inote > 65 then
			irootnote = 66
			Snote_name init "Gb4"
	elseif inote <= 71 && inote > 68 then
			irootnote = 69
			Snote_name init "A4"
	elseif inote <= 74 && inote > 71 then
			irootnote = 72
			Snote_name init "C5"
	elseif inote <= 77 && inote > 74 then
			irootnote = 75
			Snote_name init "Eb5"
	elseif inote <= 80 && inote > 77 then
			irootnote = 78
			Snote_name init "Gb5"
	elseif inote <= 83 && inote > 80 then
			irootnote = 81
			Snote_name init "A5"
	elseif inote <= 86 && inote > 83 then
			irootnote = 84
			Snote_name init "C6"
	elseif inote <= 89 && inote > 86 then
			irootnote = 87
			Snote_name init "Eb6"
	elseif inote <= 92 && inote > 89 then
			irootnote = 90
			Snote_name init "Gb6"
	elseif inote <= 127 && inote > 92 then
			irootnote = 96
			Snote_name init "C7"
	endif

irootnote2cps = A4 * pow(2, (irootnote - 69) / 12)
iratio = icps / irootnote2cps


if (ich % 2) == 0 then
	Smics_lateral[]	fillarray "L", "LKey"
else
	Smics_lateral[]	fillarray "R", "RKey"
endif

imax_RR			init 5
if strcmp(Snote_name, "A2") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "Eb3") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "Eb2") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "Gb2") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "Gb1") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "A3") == 0 then
	imax_RR	init 4
elseif strcmp(Snote_name, "C4") == 0 then
	imax_RR	init 4
endif

index_RR_lateral		init 1 + (floor(icps*idyn) % (imax_RR))

S_RR_lateral			sprintf "RR%i", index_RR_lateral
Spath_lateral			sprintf "%s/FP_%s_%s_%s_%s.wav", $loki_path, Smics_lateral[(floor(icps) % 2)], Snote_name, Sdyn, S_RR_lateral
aout_lateral			diskin Spath_lateral, iratio;, iskiptime/1000

;index_RR_central		init 1 + (floor(icps*idyn*2) % (imax_RR))
;S_RR_central			sprintf "RR%i", index_RR_central
S_RR_central			sprintf "RR%i", floor(random(1, imax_RR))
Spath_central			sprintf "%s/FP_%s_%s_%s_%s.wav", $loki_path, "C", Snote_name, Sdyn, S_RR_central
aout_central			diskin Spath_central, iratio;, iskiptime/1000

idyn_factor				init .65
aout						sum aout_lateral/2, aout_central/2
aout						*= (1-idyn_factor)+idyn*idyn_factor

; FP_RKey_C4_31-60_RR1
; RELEASE
;================================================================
if idur < 5.5 then
	Spath_release sprintf "%s/KeyNoise_RR%i.wav", $loki_path, floor((index_RR_lateral / imax_RR)*7)
	schedule "loki_release", 0, 10, Spath_release, idyn/6, ich, Sinstr_out
endif

index_RR_release		init 1 + (floor(icps*idyn) % 20)

if  idyn < ampdbfs(-7) then
	Spath_release sprintf "%s/release_soft_RR%i.wav", $loki_path, index_RR_release
else
	Spath_release sprintf "%s/release_hard_RR%i.wav", $loki_path, index_RR_release
endif
schedule "loki_release", idur, idur, Spath_release, idyn/8, ich, Sinstr_out
	$CORDELIA_OUT
	endin


	instr loki_release
idur 			init p3
Spath 		init p4
idyn			init p5
ich			init p6
Sinstr_out 	init p7

aenv		cosseg 0, $loki_release_atk, 1, idur-$loki_release_atk*2, 1, $loki_release_atk, 0

ilen 			filelen Spath
if p3 > ilen then
	p3 init ilen
endif


ains[]	diskin Spath, 1+random:i(-.005, .005)
	$CORDELIA_SAMP_OUT

aout 		= ain*idyn

	$CORDELIA_OUT
	endin

