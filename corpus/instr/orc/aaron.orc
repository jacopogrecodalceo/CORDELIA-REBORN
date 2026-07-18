;a sweet sound with a tiny, harsh attack

gkaaron_mod	init 1 ;mod parameter for aaron instr
gkaaron_indx	init 3 ;index parameter for aaron instr
gkaaron_detune	init 0 ;detune parameter for aaron instr
giaaron_atk		init .0125

	instr aaron_instr_1
	$CORDELIA_QUALITIEs(aaron)
	$CORDELIA_RELEASE

indx		init i(gkaaron_indx)
idetune 	init i(gkaaron_detune)

ivib_div	random 4, 8

kcar 		= 1+jitter(1/8, 1/idur, 4/idur)
kndx		expseg indx, idur, .05

kcps		= icps + vibr(expseg(.05, idur, icps/(icps*12)), randomi:k(idur*3, idur*5, icps/(icps*12)), gisine)

adyn		= abs(lfo:a(idyn, cosseg(random:i(idur*.35, idur*.95)/ivib_div, idur, random:i(idur*.75, idur*3.5)/ivib_div)))
aout		foscili adyn, kcps+randomi:k(-.05, .05, 1/idur, 2, 0), kcar, gkaaron_mod+randomi:k(-.0015, .0015, 1/idur, 2, 0), kndx+randomi:k(-.05, .05, 1/idur), gisine

	$CORDELIA_END_INSTR


	instr aaron_instr_2
	$CORDELIA_QUALITIEs(aaron)
	$CORDELIA_RELEASE

ipanfreq	init random:i(-.95, .95)

aout		repluck random:i(.015, .35), idyn, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3:a(1, random:i(.05, .25),  gitri)

aenv	cossegr 0, giaaron_atk, 1, irel, 0
aout	*= aenv

	$CORDELIA_OUT
	endin

	

	instr aaron_instr_3
	$CORDELIA_QUALITIEs(aaron)

ipanfreq	= random:i(-.95, .95)

aout	repluck random:i(.015, .35), $dyn_var, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3:a(1, random:i(.05, .25), gisine)

aenv	cosseg 0, giaaron_atk, 1, idur/5, 0
aout	*= aenv

	$CORDELIA_OUT
	endin


	

	instr aaron_instr_4
	$CORDELIA_QUALITIEs(aaron)

kcps		= icps + vibr(expseg(.05, idur, icps/(icps*12)), randomi:k(idur*3, idur*5, icps/(icps*12)), gisine)
anoi		fractalnoise random:i(.05, .75), random:i(.05, .75)
ares		resonx	anoi, kcps, icps/5
aout		balance2 ares, anoi

aenv		cosseg 0, giaaron_atk, idyn, idur, 0
adyn		= abs(lfo:a(idyn, cosseg(random:i(idur*.5, idur*.75)/2, idur, random:i(idur*.75, idur*3.5)/2)))
aout		*= adyn * aenv

	$CORDELIA_OUT
	endin

	

;---

	instr aaron
	$CORDELIA_QUALITIEs

Sinstr 	init "aaron"

indx		init i(gkaaron_indx)
idetune 	init i(gkaaron_detune)

	schedule sprintf("%s_instr_1", Sinstr), 0,	idur, idyn,		ienv, icps, 					ich, Sinstr_out

	schedule sprintf("%s_instr_2", Sinstr), 0,	idur, idyn/6,	ienv, icps+idetune, 			ich, Sinstr_out
	schedule sprintf("%s_instr_3", Sinstr), 0,	idur, idyn/6,	ienv, icps+idetune, 			ich, Sinstr_out

	schedule sprintf("%s_instr_2", Sinstr), 0,	idur, idyn/3,	ienv, icps*2.11+idetune, 	ich, Sinstr_out
	schedule sprintf("%s_instr_3", Sinstr), 0,	idur, idyn/3,	ienv, icps*1.97+idetune, 	ich, Sinstr_out

	schedule sprintf("%s_instr_4", Sinstr), 0,	idur, idyn/5,	ienv, icps, 					ich, Sinstr_out

	turnoff
	endin

	
