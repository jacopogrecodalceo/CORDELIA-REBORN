
	opcode cordelia_wow, a, aJ
	ain, kwet xin

if kwet == -1 then
	kwet = 1
endif

imax_del	init 3500

; subtle wow/flutter LFO
idepth1		init 3.5
irate1 		init 1/10
amod1 		oscili idepth1+jitter(1, 1/8, 1/32), irate1

idepth2		init 1.5					
irate2 		init 1/7
amod2 		oscili idepth2+jitter(.5, 1/8, 1/32), irate2

amod 		= amod1 + amod2

awow 		vdelay ain*kwet, 15 + amod*10, imax_del

aout		= ain*(1-kwet)+ awow

	xout aout
	endop

