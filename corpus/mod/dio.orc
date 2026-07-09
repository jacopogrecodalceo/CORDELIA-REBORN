
    opcode cordelia_diode_ladder, a, aJJ
    ain, kfreq, kq xin

if kfreq == -1 then
    kfreq = ntof("4B")
endif

if kq == -1 then
    kq = .5
endif

kfreq_var   = (kfreq*11/10)-kfreq
kfreq       = kfreq + jitter(1, gkBEATf/8, gkBEATf)*kfreq_var

; core
isaturation init 1.25
inlp        init 1
aout        diode_ladder ain, kfreq, kq*17, inlp, isaturation

kdyn_comp   pow (kfreq / giNYQUIST), -0.15
aout        *= kdyn_comp
;aout	    balance2 aout, ain

    xout aout
    endop


