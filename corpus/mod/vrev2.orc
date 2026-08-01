; CORDELIA INIT: p1=9500, p2=.35, p3=.5


	opcode cordelia_vapor_reverb2, a, akkk
	ain, kfreq_cutoff, kfblvl, kwet xin


a1, a2 reverbsc ain*kwet, K35_hpf(ain, kfreq_cutoff, .75+jitter(.15, gkBEATf/8, gkBEATf/32), 1, 2.5+jitter(1, gkBEATf/8, gkBEATf/32)), kfblvl, kfreq_cutoff

aout	= ain*(1-kwet) + a1 + a2

	xout aout
	endop


