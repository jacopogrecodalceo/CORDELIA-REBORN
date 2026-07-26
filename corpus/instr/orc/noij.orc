ginoij_div init $M_PI_2/10

	instr noij
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	iatk random .15, .05
	while iatk > idur/8 do
		iatk /= 2
	od
	$CORDELIA_ENV(
		aenv cossegr 0, iatk, 1, idur/2, .5, idur/2, .35, irel, 0
	)

;STEREO "CHORUS" ENRICHMENT USING JITTER
kjit_chorus		jitter cosseg(5, idur, .75), 1.5, 3.5

adev1	init 0
adev2	init 0
;MODULATORS
if ienv == 0 then
	adev1	cossegr 0, .005, 1, idur/4, .5, idur/4, .35, irel, 0
	adev2	cossegr 0, .005, 1, idur/6, .5, idur/6, .35, irel, 0
else
	adev1 cordelia_envgen ienv, idur/2, irel
	adev2 cordelia_envgen ienv, idur/3, irel
endif

kpeak_dev1		= idyn * (2+jitter(.05, 1/idur, 4/idur)) * ginoij_div
amodulator1		oscil3 kpeak_dev1*adev1, icps * 5, gisine

kpeak_dev2		= idyn * cosseg(3, idur, 5+random(-.05, .05)) * ginoij_div
amodulator2		oscil3 kpeak_dev2*adev2, icps * 2, gitri

avib1				= lfo(icps/35, icps/250)*expsegr(1/512, idur, 1, irel, random(1, 2))

acarrier			phasor	portk(icps + kjit_chorus, idur/96, 20)+avib1
acarrier			table3	acarrier + amodulator1 + amodulator2, gisaw, 1, 0, 1
aosc				= acarrier * idyn

alpf				bqrez	aosc, icps+(icps*(16*idyn)), .75+random(-.05, .05)
aout				balance2 alpf, aosc

	$CORDELIA_OUT
	endin
