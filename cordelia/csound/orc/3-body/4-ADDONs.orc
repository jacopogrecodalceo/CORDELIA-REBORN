	instr clock_sender

aph_init	chnget "heart_a"

aph		= aph_init
;aph		delay aph_init, gidelayclock

		outch gimainclock_ch, aph
		outch giquarterclock_ch, (aph*64)%1

	endin
	;alwayson("clock_sender")


/* 	massign 0, nstrnum("midi_input")

	instr midi_input

icps	cpstmid i(gktuning)

	eva_midi "ixland", 0, 1, ampmidi(1), gisotrap, icps
	turnoff

	endin
 */


	/* instr alive
	printk 1, random:k(0, 5)
	endin
	schedule "alive", 0, -1 */

ich init 1
until ich > ginchnls do
        schedule 950+giINSTR_CLEAR_COUNT/1000, 0, -1, sprintf("mouth_%i", ich)
		ich +=1
        giINSTR_CLEAR_COUNT += 1
od
