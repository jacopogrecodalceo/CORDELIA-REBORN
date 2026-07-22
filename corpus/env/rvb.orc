;	LIKEArvb
;	a 6-points function from linear segments
girvb_atk		init sr * .005
girvb_dur		init gienvdur - girvb_atk
girvb_int		init 32
girvb_intdec		init 1
girvb_dec		init girvb_intdec / girvb_int

girvb_sus1		init .15
girvb_intrel1		init 3
girvb_rel1		init girvb_intrel1 / girvb_int

girvb_sus2		init .05
girvb_intrel2		init girvb_int-girvb_intdec-girvb_intrel1
girvb_rel2		init girvb_intrel2 / girvb_int

;-----------------------
girvb		ftgen	0, 0, gienvdur, 7, 0, girvb_atk, 1, girvb_dur*girvb_dec, girvb_sus1, girvb_dur*girvb_rel1, girvb_sus2, girvb_dur*girvb_rel2, 0
;-----------------------
