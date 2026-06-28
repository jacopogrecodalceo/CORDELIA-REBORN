;	cls
;	a 3-points function from linear segments
gicls_atk		init sr * .005
gicls_dur		init gienvdur - gicls_atk
gicls_int		init 9
gicls_intdec	init 4
gicls_dec		init gicls_intdec / gicls_int
gicls_sus		init .15
gicls_intrel	init gicls_int-gicls_intdec
gicls_rel		init gicls_intrel / gicls_int
;-----------------------
gicls		ftgen	0, 0, gienvdur, 7, 0, gicls_atk, 1, gicls_dur*gicls_dec, gicls_sus, gicls_dur*gicls_rel, 0
;-----------------------


