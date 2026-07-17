/* -------------------------------------------------------------------------- */
/*                               CORDELIA REBORN                              */
/* -------------------------------------------------------------------------- */
#define CORDELIA_QUALITIEs(instr_name) #
Sinstr	init "$instr_name"
idur		init abs(p3)
idyn		init p4
ienv		init p5
icps		init p6
ich		init p7
#

#define CORDELIA_RELEASE #
if idur < 1 then
	irel_jit random .85, .95
else
	irel_jit random .5, .35
endif
irel 		init idur*irel_jit
			xtratim irel
#

#define CORDELIA_ENV #
aout *= cordelia_envgen(ienv, idur, irel)
#
#define CORDELIA_OUT #
chnmix aout, sprintf("%s_%i", Sinstr, ich)
#

#define CORDELIA_BEGIN_INSTR(instr_name) #
	instr $instr_name
$CORDELIA_QUALITIEs($instr_name)
$CORDELIA_RELEASE
#

#define CORDELIA_END_INSTR #
$CORDELIA_ENV
$CORDELIA_OUT
	endin
#

#define CORDELIA_CPS_HI_LIMIT #
until icps < giINSTR_CPS_HI_LIMIT do
	icps	init icps/2
od
#

#define CORDELIA_DCBLOCK #
aout buthp aout, 20
#

