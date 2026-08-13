
/*
MAKE IT ELASTIC
klast-vfco2 from rpr ancient cordelia wisdom
*/

; CORDELIA INIT: p1=.95

	opcode cordelia_bright_eks2, a, ak
	ain, kwet xin

/*
kflg -- compute flag, non-zero values switch on linear prediction analysis replacing filter coefficients, zero switch it off, keeping current filter coefficients.
kprd -- analysis period in samples, determining how often new coefficients are computed.
isiz -- size of lpc input frame in samples.
iord -- linear predictor order.
*/

isize		init 8192
iord		init 256
kprd		init isize/8
kport   	abs jitter(1/12, 1/12, 1)

/*
from rpr ancient wisdom:
kcfs[], krms, kerr, kf lpcanal kread, 1, ich, isize, iord, gihanning
*/
kflag 			init 1
/* kprd_count	 	init 0
if kprd_count % 16 == 0 then
	kflag = 1
else
	kflag = 0
endif */

kcfs[], krms, kerr, kf lpcanal ain, kflag, kprd, isize, iord

kf_temp		init 0
kf_last		init 0

if kf != kf_temp then
	kf_last = kf_temp
endif
kf_temp = kf

kjit_ph jitter .05, gkBEATf/12, gkBEATf/24
kn_harm = (sr/2)/kf*oscil3(1, 3+kjit_ph+krms*12, giasine)

a1			buzz 1, portk(kf, kport), kn_harm, -1
a2			vco2 4*(krms*kerr), kf_last

asum		sum a1, a2
asum		= asum*krms*kerr
adel		flanger asum*oscil3(1, .75+((1-krms)*24)+kjit_ph, giasquare), a((isize/sr)/1000*(3+jitter(.05, gkBEATf/12, gkBEATf/24))), .5
aout		allpole (asum+adel)*(2-(kwet))*kwet, kcfs
;askf		skf aout, 4500+jitter:k(350, gkBEATf/8, gkBEATf), krms*2.75, 1.25
askf 		K35_hpf aout, 4500+jitter:k(350, gkBEATf/8, gkBEATf), krms*8.75, 1, 1.24

ain		delay ain, isize/sr, isize/sr
aout		sum ain*(1-kwet), aout, askf*2

	xout aout
;	kprd_count += 1
	endop


