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







; BEGIN ORC | 02·50pm································································································································
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



/* 
~idi di luglio 2026
coming from another synth icreated working on cordelia reborn
è rimasto nel cuore, come argilla secca sugli scogli
*/

        instr tiny
        $CORDELIA_QUALITIEs
        $CORDELIA_RELEASE

inoi_type       random 0, 2
anoi                    fractalnoise 1/12, inoi_type
aosc                    oscil3 1/2, icps
avco                    vco2 1/64, icps

anoi_env                cosseg 1, .005+random(.0095, .005), 0
aout                    sum aosc, anoi*anoi_env, avco

aout                    *= idyn
avib                    = .5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005))
aout                    = aout * avib

        $CORDELIA_END_INSTR


gkpulse init 120
; INIT································································································································
gitiny_1_cycle ftgen 1001, 0, giFTGEN_SIZE, -27, 0, 0, 512, 1, 513, 1, 1024, 2, 1025, 2, 1536, 3, 1537, 3, 2048, 4, 2049, 4, 2560, 5, 2561, 5, 3072, 6, 3073, 6, 3584, 7, 3585, 7, 4096, 8, 4097, 8, 4608, 9, 4609, 9, 5120, 10, 5121, 10, 5632, 11, 5633, 11, 6144, 12, 6145, 12, 6656, 13, 6657, 13, 7168, 14, 7169, 14, 7680, 15, 7681, 15, 8192, 16


        gktalea_num init 1
gitiny_1_talea ftgen 1002, 0, giFTGEN_SIZE, -17, 0, 1, 1, 0, 192, 2, 193, 0, 384, 3, 385, 0
gitiny_1_color ftgen 1003, 0, giFTGEN_SIZE, -2, 3, 246.02311099280728967642062343657016754150390625, 287.706995053765012926305644214153289794921875, 321.73895444327041559517965652048587799072265625
gitiny_1_dur ftgen 1004, 0, giFTGEN_SIZE, -2, 4, 2, 2, 2, 2
gitiny_1_dyn ftgen 1005, 0, giFTGEN_SIZE, -2, 1, $mf
gitiny_1_env ftgen 1006, 0, giFTGEN_SIZE, -2, 1, gicls
gitiny_1_space ftgen 1007, 0, giFTGEN_SIZE, -2, 1, 0

gktiny_1_color_count init -1
gktiny_1_dur_count init -1
gktiny_1_dyn_count init -1
gktiny_1_env_count init -1
gktiny_1_space_count init -1

        instr REF
        gktalea_num init 2
gitiny_1_talea ftgen 1002, 0, giFTGEN_SIZE, -17, \
        0, 1, 1, 0, 192, 2, 193, 0, 384, 3, 385, 0, 512, 4, 513, 0, 704, 5, 705, 0, 896, 6, 897, 0
        prints "REF\n\n\n\n\n"
        turnoff
        endin
        schedule "REF", 5, 1

        instr REF1
        gktalea_num init 1
gitiny_1_talea ftgen 1002, 0, giFTGEN_SIZE, -17, 0, 1, 1, 0, 64, 2, 65, 0, 128, 3, 129, 0, 192, 4, 193, 0, 256, 5, 257, 0, 320, 6, 321, 0, 384, 7, 385, 0, 448, 8, 449, 0
        prints "REF\n\n\n\n\n"
        turnoff
        endin
        schedule "REF1", 10, 1

        instr tiny_1
ktalea_prev init -1
kinit_flag  init 1

kmain   chnget "heart"

kphase          table kmain, gitiny_1_cycle, 1

ktalea_idx      = floor((kphase % gktalea_num) * 512)
ktalea          table floor(ktalea_idx), gitiny_1_talea


if ktalea > 0 && ktalea != ktalea_prev then
        if kinit_flag == 1 then
                gktiny_1_color_count = ktalea - 1
                gktiny_1_dur_count = ktalea - 1
                gktiny_1_dyn_count = ktalea - 1
                gktiny_1_env_count = ktalea - 1
                gktiny_1_space_count = ktalea - 1
                kinit_flag = 0
        endif

        ; ··· color
        kcolor_len  table 0, gitiny_1_color
        kcolor_idx  = (gktiny_1_color_count % kcolor_len) + 1
        kcolor      table kcolor_idx, gitiny_1_color
        ; ··· dur
        kdur_len  table 0, gitiny_1_dur
        kdur_idx  = (gktiny_1_dur_count % kdur_len) + 1
        kdur      table kdur_idx, gitiny_1_dur
        ; ··· dyn
        kdyn_len  table 0, gitiny_1_dyn
        kdyn_idx  = (gktiny_1_dyn_count % kdyn_len) + 1
        kdyn      table kdyn_idx, gitiny_1_dyn
        ; ··· env
        kenv_len  table 0, gitiny_1_env
        kenv_idx  = (gktiny_1_env_count % kenv_len) + 1
        kenv      table kenv_idx, gitiny_1_env
        ; ··· space
        kspace_len  table 0, gitiny_1_space
        kspace_idx  = (gktiny_1_space_count % kspace_len) + 1
        kspace      table kspace_idx, gitiny_1_space

        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kch, "tiny_1"
                        kch += 1
                od
        else
                schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kspace, "tiny_1"
        endif

        gktiny_1_color_count += 1
        gktiny_1_dur_count += 1
        gktiny_1_dyn_count += 1
        gktiny_1_env_count += 1
        gktiny_1_space_count += 1
        ktalea_prev = ktalea
endif
        endin
schedule "tiny_1", 0, -1
schedule 950.01, 0, -1, "tiny_1_1"
schedule 950.02, 0, -1, "tiny_1_2"

; BRIDGE tiny································································································································
        instr tiny_1_bridge
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

amain_in chnget sprintf("%s_%i", "tiny_1", ich)
amain_in *= adyn_in

amain_out = amain_in

        chnmix amain_out*adyn_out, gSmouth[ich-1]
        endin
schedule nstrnum("tiny_1_bridge")+1/1000, 0, -1, 1
schedule nstrnum("tiny_1_bridge")+2/1000, 0, -1, 2


; END ORC | 02·50pm································································································································





</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

