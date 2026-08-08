#define CORDELIA_DISKIN_CHs #
ifile_nchnls	filenchnls Spath
ilimit			max ifile_nchnls, ginchnls
ifile_ch   		init ((ich-1) % (ifile_nchnls <= ginchnls ? ifile_nchnls : ginchnls)) + 1
ain 				= ains[ifile_ch-1]
#