/*
after bretagne
same as josciln but with acc/dec
*/

; N.B. Path without the last slash / !!!
gSjosciln_path		init "/Users/j/Documents/PROJECTs/CORDELIA/_INSTR/sonvs/samps-joscil"
gijosciln_dyn		init 1
gijosciln_tuning 	init cent(85)
gkjosciln_div 		init 6
gkjosciln_ratio	init 1.05 ; >1 = decelerating, <1 = accelerating
#define josciln_max #48#

	instr josciln
Sinstr init "josciln_instr"
	$CORDELIA_QUALITIEs

inote = 69 + 12 * log2(icps / A4)
; josciln-01  to 21

irootnote2cps = A4 * pow(2, (inote - 69) / 12)
iratio = icps*gijosciln_tuning / irootnote2cps

if inote < 10 then
	Snote sprintf "0%i", inote
else
	Snote sprintf "%i", inote
endif

Spath 			sprintf "%s/joscil-%s.wav", gSjosciln_path, Snote
ilen 				init filelen(Spath)/iratio
istart 			init (1-idyn)*ilen/4

isegment 		i gkBEATs
idiv				i gkjosciln_div
iratio_grow		i gkjosciln_ratio 

isegment 		divz isegment, idiv, 0

ionset			init 0
indx				init 0
isegment_cur	init isegment
ionset_last		init -1
while ionset < idur && indx < $josciln_max && isegment > 0 do
	if abs(ionset - ionset_last) > .005 then
		schedule Sinstr, ionset+random:i(0, .005), isegment, idyn*pow(.95, indx), ienv, iratio, ich, Sinstr_out, Spath, istart
		ionset_last = ionset
	endif
	ionset += isegment_cur
	isegment_cur *= iratio_grow
	indx += 1
od
	turnoff
	endin

	instr josciln_instr
	$CORDELIA_QUALITIEs
	$CORDELIA_RELEASE
	$CORDELIA_ENV(
		aenv cossegr 0, .005, 1, idur/2, .5, idur/2, .35, irel, 0
	)
	Spath		init p9
	istart	init p10

	ains[] diskin Spath, icps, istart + random:i(0, .005)

	$CORDELIA_DISKIN_CHs

	aout = ain
	aout diode_ladder aout, limit(20$k-((1-idyn)*19.5$k), 20, 20$k), random:i(.25, .5)
	aout *= gijosciln_dyn

	$CORDELIA_OUT
	endin


