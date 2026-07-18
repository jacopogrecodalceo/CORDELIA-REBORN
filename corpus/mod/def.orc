; CORDELIA INIT: p1=i(gkBEATs)*1/9, p2=.5, 4

	opcode cordelia_delay_phaser, a, akki
	setksmps 1
	ain, ktime, kfb, instances xin

ain         init 0
adel_tap    init 0

idel_buf    init 10 ; idlt -- requested delay time in seconds

adel_dump   delayr idel_buf
adel_tap    deltap ktime
				delayw ain + (adel_tap * kfb)

aout    = adel_tap

if instances > 1 then
	aout += cordelia_delay_phaser(aout, ktime + ktime*instances + random:i(-1/12, 1/12), kfb/(5-instances), instances-1)/4
endif

kfreq samphold oscili(1, 1/ktime, giasine)*1/ktime, phasor(1/ktime + random:i(-1/12, 1/12))
aout	phaser1 aout*(1-kfb), kfreq, 48+instances*4, kfb

	xout aout
	
	endop





