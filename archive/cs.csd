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
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/2-GLOBAL_VAR.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/1-character/3-FORMAT.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/saw.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/sine.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/square.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/2-bipolar/tri.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/3-window/hamming.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/3-window/hanning.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asaw.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asine.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/asquare.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/GEN/1-polar/atri.orc"

giedo12					ftgen 0, 0, 0, -2, 12, 2/1, A4, 69, 1, 1.0594630943592953, 1.122462048309373, 1.189207115002721, 1.2599210498948732, 1.3348398541700344, 1.4142135623730951, 1.4983070768766815, 1.5874010519681994, 1.681792830507429, 1.7817974362806785, 1.8877486253633868, 2/1

gktuning init giedo12
gktuning_len init tab_i(0, i(gktuning))

gSmouth[]		init ginchnls

indx		init 0
until	indx == ginchnls do
	gSmouth[indx]		sprintf	"mouth_%i", indx+1
	indx	+= 1
od

gkabstime	init 0 
gkdiv		init 64 ;max division of main tempo for heart and lungs

;	HEART
;	tempo for heart
gkpulse 	init 120
gkBEATf		init i(gkpulse) / 60
gkBEATs		init 1 / (i(gkpulse) / 60)

	instr heart

if gkpulse <= 0 then
	gkpulse = gizero
endif

gkBEATf		= gkpulse / 60				;frequency for a quarter note in Hz
gkBEATs		= 1 / (gkpulse / 60)		;time of a quarter note in sec
gkBEATms	= gkBEATs*1000

kph		init 0
kph		phasor (gkpulse / gkdiv) / 60

aph		init 0
aph		phasor (gkpulse / gkdiv) / 60

gkBEATn		init 0				;number of beats from the beginning of session
klast_n		init -1

if (((kph*gkdiv)%1) < klast_n) then
	gkBEATn += 1
endif

klast_n	= ((kph*gkdiv)%1)

gkBEATc	init 0				;number of beats from the beginning of session
klast_c	init -1

if kph < klast_c then
	gkBEATc += 1
endif

klast_c	= kph

/* kswing = (kph*gkdiv)%1
if gkswing > 0 && kswing > .5 then
	kph = (.5 + (kph - .5) * (1 - gkswing))%1
	aph = (.5 + (aph - .5) * (1 - gkswing))%1
endif */

	chnset	kph, "heart"

gkabstime	times


	endin
	schedule("heart", 1, -1)
;	alwayson("heart")


gkheartbeat_print_fact init 1

	instr heartbeat_print_control

if	gkpulse < 40 then
	gkheartbeat_print_fact = 32 
elseif	gkpulse > 40 && gkpulse < 160 then
	gkheartbeat_print_fact = 16
else
	gkheartbeat_print_fact = 8
endif

kph	chnget "heart"	
kph	= (kph * gkheartbeat_print_fact)
kph	= kph % 1

klast init -1

schedule "heartbeat_print", 0, 1

if (kph < klast) then
	schedulek "heartbeat_print", 0, 1
endif

klast	= kph

	endin
	alwayson("heartbeat_print_control")

	instr heartbeat_print
gipulse = i(gkpulse)
gibeats = i(gkBEATs)
gibeatms = i(gkBEATms)
gibeatf = i(gkBEATf)
itun = i(gktuning)
prints("\n────────── heartbeat signal ──────────\n")
	turnoff
	endin



#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/3-SOUL.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/4-ADDONs.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/envgen.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/cordelia_envgen.orc"











; BEGIN ORC | 01·31pm································································································································
schedule "heart", 0, -1
;       LIKEAREV
;       a 6-points function from linear segments
girev_atk               init sr * .005
girev_dur               init gienvdur - girev_atk
girev_int               init 32
girev_intdec            init 1
girev_dec               init girev_intdec / girev_int

girev_sus1              init .15
girev_intrel1           init 3
girev_rel1              init girev_intrel1 / girev_int

girev_sus2              init .05
girev_intrel2           init girev_int-girev_intdec-girev_intrel1
girev_rel2              init girev_intrel2 / girev_int

;-----------------------
girev           ftgen   0, 0, gienvdur, 7, 0, girev_atk, 1, girev_dur*girev_dec, girev_sus1, girev_dur*girev_rel1, girev_sus2, girev_dur*girev_rel2, 0
;-----------------------

/* 
~idi di luglio 2026
coming from another synth icreated working on cordelia reborn
è rimasto nel cuore, come argilla secca sugli scogli
*/

        $CORDELIA_BEGIN_INSTR(tiny)

anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco
aout *= idyn
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

        $CORDELIA_END_INSTR



