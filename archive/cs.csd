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
gkpulse 	init 60
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










; BEGIN ORC | 06·55pm································································································································
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



; N.B. Path without the last slash / !!!
gSloki_path init "/Users/j/Documents/PROJECTs/CORDELIA/_INSTR/sonvs/samps-loki"
giloki_mecha    init 1

        $start_instr(loki)
        ; IF RANGE DYN
                if      idyn < ampdbfs(-13) then
                        Sdyn init "0-30"
                elseif  idyn < ampdbfs(-11) then
                        idyn init ampdbfs(-11)
                        Sdyn init "31-60"
                elseif  idyn < ampdbfs(-9) then
                        idyn init ampdbfs(-9)
                        Sdyn init "61-90"
                elseif  idyn < ampdbfs(-5) then
                        idyn init ampdbfs(-5)
                        Sdyn init "91-110"
                else
                        Sdyn init "111-127"
                endif


        inote = 69 + 12 * log2(icps / A4)
        ; IF IN RANGE:
                if inote <= 11 && inote > 0 then
                                irootnote = 9
                                Snote_name init "A-1"
                elseif inote <= 14 && inote > 11 then
                                irootnote = 12
                                Snote_name init "C0"
                elseif inote <= 17 && inote > 14 then
                                irootnote = 15
                                Snote_name init "Eb0"
                elseif inote <= 20 && inote > 17 then
                                irootnote = 18
                                Snote_name init "Gb0"
                elseif inote <= 23 && inote > 20 then
                                irootnote = 21
                                Snote_name init "A0"
                elseif inote <= 26 && inote > 23 then
                                irootnote = 24
                                Snote_name init "C1"
                elseif inote <= 29 && inote > 26 then
                                irootnote = 27
                                Snote_name init "Eb1"
                elseif inote <= 32 && inote > 29 then
                                irootnote = 30
                                Snote_name init "Gb1"
                elseif inote <= 35 && inote > 32 then
                                irootnote = 33
                                Snote_name init "A1"
                elseif inote <= 38 && inote > 35 then
                                irootnote = 36
                                Snote_name init "C2"
                elseif inote <= 41 && inote > 38 then
                                irootnote = 39
                                Snote_name init "Eb2"
                elseif inote <= 44 && inote > 41 then
                                irootnote = 42
                                Snote_name init "Gb2"
                elseif inote <= 47 && inote > 44 then
                                irootnote = 45
                                Snote_name init "A2"
                elseif inote <= 50 && inote > 47 then
                                irootnote = 48
                                Snote_name init "C3"
                elseif inote <= 53 && inote > 50 then
                                irootnote = 51
                                Snote_name init "Eb3"
                elseif inote <= 56 && inote > 53 then
                                irootnote = 54
                                Snote_name init "Gb3"
                elseif inote <= 59 && inote > 56 then
                                irootnote = 57
                                Snote_name init "A3"
                elseif inote <= 62 && inote > 59 then
                                irootnote = 60
                                Snote_name init "C4"
                elseif inote <= 65 && inote > 62 then
                                irootnote = 63
                                Snote_name init "Eb4"
                elseif inote <= 68 && inote > 65 then
                                irootnote = 66
                                Snote_name init "Gb4"
                elseif inote <= 71 && inote > 68 then
                                irootnote = 69
                                Snote_name init "A4"
                elseif inote <= 74 && inote > 71 then
                                irootnote = 72
                                Snote_name init "C5"
                elseif inote <= 77 && inote > 74 then
                                irootnote = 75
                                Snote_name init "Eb5"
                elseif inote <= 80 && inote > 77 then
                                irootnote = 78
                                Snote_name init "Gb5"
                elseif inote <= 83 && inote > 80 then
                                irootnote = 81
                                Snote_name init "A5"
                elseif inote <= 86 && inote > 83 then
                                irootnote = 84
                                Snote_name init "C6"
                elseif inote <= 89 && inote > 86 then
                                irootnote = 87
                                Snote_name init "Eb6"
                elseif inote <= 92 && inote > 89 then
                                irootnote = 90
                                Snote_name init "Gb6"
                elseif inote <= 127 && inote > 92 then
                                irootnote = 96
                                Snote_name init "C7"
                endif

        irootnote2cps = A4 * pow(2, (irootnote - 69) / 12)
        iratio = icps / irootnote2cps


        if (ich % 2) == 0 then
                Smics_lateral[] fillarray "L", "LKey"
        else
                Smics_lateral[] fillarray "R", "RKey"
        endif

        imax_RR                 init 5
        if strcmp(Snote_name, "A2") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "Eb3") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "Eb2") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "Gb2") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "Gb1") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "A3") == 0 then
                imax_RR init 4
        elseif strcmp(Snote_name, "C4") == 0 then
                imax_RR init 4
        endif

        index_RR_lateral                init 1 + (floor(icps*idyn) % (imax_RR))

        S_RR_lateral                    sprintf "RR%i", index_RR_lateral
        Spath_lateral                   sprintf "%s/FP_%s_%s_%s_%s.wav", gSloki_path, Smics_lateral[(floor(icps) % 2)], Snote_name, Sdyn, S_RR_lateral
        aout_lateral                    diskin Spath_lateral, iratio;, iskiptime/1000



        ;index_RR_central               init 1 + (floor(icps*idyn*2) % (imax_RR))
        ;S_RR_central                   sprintf "RR%i", index_RR_central
        S_RR_central                    sprintf "RR%i", floor(random(1, imax_RR))
        Spath_central                   sprintf "%s/FP_%s_%s_%s_%s.wav", gSloki_path, "C", Snote_name, Sdyn, S_RR_central
        aout_central                    diskin Spath_central, iratio;, iskiptime/1000


        aout                                            sum aout_lateral/8, aout_central/8
        
        ;FP_RKey_C4_31-60_RR1
        ; RELEASE
        ;================================================================
        if idur < 7.5 then
                Spath_release sprintf "%s/KeyNoise_RR%i.wav", gSloki_path, floor(index_RR_lateral / imax_RR)*15
                schedule "loki_release", 0, 5, Spath_release, idyn/3, ich
        endif

        index_RR_release                init 1 + (floor(icps*idyn) % 20)


        if  idyn < ampdbfs(-7) then
                Spath_release sprintf "%s/release_soft_RR%i.wav", gSloki_path, index_RR_release
        else
                Spath_release sprintf "%s/release_hard_RR%i.wav", gSloki_path, index_RR_release
        endif
        schedule "loki_release", idur, idur, Spath_release, idyn*giloki_mecha, ich
        ;================================================================


        $dur_var(10)
