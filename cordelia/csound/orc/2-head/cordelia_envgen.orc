gisotrap_ramp		init 32 ; in samps
gisotrap_seg		init gienvdur-(gisotrap_ramp*2)
;-----------------------
gisotrap		ftgen	0, 0, gienvdur, 7, 0, gisotrap_ramp, 1, gisotrap_seg, 1, gisotrap_ramp, 0

	opcode cordelia_envgen, a, iii
	ienv, idur, irel	xin

ift_num			abs floor(ienv)
iexists 			ftexists ift_num

if iexists != 1 || ift_num == 0 then
	ift_num = gisotrap
	printks "WARNING ENVGEN DOESN'T EXIST\n", 1/2
endif

ift_mod			init	ift_num-ienv
irel_jit			floor random(0, 128)

if	ift_mod == 0 then
	if	ienv > 0 then
		aphase	linsegr 0, idur, gienvdur-irel_jit, irel, gienvdur
	else
		aphase	linsegr gienvdur, idur, irel_jit, irel, 0
	endif

else 

	iatk	abs ift_mod
	if	ienv > 0 then

		
		ires	init 0
		indx	init 0
		until ires==1 do
			ires	table indx, ift_num
			ires 	= round(ires * 1000) / 1000
			indx	+= 1
		od

		ilast	init idur-iatk
		if	iatk<ilast then
			aphase	linsegr 0, iatk, indx, ilast, gienvdur-irel_jit, irel, gienvdur
		else
			aphase	linsegr 0, idur, gienvdur-irel_jit, irel, gienvdur
		endif

	else

		ires	init 0
		indx	init 0
		ilast	init idur-iatk
			
		until ires==1 do
			ires	table indx, ift_num
			ires	= round(ires * 1000) / 1000
			indx	+= 1
		od
		
		if	iatk<ilast then
			aphase	linsegr gienvdur, ilast, indx, iatk, 0
		else
			aphase	linsegr gienvdur, idur, 0
		endif

	endif

endif

	aenv	table3 aphase, ift_num

	xout aenv
	endop


