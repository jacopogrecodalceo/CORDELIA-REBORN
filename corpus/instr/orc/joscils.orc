/*
after bretagne, i wanted some instrument that repeat themselves
so let's go
*/

; N.B. Path without the last slash / !!!
gSjoscils_path		init "/Users/j/Documents/PROJECTs/CORDELIA/_INSTR/sonvs/samps-joscil"
gijoscils_dyn		init 1
gijoscils_tuning 	init cent(85)
gkjoscils_div 		init 6
#define joscils_max #48#

	instr joscils
Sinstr init "joscils_instr"
	$CORDELIA_QUALITIEs

inote = 69 + 12 * log2(icps / A4)
; joscils-01  to 21

irootnote2cps = A4 * pow(2, (inote - 69) / 12)
iratio = icps*gijoscils_tuning / irootnote2cps

if inote < 10 then
	Snote sprintf "0%i", inote
else
	Snote sprintf "%i", inote
endif

Spath 	sprintf "%s/joscil-%s.wav", gSjoscils_path, Snote
ilen 		init filelen(Spath)/iratio

isegment i gkBEATs
idiv		i gkjoscils_div

isegment divz isegment, idiv, 0
istart init ((1-idyn)*ilen)/3

ionset	init 0
indx		init 0
ionset_last		init -1
while ionset < idur && indx < $joscils_max && isegment > 0 do
	ionset init isegment*indx
	if abs(ionset - ionset_last) > .005 then
		schedule Sinstr, ionset+random:i(0, .005), isegment, idyn*pow(.95, indx), ienv, iratio, ich, Sinstr_out, Spath, istart
		ionset_last = ionset
	endif
	indx += 1
od
	turnoff
	endin

	instr joscils_instr
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
	aout *= gijoscils_dyn

	$CORDELIA_OUT
	endin


