; CORDELIA INIT: p1=i(gkBEATs)/4*6, p2=.5, 4

    opcode cordelia_delay_array, a, akki
    setksmps 1
    ain, kdel_time, kfb, instances xin

ain         init 0
adel_tap    init 0

idel_buf    init 10 ; idlt -- requested delay time in seconds

adel_dump   delayr idel_buf
adel_tap    deltap kdel_time
            delayw ain + (adel_tap * kfb)

aout    = adel_tap;, -1, 1

if instances > 1 then
    aout += cordelia_delay_array(aout, kdel_time + .15*instances + random:i(-1/12, 1/12), kfb/instances, instances-1)/4
endif

    xout aout
    
    endop
