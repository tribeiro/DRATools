#!/bin/sh

#  sland.sh
#  DRATools
#
#  Created by Tiago Ribeiro on 10/01/14.
#

function copydata {

	#if [ -d "~/Documents/analise/CAL87/emap_0305keV_rateall/sland/par$2" ] ;then
	mkdir ~/Documents/analise/CAL87/emap_0305keV_rateall/slandq/par$2
	#fi

	cp $1 ~/Documents/analise/CAL87/emap_0305keV_rateall/slandq/par$2/

}

function c_simeclp {
    cd ~/Documents/analise/CAL87/emap_0305keV_rateall/slandq/par$2
	cat cal87_0305keV_rateall.dat.122 | awk '{print $1}'  > fase.122
    simeclp 51 sland 2 $1 $2 122 fase.122
    #prida 51 cal87_0305keV_rateall sland_122 ../../cal87config 1.1 0.5
}

function c_prida {
    cd ~/Documents/analise/CAL87/emap_0305keV_rateall/slandq/par$1
	#cat cal87_0305keV_rateall.data.122 | awk '{print $1}' > fase.122
    #simeclp 51 sland 2 $1 $2 122 fase.122
    prida 51 cal87_0305keV_rateall sland_122 ../../cal87config 1.11 0.
}


INC=82
for Q in $(seq 0.1 0.05 2.);do
	#echo $INC
	#copydata $1 $INC
	#copydata $1 $Q
	#c_simeclp $INC $Q
	c_prida $Q
done