; INIT································································································································
gitiny_2_cycle ftgen 1001, 0, giFTGEN_SIZE, -27, 0, 0, 256, 1, 257, 0, 512, 1, 513, 0, 768, 1, 769, 0, 1024, 1, 1025, 0, 1280, 1, 1281, 0, 1536, 1, 1537, 0, 1792, 1, 1793, 0, 2048, 1, 2049, 0, 2304, 1, 2305, 0, 2560,
1, 2561, 0, 2816, 1, 2817, 0, 3072, 1, 3073, 0, 3328, 1, 3329, 0, 3584, 1, 3585, 0, 3840, 1, 3841, 0, 4096, 1, 4097, 0, 4352, 1, 4353, 0, 4608, 1, 4609, 0, 4864, 1, 4865, 0, 5120, 1, 5121, 0, 5376, 1, 5377, 0, 5632, 
1, 5633, 0, 5888, 1, 5889, 0, 6144, 1, 6145, 0, 6400, 1, 6401, 0, 6656, 1, 6657, 0, 6912, 1, 6913, 0, 7168, 1, 7169, 0, 7424, 1, 7425, 0, 7680, 1, 7681, 0, 7936, 1, 7937, 0, 8192, 1

gitiny_2_talea ftgen 1002, 0, giFTGEN_SIZE, -2, 128, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 
0, 0
gitiny_2_color ftgen 1003, 0, giFTGEN_SIZE, -2, 16, 400, 400, 400, 400, 90, 90, 90, 90, 90, 90, 90, 90, 90, 120, 120, 120
gitiny_2_dur ftgen 1004, 0, giFTGEN_SIZE, -2, 1, .5
gitiny_2_dyn ftgen 1005, 0, giFTGEN_SIZE, -2, 1, $mf
gitiny_2_env ftgen 1006, 0, giFTGEN_SIZE, -2, 1, girev
gitiny_2_space ftgen 1007, 0, giFTGEN_SIZE, -2, 1, 0

gktiny_2_color_count init -1
gktiny_2_dur_count init -1
gktiny_2_dyn_count init -1
gktiny_2_env_count init -1
gktiny_2_space_count init -1

        instr tiny_2
ktalea_prev init -1
kinit_flag  init 1

kmain   chnget "heart"

kphase table kmain, gitiny_2_cycle, 1

ktalea_len  table 0, gitiny_2_talea
ktalea_idx = floor(kphase * ktalea_len) + 1
ktalea  table ktalea_idx, gitiny_2_talea

if ktalea > 0 && ktalea != ktalea_prev then
        if kinit_flag == 1 then
                gktiny_2_color_count = ktalea - 1
                gktiny_2_dur_count = ktalea - 1
                gktiny_2_dyn_count = ktalea - 1
                gktiny_2_env_count = ktalea - 1
                gktiny_2_space_count = ktalea - 1
                kinit_flag = 0
        endif

        ; ··· color
        kcolor_len  table 0, gitiny_2_color
        kcolor_idx  = (gktiny_2_color_count % kcolor_len) + 1
        kcolor      table kcolor_idx, gitiny_2_color
        ; ··· dur
        kdur_len  table 0, gitiny_2_dur
        kdur_idx  = (gktiny_2_dur_count % kdur_len) + 1
        kdur      table kdur_idx, gitiny_2_dur
        ; ··· dyn
        kdyn_len  table 0, gitiny_2_dyn
        kdyn_idx  = (gktiny_2_dyn_count % kdyn_len) + 1
        kdyn      table kdyn_idx, gitiny_2_dyn
        ; ··· env
        kenv_len  table 0, gitiny_2_env
        kenv_idx  = (gktiny_2_env_count % kenv_len) + 1
        kenv      table kenv_idx, gitiny_2_env
        ; ··· space
        kspace_len  table 0, gitiny_2_space
        kspace_idx  = (gktiny_2_space_count % kspace_len) + 1
        kspace      table kspace_idx, gitiny_2_space

        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kch
                        kch += 1
                od
        else
                schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kspace
        endif

        gktiny_2_color_count += 1
        gktiny_2_dur_count += 1
        gktiny_2_dyn_count += 1
        gktiny_2_env_count += 1
        gktiny_2_space_count += 1
        ktalea_prev = ktalea
endif
        endin
schedule "tiny_2", 0, -1
schedule 950.01, 0, -1, "tiny_1"
schedule 950.02, 0, -1, "tiny_2"

; BRIDGE tiny································································································································
        instr tiny_2_bridge
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

amain_in chnget sprintf("%s_%i", "tiny", ich)
amain_in *= adyn_in

amain_out = amain_in

        chnmix amain_out*adyn_out, gSmouth
        endin
schedule nstrnum("tiny_2_bridge")+1/1000, 0, -1, 1
schedule nstrnum("tiny_2_bridge")+2/1000, 0, -1, 2

