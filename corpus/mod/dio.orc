; CORDELIA INIT: p1=ntof("4B"), p2=.5

    opcode cordelia_diode_ladder, a, akk
    ain, kfreq, kq xin

kfreq_var   = (kfreq*11/10)-kfreq
kfreq       = kfreq + jitter(1, gkBEATf/8, gkBEATf)*kfreq_var

; core
isaturation init 1.25
inlp        init 1
aout        diode_ladder ain, kfreq, kq*15, inlp, isaturation

kdyn_comp   pow (kfreq / giNYQUIST), -0.15
aout        *= kdyn_comp

    xout aout
    endop


