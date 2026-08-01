
/*
klast-vfco2 from rpr ancient cordelia wisdom
*/

; CORDELIA INIT: p1=.95

	opcode cordelia_brightq, a, ak
	ain, kwet xin

/*
kflg -- compute flag, non-zero values switch on linear prediction analysis replacing filter coefficients, zero switch it off, keeping current filter coefficients.
kprd -- analysis period in samples, determining how often new coefficients are computed.
isiz -- size of lpc input frame in samples.
iord -- linear predictor order.
*/

isize		init 2048
iord		init 256
kprd		init isize/8
kport   	abs jitter(1/12, 1/12, 1)

/*
from rpr ancient wisdom:
kcfs[], krms, kerr, kf lpcanal kread, 1, ich, isize, iord, gihanning
*/
kcfs[], krms, kerr, kf lpcanal ain, 1, kprd, isize, iord

kf				init 0
kf_temp		init 0
kf_last		init 0

if kf != kf_temp then
	kf_last = kf_temp
endif
kf_temp = kf

kn_harm = (sr/2)/kf

a1			buzz 1, portk(kf, kport), kn_harm, -1
a2			vco2 4*(krms*kerr), kf_last

asum		sum a1, a2
aout		allpole asum*krms*kerr*(4-(kwet)), kcfs

ain		delay ain, isize/sr, isize/sr
aout		= ain*(1-kwet) + aout*kwet

	xout aout
	endop


