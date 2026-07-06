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
	schedule("heart", .5, -1)
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
prints("   ☀️ BPM : %.02f\n", gipulse)
prints("   ⏱  BEATS: %.02f s\n", gibeats)
prints("   🌐 FREQ : %.02f Hz\n", gibeatf)
prints("   🎚  TUNE : %.02f\n", itun)
prints("--------------------------------------\n")
        turnoff
	endin



#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/3-SOUL.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/3-body/4-ADDONs.orc"
#include "/Users/j/Documents/PROJECTs/CORDELIA-REBORN/cordelia/csound/orc/2-head/envgen.orc"



;BEGIN ORC | 02·34pm································································································································
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



;INSTRUMENT repuck LOADED································································································································
                $start_instr(repuck)

ipanfreq        init random:i(-.25, .25)

aout    repluck random:i(.015, .35), $dyn_var, icps + random:i(-ipanfreq, ipanfreq), randomh:k(.25, .95, random:i(.05, .15)), random:i(.05, .65), oscil3(1, random:i(.05, .25),  gisine)

aout    buthp aout, icps - icps/12
        outall aout*cosseg:a(1, idur, 0)
                $dur_var(10)
                $end_instr


; ── INSTRUMENT repuck_1 BIRTH ────────────────────────────
gkrepuck_1_cycle init 4

girepuck_1_talea ftgen 1001, 0, giFTGEN_SIZE, -2, 8, 0, 1, 0, 2, 0, 0, 3, 0
girepuck_1_colores ftgen 1002, 0, giFTGEN_SIZE, -2, 2, 300, 500
girepuck_1_dur ftgen 1003, 0, giFTGEN_SIZE, -2, 3, 24, 36, 36
girepuck_1_dyn ftgen 1004, 0, giFTGEN_SIZE, -2, 1, $mf
girepuck_1_env ftgen 1005, 0, giFTGEN_SIZE, -2, 1, gicls
girepuck_1_space ftgen 1006, 0, giFTGEN_SIZE, -2, 1, 0

gkrepuck_1_talea_count init -1
gkrepuck_1_colores_count init -1
gkrepuck_1_dur_count init -1
gkrepuck_1_dyn_count init -1
gkrepuck_1_env_count init -1
gkrepuck_1_space_count init -1

        instr repuck_1
ktalea_last init -1
kinit_flag  init 1

kcycle_reset init 1
kmain   chnget "heart"

if kmain < kcycle_reset then
        kcycle_reset = -1
endif
kphase  = (kmain * gkrepuck_1_cycle) % 1

ktalea_len      table 0, girepuck_1_talea
ktalea_idx      = floor(kphase * ktalea_len) + 1
ktalea          table ktalea_idx, girepuck_1_talea

if ktalea > 0 && ktalea != ktalea_last then
        if kinit_flag == 1 then
                kcycle_reset = kmain
                gkrepuck_1_talea_count = ktalea - 1
                gkrepuck_1_colores_count = ktalea - 1
                gkrepuck_1_dur_count = ktalea - 1
                gkrepuck_1_dyn_count = ktalea - 1
                gkrepuck_1_env_count = ktalea - 1
                gkrepuck_1_space_count = ktalea - 1
                kinit_flag = 0
        endif

        printf "talea:%09f, last: %09f\n", random:k(1, 2), ktalea, ktalea_last

        ; ··· talea
        ; ··· colores
        kcolores_len  table 0, girepuck_1_colores
        kcolores_idx  = (gkrepuck_1_colores_count % kcolores_len) + 1
        kcolores      table kcolores_idx, girepuck_1_colores
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

        ; ── schedule events ──────────────────────────────────────
        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "repuck", 0, kdur * gkBEATs * gkrepuck_1_cycle / gkdiv, kdyn, kenv, kcolores, kch
                        kch += 1
                od
        else
                schedulek "repuck", 0, kdur * gkBEATs * gkrepuck_1_cycle / gkdiv, kdyn, kenv, kcolores, kspace
        endif

        gkrepuck_1_talea_count += 1
        gkrepuck_1_colores_count += 1
        gkrepuck_1_dur_count += 1
        gkrepuck_1_dyn_count += 1
        gkrepuck_1_env_count += 1
        gkrepuck_1_space_count += 1

        ktalea_last = ktalea
        if kcycle_reset == -1 then
                ktalea_last = -1
        endif
endif
        endin

schedule "repuck_1", 0, -1
;END ORC | 02·34pm································································································································




</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

