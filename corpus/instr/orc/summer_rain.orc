/*
360602 and 360603
summer_rain is an instrument coming from an improvisation I made at the Fabrique de la danse in Paris with dancers.
A recordin' of a cycling synth become the landascape behind a summer in Paris after a hot days — grey days are on.
*/

gSsummer_rain_path init "seq/summer_rain"
gSsunday_file	init "summer_rain-"
gisummer_rain_max init 23

	instr summer_rain
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		ienv init .005
		aenv cossegr 0, ienv, 1, idur-(ienv*2), 1, ienv, 0
	)

iheart      i chnget("heart")
inum        floor 1+(iheart*gisummer_rain_max)

Spath       sprintf "%s/%s%s.wav", gSsummer_rain_path, gSsunday_file, pad(inum, 2)

/* -------------------------------------------------------------------------- */
/*                                   source                                   */
/* -------------------------------------------------------------------------- */
a1          vco2 idyn/4, icps
a2          vco2 idyn/4, icps+random:i(-.05, .05)
aosc        sum a1, a2

kph_line    = floor(abs(lfo(idur*4, 1/idur/2))) / 2
aosc        phaser1 aosc, icps*kph_line, 16, .75+iheart/5

/* -------------------------------------------------------------------------- */
/*                                   diskin                                   */
/* -------------------------------------------------------------------------- */
istart      init iheart * filelen(Spath)
adisk       diskin Spath, random:i(.95, 1.05), 1, istart
adisk_hpf   skf adisk, a(4500+jitter:k(500, gkBEATf/8, gkBEATf)), 1.5+(iheart/2), 1

across      cross2 aosc, adisk+adisk_hpf*4, 2048, 2, gihanning, cosseg:k(0, idur/2, 1, idur/2, 0)
ahpf        skf across, a(4500+jitter:k(500, gkBEATf/8, gkBEATf)), 1.5+(iheart/2), 1

aout        sum across/2, ahpf

	$CORDELIA_OUT
	endin
