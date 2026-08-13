; CORDELIA INIT: p1=ntof("4B"), p2=.5

/*
playing the name of see as sea. and then imagine that god can see throught a ray of light
that's where dio_sea comes
*/


    opcode cordelia_diode_ladder_sea, a, akk
    ain, kfreq, kq xin

kfreq_var   = (kfreq*11/10)-kfreq
kfreq       = kfreq + jitter(1, gkBEATf/8, gkBEATf)*kfreq_var

; core
isaturation init 1.25+random(.15, .25)
inlp        init 1
alpf        diode_ladder ain, kfreq, kq*15, inlp, isaturation



; RESON
ilow		init 3
ihigh		init 13
itime		init i(gkBEATs)/9
idbthresh	init 5
koct, kdyn_	pitch ain, itime, ilow, ihigh, idbthresh
kres_cps    = cpsoct(koct)

asea        resonx ain, kres_cps*4, kfreq/4, 4, 2
asea        buthp asea/powoftwo(13), 20

kdyn_comp   pow (kfreq / giNYQUIST), -0.45
aout        sum asea, alpf*kdyn_comp

    xout aout
    endop


