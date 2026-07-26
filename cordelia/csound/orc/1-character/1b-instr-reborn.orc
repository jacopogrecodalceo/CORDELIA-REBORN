/* -------------------------------------------------------------------------- */
/*                               CORDELIA REBORN                              */
/* -------------------------------------------------------------------------- */
#define CORDELIA_QUALITIEs #
idur			init abs(p3)
idyn			init p4
ienv			init p5
icps			init p6
ich			init p7
Sinstr_out	init p8
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

#define CORDELIA_ENV(custom_env) #
if ienv == 0 then
	$custom_env
else
	aenv	cordelia_envgen ienv, idur, irel
endif
#

#define CORDELIA_OUT #
aout	*= aenv
chnmix aout, sprintf("%s_%i", Sinstr_out, ich)
#

#define CORDELIA_SCHEDULE(instr_name) #
	schedule $instr_name, 0, idur, idyn, ienv, icps, ich, Sinstr_out
#

#define CORDELIA_BEGIN_INSTR(instr_name) #
	instr $instr_name
$CORDELIA_QUALITIEs($instr_name)
#

#define CORDELIA_CPS_HI_LIMIT #
until icps < giINSTR_CPS_HI_LIMIT do
	icps	init icps/2
od
#

#define CORDELIA_DCBLOCK #
aout buthp aout, 20
#

#define CORDELIA_SAMP_OUT #
indx				init ich - 1
ifile_nchnls	filenchnls Spath
ilimit			max ifile_nchnls, ginchnls
ifile_ch   		init (indx % (ifile_nchnls <= ginchnls ? ifile_nchnls : ginchnls)) + 1
ain 				= ains[ifile_ch-1]
#