; INIT································································································································
gitiny_3_cycle ftgen 1008, 0, giFTGEN_SIZE, -27, 0, 0, 256, 1, 257, 0, 512, 1, 513, 0, 768, 1, 769, 0, 1024, 1, 1025, 0, 1280, 1, 1281, 0, 1536, 1, 1537, 0, 1792, 1, 1793, 0, 2048, 1, 2049, 0, 2304, 1, 2305, 0, 2560,
1, 2561, 0, 2816, 1, 2817, 0, 3072, 1, 3073, 0, 3328, 1, 3329, 0, 3584, 1, 3585, 0, 3840, 1, 3841, 0, 4096, 1, 4097, 0, 4352, 1, 4353, 0, 4608, 1, 4609, 0, 4864, 1, 4865, 0, 5120, 1, 5121, 0, 5376, 1, 5377, 0, 5632, 
1, 5633, 0, 5888, 1, 5889, 0, 6144, 1, 6145, 0, 6400, 1, 6401, 0, 6656, 1, 6657, 0, 6912, 1, 6913, 0, 7168, 1, 7169, 0, 7424, 1, 7425, 0, 7680, 1, 7681, 0, 7936, 1, 7937, 0, 8192, 1

gitiny_3_talea ftgen 1009, 0, giFTGEN_SIZE, -2, 8, 1, 2, 3, 4, 5, 6, 7, 8
gitiny_3_color ftgen 1010, 0, giFTGEN_SIZE, -2, 7, 200, 200, 200, 200, 100, 100, 100
gitiny_3_dur ftgen 1011, 0, giFTGEN_SIZE, -2, 1, .5
gitiny_3_dyn ftgen 1012, 0, giFTGEN_SIZE, -2, 1, $mf
gitiny_3_env ftgen 1013, 0, giFTGEN_SIZE, -2, 1, girev
gitiny_3_space ftgen 1014, 0, giFTGEN_SIZE, -2, 1, 0

gktiny_3_color_count init -1
gktiny_3_dur_count init -1
gktiny_3_dyn_count init -1
gktiny_3_env_count init -1
gktiny_3_space_count init -1

        instr tiny_3
ktalea_prev init -1
kinit_flag  init 1

kmain   chnget "heart"

kphase table kmain, gitiny_3_cycle, 1

ktalea_len  table 0, gitiny_3_talea
ktalea_idx = floor(kphase * ktalea_len) + 1
ktalea  table ktalea_idx, gitiny_3_talea

if ktalea > 0 && ktalea != ktalea_prev then
        if kinit_flag == 1 then
                gktiny_3_color_count = ktalea - 1
                gktiny_3_dur_count = ktalea - 1
                gktiny_3_dyn_count = ktalea - 1
                gktiny_3_env_count = ktalea - 1
                gktiny_3_space_count = ktalea - 1
                kinit_flag = 0
        endif

        ; ··· color
        kcolor_len  table 0, gitiny_3_color
        kcolor_idx  = (gktiny_3_color_count % kcolor_len) + 1
        kcolor      table kcolor_idx, gitiny_3_color
        ; ··· dur
        kdur_len  table 0, gitiny_3_dur
        kdur_idx  = (gktiny_3_dur_count % kdur_len) + 1
        kdur      table kdur_idx, gitiny_3_dur
        ; ··· dyn
        kdyn_len  table 0, gitiny_3_dyn
        kdyn_idx  = (gktiny_3_dyn_count % kdyn_len) + 1
        kdyn      table kdyn_idx, gitiny_3_dyn
        ; ··· env
        kenv_len  table 0, gitiny_3_env
        kenv_idx  = (gktiny_3_env_count % kenv_len) + 1
        kenv      table kenv_idx, gitiny_3_env
        ; ··· space
        kspace_len  table 0, gitiny_3_space
        kspace_idx  = (gktiny_3_space_count % kspace_len) + 1
        kspace      table kspace_idx, gitiny_3_space

        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kch
                        kch += 1
                od
        else
                schedulek "tiny", 0, kdur * gkBEATs, kdyn, kenv, kcolor, kspace
        endif

        gktiny_3_color_count += 1
        gktiny_3_dur_count += 1
        gktiny_3_dyn_count += 1
        gktiny_3_env_count += 1
        gktiny_3_space_count += 1
        ktalea_prev = ktalea
endif
        endin
schedule "tiny_3", 0, -1
schedule 950.03, 0, -1, "tiny_1"
schedule 950.04, 0, -1, "tiny_2"

; BRIDGE tiny································································································································
        instr tiny_3_bridge
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

amain_in chnget sprintf("%s_%i", "tiny", ich)
amain_in *= adyn_in

amain_out = amain_in

        chnmix amain_out*adyn_out, gSmouth[ich-1]
        endin
schedule nstrnum("tiny_3_bridge")+1/1000, 0, -1, 1
schedule nstrnum("tiny_3_bridge")+2/1000, 0, -1, 2

; END ORC | 01·31pm································································································································










</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

