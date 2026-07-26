<CsoundSynthesizer>
<CsOptions>
-odac

--sample-rate=48000
--format=24bit
--nchnls=2
--ksmps=64
--0dbfs=1
--m-amps=1
--m-range=1
--m-warnings=0
--m-dB=1
--m-colours=1
--m-benchmarks=0

</CsOptions>
<CsInstruments>
ginchnls init nchnls
gioffch init 0
giINSTR_CLEAR_COUNT init 0
giFTGEN_SIZE init 8192
giTALEA_RESAMPLE_LEN init giFTGEN_SIZE

		gimainclock_ch init 0
		giquarterclock_ch init 0
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/1-MACRO.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/1b-instr-global_var.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/1b-instr-reborn.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/2-GLOBAL_VAR.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/3-FORMAT.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/MACROs-modifiers-limits.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asaw.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asine.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asquare.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/atri.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/saw.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/sine.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/square.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/tri.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/3-window/hamming.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/3-window/hanning.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/cordelia_envgen.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/envgen.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/tie_status.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/1-ORGAN.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/3-SOUL.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/4-ADDONs.orc"






; BEGIN ORC | 05·41pm································································································································
schedule "heart", 0, -1
;       cls
;       a 3-points function from linear segments
gicls_atk               init sr * .005
gicls_dur               init gienvdur - gicls_atk
gicls_int               init 9
gicls_intdec    init 4
gicls_dec               init gicls_intdec / gicls_int
gicls_sus               init .15
gicls_intrel    init gicls_int-gicls_intdec
gicls_rel               init gicls_intrel / gicls_int
;-----------------------
gicls           ftgen   0, 0, gienvdur, 7, 0, gicls_atk, 1, gicls_dur*gicls_dec, gicls_sus, gicls_dur*gicls_rel, 0
;-----------------------



gigol ftgen 0, 0, 0, 1, "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/corpus/env/els/rub.wav", 0, 0, 1


        instr repuck
        $CORDELIA_QUALITIEs
        $CORDELIA_RELEASE

ipanfreq        init random:i(-.25, .25)

aout            repluck random:i(.015, .35), idyn, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3(1, random:i(.05, .25),  gisine)

aout    buthp aout, icps - icps/12

aout *= table3:a(linseg:a(0, idur, 1), ienv, 1)
        $CORDELIA_OUT
        endin


; INIT································································································································
girepuck_1_cycle ftgen 1001, 0, giFTGEN_SIZE, -27, 0, 0, 1024, 1, 2048, 2, 3072, 3, 4096, 4, 5120, 5, 6144, 6, 7168, 7, 8192, 8
gkrepuck_1_talea_num init 1
girepuck_1_talea ftgen 1002, 0, giFTGEN_SIZE, -17, 0, 1, 1, 0, 64, 2, 65, 0, 128, 3, 129, 0, 192, 4, 193, 0, 256, 5, 257, 0, 320, 6, 321, 0, 384, 7, 385, 0, 448, 8, 449, 0

girepuck_1_color ftgen 1003, 0, giFTGEN_SIZE, -2, 3, 246.02311099280728967642062343657016754150390625, 321.73895444327041559517965652048587799072265625, 492.0462219856145793528412468731403350830078125
girepuck_1_dur ftgen 1004, 0, giFTGEN_SIZE, -2, 1, 3
girepuck_1_dyn ftgen 1005, 0, giFTGEN_SIZE, -2, 1, $mf
girepuck_1_env ftgen 1006, 0, giFTGEN_SIZE, -2, 2, gicls, gigol
girepuck_1_space ftgen 1007, 0, giFTGEN_SIZE, -2, 1, 0

gkrepuck_1_color_count init -1
gkrepuck_1_dur_count init -1
gkrepuck_1_dyn_count init -1
gkrepuck_1_env_count init -1
gkrepuck_1_space_count init -1

        instr repuck_1
ktalea_prev init -1
kinit_flag  init 1

kmain                                   chnget "heart"
kphase                          table3 kmain, girepuck_1_cycle, 1
ktalea_idx                      = kphase % gkrepuck_1_talea_num 
ktalea                          table ktalea_idx * giTALEA_RESAMPLE_LEN, girepuck_1_talea

if ktalea > 0 && ktalea != ktalea_prev then
        if kinit_flag == 1 then
                gkrepuck_1_color_count = ktalea - 1
                gkrepuck_1_dur_count = ktalea - 1
                gkrepuck_1_dyn_count = ktalea - 1
                gkrepuck_1_env_count = ktalea - 1
                gkrepuck_1_space_count = ktalea - 1
                kinit_flag = 0
        endif

        ; ··· color
        kcolor_len  table 0, girepuck_1_color
        kcolor_idx  = (gkrepuck_1_color_count % kcolor_len) + 1
        kcolor      table kcolor_idx, girepuck_1_color
        ; ··· dur
        kdur_len  table 0, girepuck_1_dur
        kdur_idx  = (gkrepuck_1_dur_count % kdur_len) + 1
        kdur      table kdur_idx, girepuck_1_dur
        ; ··· dyn
        kdyn_len  table 0, girepuck_1_dyn
        kdyn_idx  = (gkrepuck_1_dyn_count % kdyn_len) + 1
        kdyn      table kdyn_idx, girepuck_1_dyn
        ; ··· env
        kenv_len  table 0, girepuck_1_env
        kenv_idx  = (gkrepuck_1_env_count % kenv_len) + 1
        kenv      table kenv_idx, girepuck_1_env
        ; ··· space
        kspace_len  table 0, girepuck_1_space
        kspace_idx  = (gkrepuck_1_space_count % kspace_len) + 1
        kspace      table kspace_idx, girepuck_1_space

        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "repuck", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kch, "repuck_1"
                        kch += 1
                od
        else
                schedulek "repuck", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kspace, "repuck_1"
        endif

        gkrepuck_1_color_count += 1
        gkrepuck_1_dur_count += 1
        gkrepuck_1_dyn_count += 1
        gkrepuck_1_env_count += 1
        gkrepuck_1_space_count += 1
        ktalea_prev = ktalea
endif
        endin
schedule "repuck_1", 0, -1
schedule 950.01, 0, -1, "repuck_1_1"
schedule 950.02, 0, -1, "repuck_1_2"

; BRIDGE repuck_1································································································································
        instr repuck_1_bridge
ich init p4
        xtratim giXTRATIM

krel            init 0
krel            release
idyn            init 1
adyn_in cosseg 0, .005, 1
adyn_out        init 1

if krel == 1 then
        adyn_in cosseg idyn, giXTRATIM/4, 0, giXTRATIM*3/4, 0 
        adyn_out cosseg idyn, giXTRATIM*2/3, idyn, giXTRATIM/3, 0
endif

amain_in chnget sprintf("%s_%i", "repuck_1", ich)
amain_in *= adyn_in

amain_out = amain_in

        chnmix amain_out*adyn_out, gSmouth[ich-1]
        endin
schedule nstrnum("repuck_1_bridge")+1/1000, 0, -1, 1
schedule nstrnum("repuck_1_bridge")+2/1000, 0, -1, 2

; GLOBAL VAR pulse INIT································································································································
        instr pulse
gkpulse = 120
        endin
schedule "pulse", 0, -1

; END ORC | 05·41pm································································································································




</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

