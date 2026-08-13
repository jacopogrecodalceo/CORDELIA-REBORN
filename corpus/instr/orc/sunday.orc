
gSsunday_path 	init "seq/sunday"
gSsunday_file	init "sunday-"
gisunday_max	init 171
gisunday_idx	init 0

	instr sunday
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		ienv init .005
		aenv cossegr 0, ienv, 1, idur-(ienv*2), 1, ienv, 0
	)

iphase		i chnget("heart") * gkdiv
Spath			sprintf "%s/%s%s.wav", gSsunday_path, gSsunday_file, pad((gisunday_idx%gisunday_max)+1)
ilen			init filelen(Spath)-idur

istart		init ((iphase/(icps%96))%1)*ilen

; it's mono..
aout				diskin Spath, 1+random:i(-.005, .005), istart
aout				*= idyn

	gisunday_idx += 1

	$CORDELIA_OUT
	endin

