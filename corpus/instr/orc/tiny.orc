/* 
~idi di luglio 2026
coming from another synth icreated working on cordelia reborn
è rimasto nel cuore, come argilla secca sugli scogli
*/

	instr tiny
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		aenv cossegr 0, .005, 1, idur/2, .5, idur/2, .35, irel, 0
	)

inoi_type 	random 0, 2
anoi 			fractalnoise 1/12, inoi_type
aosc 			oscil3 1/2, icps
avco 			vco2 1/64, icps

anoi_env		cosseg 1, .005+random(.0095, .005), 0
aout 			sum aosc, anoi*anoi_env, avco

aout 			*= idyn
avib			= .5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005))
aout 			= aout * avib

	$CORDELIA_OUT
	endin
