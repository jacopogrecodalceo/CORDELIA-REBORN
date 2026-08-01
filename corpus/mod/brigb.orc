
/*
variant of brig
klast-vfco2 from rpr ancient cordelia wisdom
*/

; CORDELIA INIT: p1=.5

	opcode cordelia_brightb, a, ak
	ain, kwet xin

/*
kflg -- compute flag, non-zero values switch on linear prediction analysis replacing filter coefficients, zero switch it off, keeping current filter coefficients.
kprd -- analysis period in samples, determining how often new coefficients are computed.
isiz -- size of lpc input frame in samples.
iord -- linear predictor order.
*/

isize		init 4096
iord		init 96
kprd		init isize

/*
from rpr ancient wisdom:
kcfs[], krms, kerr, kf lpcanal kread, 1, ich, isize, iord, gihanning
*/
kcfs[], krms, kerr, kf lpcanal ain, 1, kprd, isize, iord

karp1		= floor(krms*8)-4
kn_harm 	= kf*powoftwo(karp1)+jitter(1, gkBEATf, gkBEATf/16)
kn_harm	limit kn_harm, 20, 13500


;koct		= krms*4
koct		= powoftwo(floor((krms*2)-1))

kcps1		limit kf*koct, 20, 13500
a1			buzz 1, kcps1, kn_harm, -1

kheart	chnget "heart"
karp2		= floor((kheart*gkdiv*4)%8)-4
kcps2		= kcps1*powoftwo(karp2)
a2			vco2 4*(krms*kerr), kcps2

asum		sum a1, a2
asum		*= .5+oscil3:a(.5, 9+jitter(1/24, gkBEATf, gkBEATf/16), giasquare)
aout		allpole asum*krms*kerr*(2-(kwet)), kcfs
/*
icomp1 -- compression ratio for upper zone.
icomp2 -- compression ratio for lower zone
irtime -- gain rise time in seconds. Time over which the gain factor is allowed to raise of one unit.
iftime -- gain fall time in seconds. Time over which the gain factor is allowed to decrease of one unit.
kthreshold -- level of input signal which acts as the threshold. Can be changed at k-time (e.g. for ducking)
Note on the compression factors: A compression ratio of one leaves the sound unchanged. Setting the ratio to a value smaller than one will compress the signal (reduce its volume) while setting the ratio to a value greater than one will expand the signal (augment its volume).
aout 		dam aout, .25, .75, .125, .005, .15
*/
ain		delay ain, isize/sr, isize/sr
aout		= ain*(1-kwet) + aout*kwet

	xout aout
	endop


