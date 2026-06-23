
gSFAREWELLs[] fillarray \
"Farewell, farewell! one kiss, and I'll descend.", \
"Farewell! God knows when we shall meet again.", \
"Farewell: buy food, and get thyself in flesh.", \
"Farewell: thou canst not teach me to forget.", \
"Farewell; be trusty, and I'll quit thy pains.", \
"Farewell; commend me to thy mistress."


	seed 0
	instr SENSE_KEYBOARD_TOUCHEs
ilen			lenarray gSFAREWELLs
ialea			floor random(0, ilen)
Sfarewell	init gSFAREWELLs[ialea]
iesc			init 27

kascii, kpress sensekey

if kascii == iesc && kpress == 1 then
	printks "\n························································\n", 1
	printks "························································\n", 1
	printks "························································\n", 1
	printks sprintfk("···\t%s\t···\n", Sfarewell), 1
	printks "························································\n", 1
	printks "························································\n", 1
	printks "························································\n", 1
	event "e", 0, 1/6
	turnoff
endif

	endin
	schedule "SENSE_KEYBOARD_TOUCHEs", 0, -1