$end_instr


instr loki_release

        Sinstr  init "loki"
        Spath init p4
        ilen filelen Spath
        if p3 > ilen then
                p3 init ilen
        endif
        idur init p3
        idyn init p5
        ich init p6
        aenv cosseg 0, .05, 1, idur-.05*2, 1, .05, 0
        ains[] diskin Spath, 1;, iskiptime/1000
        ifactor_dyn init 1
        $sample_instr_out
        aout = ain
        $channel_mix
endin



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
;aout       balance2 aout, ain

    xout aout
    endop




; INIT································································································································

giloki_1_talea ftgen 1002, 0, giFTGEN_SIZE, -2, 8, 1, 0, 2, 0, 3, 0, 4, 0
giloki_1_colores ftgen 1003, 0, giFTGEN_SIZE, -2, 4, 300, 300, 500, 200
giloki_1_dur ftgen 1004, 0, giFTGEN_SIZE, -2, 4, 24.0, 24.0, 24.0, 24.0
giloki_1_dyn ftgen 1005, 0, giFTGEN_SIZE, -2, 1, $fff
giloki_1_env ftgen 1006, 0, giFTGEN_SIZE, -2, 1, gicls
giloki_1_space ftgen 1007, 0, giFTGEN_SIZE, -2, 1, 0
giloki_1_cycle ftgen 1001, 0, giFTGEN_SIZE, -2, 1, 8

