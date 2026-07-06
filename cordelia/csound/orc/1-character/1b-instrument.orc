#define CORDELIA_BEGIN_INSTR(instr_name) #
	instr $instr_name
	$CORDELIA_QUALITIEs($instr_name)
#

#define CORDELIA_QUALITIEs(instr_name) #
Sinstr	init "$instr_name"
idur		init abs(p3)
idyn		init p4
ienv		init p5
icps		init p6
ich		init p7
#

/* -------------------------------------------------------------------------- */
/*                                   PREVENT                                  */
/* -------------------------------------------------------------------------- */
#define CORDELIA_CPS_HI_LIMIT #
until icps < giINSTR_CPS_HI_LIMIT do
	icps	init icps/2
od
#

#define CORDELIA_DCBLOCK #
aout buthp aout, 20
#

#define CORDELIA_ENV #
aout *= envgen(idur_var, ienv)
#
#define CORDELIA_OUT #chnmix aout, sprintf("%s_%i", Sinstr, ich)#

#define CORDELIA_END_INSTR #
	$CORDELIA_ENV
	$CORDELIA_OUT
	endin
#


#define sample_instr_out #
indx				init ich - 1
ifile_nchnls	filenchnls Spath
ilimit			max ifile_nchnls, ginchnls
ifile_ch   		init (indx % (ifile_nchnls <= ginchnls ? ifile_nchnls : ginchnls)) + 1

ain = ains[ifile_ch-1]*$dyn_var*ifactor_dyn
#
