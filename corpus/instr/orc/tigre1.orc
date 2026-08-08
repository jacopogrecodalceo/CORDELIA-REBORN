	instr tigre1
	$CORDELIA_QUALITIEs
if ich > 1 then
	turnoff
endif
igate_len	init .05

aenv 			linseg 0, .005, 1, igate_len-.005*2, 1, .005, 0

	outch 1, aenv

	if timeinsts() > igate_len then
		turnoff
	endif

	endin