	instr repuck
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE

ipanfreq	init random:i(-.25, .25)

aout		repluck random:i(.015, .35), idyn, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3(1, random:i(.05, .25),  gisine)

aout	buthp aout, icps - icps/12

	$CORDELIA_ENV
	$CORDELIA_OUT
	endin
