/* 
~idi di luglio 2026
coming from another synth icreated working on cordelia reborn
è rimasto nel cuore, come argilla secca sugli scogli
*/

	$CORDELIA_BEGIN_INSTR(tiny)

irel init idur+random(.005, -.005)
	xtratim irel

anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

aenv_indx	linsegr 1, idur, random(1/8, 1/24), irel, 0
aenv 			table3 aenv_indx, ienv, 1
aout 			*= aenv

	$CORDELIA_OUT
	endin
