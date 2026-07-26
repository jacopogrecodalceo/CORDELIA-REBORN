	instr repuck
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		aenv cossegr 1, idur, .75, irel, 0
	)

ipanfreq		init random:i(-.25, .25)

aout			repluck random:i(.015, .35), idyn, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3(1, random:i(.05, .25),  gisine)

aout			buthp aout, limit(icps/2, 20, ntof("5B"))

	$CORDELIA_OUT
	endin
