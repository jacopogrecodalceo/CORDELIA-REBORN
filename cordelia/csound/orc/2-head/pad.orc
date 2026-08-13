opcode pad, S, ij
	inum, ipad xin

if ipad == -1 then
	ipad init 3
endif

Snum	sprintf "%i", inum
while strlen(Snum) < ipad do
	Snum strcat "0", Snum
od
	xout Snum
endop

