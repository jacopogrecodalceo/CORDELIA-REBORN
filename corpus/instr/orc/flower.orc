
gSflower_path 	init "seq/flower"
gSflower_file	init "flower_coloured-"
giflower_max	init 420
giflower_idx	init 0

	instr flower
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		ienv init .005
		aenv cossegr 0, ienv, 1, idur-(ienv*2), 1, ienv, 0
	)

iphase		i chnget("heart") * gkdiv
Spath			sprintf "%s/%s%s.wav", gSflower_path, gSflower_file, pad((giflower_idx%giflower_max)+1, 4)

ilen			init filelen(Spath)
if ilen > idur then 
	ilen -= idur
else
	ilen -= idur
endif

istart		init ((iphase/(icps%64))%1)*ilen

; it's mono..
aout				diskin Spath, 1+random:i(-.005, .005), istart
aout				*= idyn

	giflower_idx += 1

	$CORDELIA_OUT
	endin

