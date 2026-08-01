; CORDELIA INIT: p1=9500, p2=.35, p3=.5

	opcode cordelia_vapor_reverb, a, akkk
	ain, kfreq_cutoff, kfblvl, kwet xin


a1, a2 reverbsc ain*kwet, K35_hpf(ain, kfreq_cutoff, .65, 1, 1.5), kfblvl, kfreq_cutoff

aout	= ain*(1-kwet) + a1 + a2

	xout aout
	endop

;END OPCODE