gkloki_1_colores_count init -1
gkloki_1_dur_count init -1
gkloki_1_dyn_count init -1
gkloki_1_env_count init -1
gkloki_1_space_count init -1

        instr loki_1
ktalea_prev init -1
kinit_flag  init 1

kmain   chnget "heart"

kcycle_len table 0, giloki_1_cycle
kcycle_idx  = floor(((kmain*gkdiv/kcycle_len)%1)*kcycle_len) + 1
kcycle table kcycle_idx, giloki_1_cycle

kphase  = (kmain * kcycle) % 1

ktalea_len  table 0, giloki_1_talea
ktalea_idx = floor(kphase * ktalea_len) + 1
ktalea  table ktalea_idx, giloki_1_talea

if ktalea > 0 && ktalea != ktalea_prev then
        if kinit_flag == 1 then
                gkloki_1_colores_count = ktalea - 1
                gkloki_1_dur_count = ktalea - 1
                gkloki_1_dyn_count = ktalea - 1
                gkloki_1_env_count = ktalea - 1
                gkloki_1_space_count = ktalea - 1
                kinit_flag = 0
        endif

        ; ··· colores
        kcolores_len  table 0, giloki_1_colores
        kcolores_idx  = (gkloki_1_colores_count % kcolores_len) + 1
        kcolores      table kcolores_idx, giloki_1_colores
        ; ··· dur
        kdur_len  table 0, giloki_1_dur
        kdur_idx  = (gkloki_1_dur_count % kdur_len) + 1
        kdur      table kdur_idx, giloki_1_dur
        ; ··· dyn
        kdyn_len  table 0, giloki_1_dyn
        kdyn_idx  = (gkloki_1_dyn_count % kdyn_len) + 1
        kdyn      table kdyn_idx, giloki_1_dyn
        ; ··· env
        kenv_len  table 0, giloki_1_env
        kenv_idx  = (gkloki_1_env_count % kenv_len) + 1
        kenv      table kenv_idx, giloki_1_env
        ; ··· space
        kspace_len  table 0, giloki_1_space
        kspace_idx  = (gkloki_1_space_count % kspace_len) + 1
        kspace      table kspace_idx, giloki_1_space

        if kspace == 0 then
                kch = 1
                until kch > ginchnls do
                        schedulek "loki", 0, kdur * gkBEATs * kcycle / gkdiv, kdyn, kenv, kcolores, kch
                        kch += 1
                od
        else
                schedulek "loki", 0, kdur * gkBEATs * kcycle / gkdiv, kdyn, kenv, kcolores, kspace
        endif

        gkloki_1_colores_count += 1
        gkloki_1_dur_count += 1
        gkloki_1_dyn_count += 1
        gkloki_1_env_count += 1
        gkloki_1_space_count += 1
        ktalea_prev = ktalea
endif
        endin

schedule "loki_1", ksmps/sr, -1
schedule 950.01, 0, -1, "loki_1"
schedule 950.02, 0, -1, "loki_2"

; GLOBAL VAR loki_1_dio_1_0 INIT································································································································
gkloki_1_dio_1_0 init 330
        instr loki_1_dio_1_0
gkloki_1_dio_1_0 = 3000+oscil3:k(3000/2, 1/2, giasine)+jitter(3000/4, gkBEATf, gkBEATf/8)
        endin
schedule "loki_1_dio_1_0", 0, -1

; BRIDGE loki································································································································
        instr loki_1_bridge
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

amain_in chnget sprintf("%s_%i", "loki", ich)
amain_in *= adyn_in

amain_out cordelia_diode_ladder amain_in , gkloki_1_dio_1_0
        chnmix amain_out*adyn_out, gSmouth[ich-1]
        endin
schedule nstrnum("loki_1_bridge")+1/1000, 0, -1, 1
schedule nstrnum("loki_1_bridge")+2/1000, 0, -1, 2

; END ORC | 06·55pm································································································································

















</CsInstruments>
<CsScore>
f 0 z
</CsScore>
</CsoundSynthesizer>

