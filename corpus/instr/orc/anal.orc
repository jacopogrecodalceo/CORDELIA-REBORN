	instr anal
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		aenv cossegr 0, .005, 1, idur/2, .5, idur/2, .35, irel, 0
	)
imode		init 16
inyx		init .25

kpw		abs jitter(1, gkBEATf/4, gkBEATf)
kphs		abs jitter(1, gkBEATf/4, gkBEATf)
kndx		samphold jitter(1, gkBEATf/4, gkBEATf), metro:k(gkBEATf*8)
kvibf		= lfo(icps/100, random:i(2.5, 4.5))

ivibdiv		random 4, 8
kvibd		= lfo(1, cosseg(random:i(idur*.35, idur*.95)/ivibdiv, idur, random:i(idur*.75, idur*3.5)/ivibdiv))*cosseg(1, idur, 0)

ilen		tab_i 0, i(gktuning)
ioff		init 4
itun_len	init ilen - ioff

kcps		tab (abs(kndx)*itun_len)+ioff, i(gktuning)

kcps		= portk(icps * kcps, .025)+kvibf
aout		vco2 idyn*abs(kvibd), kcps, imode, kpw, kphs, inyx

	$CORDELIA_OUT
	endin



