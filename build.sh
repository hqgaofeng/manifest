#!/bin/bash

echo "*****************************************************"
echo "----------------------compile start------------------"
echo "*****************************************************"

board="$1"
lunch="$2"
set_ccache()
{
    # user can use environment variable "CACHE_BASE" to customize ccache directory
    if [ -z "$CACHE_BASE" ]
    then
        CACHE_BASE=~/CC_TMP
        if [ ! -d "$CACHE_BASE" ]
        then
            mkdir -p $CACHE_BASE
            chmod -R 777 $CACHE_BASE
        fi
    fi

    echo "CCACHE_DIR="$CACHE_BASE

    export USE_CCACHE=1
    export CCACHE_DIR=$CACHE_BASE

    export CCACHE_UMASK=002

    prebuilts/misc/linux-x86/ccache/ccache -M 50G
}

export NUMBER_OF_PROCESSORS=`cat /proc/cpuinfo | grep 'processor' | wc -l`
source ./build/envsetup.sh

#choosecombo release full_cro_go user
lunch $lunch
board $board


set_ccache

#if [ ! "$1" ]; then
make update-api -j$NUMBER_OF_PROCESSORS
#fi

make -j$NUMBER_OF_PROCESSORS 2>&1 | tee BUILD-LOG-`date +[%Y-%m-%d]-[%H-%M-%S]`.txt
