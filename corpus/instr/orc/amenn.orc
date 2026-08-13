
gSamenn_path 	init "seq/amenn"
gSamenn_file	init "amenn-"
giamenn_max	init 19

	instr amenn
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		ienv init .005
		aenv cossegr 0, ienv, 1, idur-(ienv*2), 1, ienv, 0
	)

iheart		i chnget("heart")
iphase		i iheart * gkdiv
Spath			sprintf "%s/%s%s.wav", gSamenn_path, gSamenn_file, pad((iheart*giamenn_max)+1, 2)
ilen			init filelen(Spath)-idur

istart		init ((iphase/(icps%96))%1)*ilen

; it's mono..
ains[]	diskin Spath, 1+random:i(-.005, .005)
	$CORDELIA_SAMP_OUT

aout 		= ain*idyn

	$CORDELIA_OUT
	endin

