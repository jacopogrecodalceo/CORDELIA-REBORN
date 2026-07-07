;	LIKEAREV
;	a 6-points function from linear segments
girev_atk		init sr * .005
girev_dur		init gienvdur - girev_atk
girev_int		init 32
girev_intdec		init 1
girev_dec		init girev_intdec / girev_int

girev_sus1		init .15
girev_intrel1		init 3
girev_rel1		init girev_intrel1 / girev_int

girev_sus2		init .05
girev_intrel2		init girev_int-girev_intdec-girev_intrel1
girev_rel2		init girev_intrel2 / girev_int

;-----------------------
girev		ftgen	0, 0, gienvdur, 7, 0, girev_atk, 1, girev_dur*girev_dec, girev_sus1, girev_dur*girev_rel1, girev_sus2, girev_dur*girev_rel2, 0
;-----------------------
