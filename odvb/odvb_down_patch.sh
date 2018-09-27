#!/bin/bash
################################################################################
#description:download code used by repo command
#                         EDIT HISTORY FOR MODULE
#      case                who                when                Action
################################################################################
export PATH=~/bin:$PATH

echo "********************************************************************************"
echo "                       odvb repo_download_patch                          "
echo "********************************************************************************"

# debug_flag:(on/off)
if [[ $debug_flag == "on" ]];then
    set -x
fi

# initialize the parameters
code_root=$1

patch_cfg_file=$code_root/patch/patch.cfg
android_root=$code_root/android_code

echo "code_root=$code_root"
echo "android_root=$android_root"
echo "patch_cfg_file=$patch_cfg_file"

#建立环境目录
# echo "********************************************************************************"
# echo "                   Prepare SSH                                       "
# echo "********************************************************************************"
# cp -rvf ~/ssh_download/.gitconfig ~/
# cp -rvf ~/ssh_download/.ssh ~/

pushd $android_root
    while read line
    do
        project=`echo $line | awk -F ":" '{print $1}'`
        refchange=`echo $line | awk -F ":" '{print $2}'`
        echo "download patch cmd: [repo download $project $refchange]"
        repo download $project $refchange
    done < $patch_cfg_file
popd
