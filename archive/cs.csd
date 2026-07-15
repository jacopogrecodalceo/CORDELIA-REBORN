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












; BEGIN ORC | 05·19pm································································································································
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

        $CORDELIA_BEGIN_INSTR(tiny)

irel init idur+random(.005, -.005)
        xtratim irel

anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco
aout *= idyn
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

aenv_indx       linsegr 1, idur, random(1/8, 1/24), irel, 0
aenv                    table3 aenv_indx, ienv, 1
aout                    *= aenv

        $CORDELIA_OUT
        endin


; INIT································································································································

gitiny_1_ts_idx ftgen 1001, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0

gktiny_1_ts_dur[] fillarray 8
gktiny_1_ts_start[] fillarray 0
gktiny_1_ts_den init 1
gktiny_1_ts_total init 8
                

gitiny_1_talea ftgen 1002, 0, giFTGEN_SIZE, -2, 8, 1, 2, 3, 4, 5, 6, 7, 8
gitiny_1_color ftgen 1003, 0, giFTGEN_SIZE, -2, 3, 300, 500, 200
gitiny_1_dur ftgen 1004, 0, giFTGEN_SIZE, -2, 3, 24.0, 24.0, 16.0
gitiny_1_dyn ftgen 1005, 0, giFTGEN_SIZE, -2, 1, $fff
gitiny_1_env ftgen 1006, 0, giFTGEN_SIZE, -2, 1, gicls
gitiny_1_space ftgen 1007, 0, giFTGEN_SIZE, -2, 1, 0

gktiny_1_color_count init -1
gktiny_1_dur_count init -1
gktiny_1_dyn_count init -1
gktiny_1_env_count init -1
gktiny_1_space_count init -1

        instr tiny_1
ktalea_prev init -1
kinit_flag  init 1

kmain   chnget "heart"


kglobal_beat = kmain * gkdiv * (gktiny_1_ts_den/4)
kcycle_pos = kglobal_beat % gktiny_1_ts_total

kseg_idx    table kcycle_pos / gktiny_1_ts_total, gitiny_1_ts_idx, 1
kphase = (kcycle_pos - gktiny_1_ts_start[kseg_idx]) / gktiny_1_ts_dur[kseg_idx]


ktalea_len  table 0, gitiny_1_talea
ktalea_idx = floor(kphase * ktalea_len) + 1
ktalea  table ktalea_idx, gitiny_1_talea

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
                        schedulek "tiny", 0, kdur * gkBEATs / gkdiv, kdyn, kenv, kcolor, kch
                        kch += 1
                od
        else
                schedulek "tiny", 0, kdur * gkBEATs / gkdiv, kdyn, kenv, kcolor, kspace
        endif

        gktiny_1_color_count += 1
        gktiny_1_dur_count += 1
        gktiny_1_dyn_count += 1
        gktiny_1_env_count += 1
        gktiny_1_space_count += 1
        ktalea_prev = ktalea
endif
        endin

schedule "tiny_1", ksmps/sr, -1
schedule 950.01, 0, -1, "tiny_1"
schedule 950.02, 0, -1, "tiny_2"

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

amain_in chnget sprintf("%s_%i", "tiny", ich)
amain_in *= adyn_in

amain_out = amain_in

        chnmix amain_out*adyn_out, gSmouth[ich-1]
        endin
schedule nstrnum("tiny_1_bridge")+1/1000, 0, -1, 1
schedule nstrnum("tiny_1_bridge")+2/1000, 0, -1, 2

; END ORC | 05·19pm································································································································













</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

