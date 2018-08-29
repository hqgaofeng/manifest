#!/bin/bash

cd snapdragon-high-mid-2017-spf-1-0_amss_standard_oem


project_name_prefix="sdm"
local_ontim_branch="qualcomm/oem/caf"


#git checkout master
git branch
git pull
git_log=`git log -1 --pretty=format:"%s"`
echo $git_log

remote_path=(boot_images rpm_proc sdm636_common sdm660_common trustzone_images wdsp_proc btfm_proc adsp_proc cpe_proc modem_proc venus_proc wlan_proc cdsp_proc proprietary)

#cp about.html ../about
#cp MSM8953.LA.3.0.1/contents.xml ../about
#cd ../about
#git add .
#git commit -m "update $git_log"
#git push origin qualcomm:$local_ontim_branch
#cd -

for branch in ${remote_path[@]};
do
	    echo "当前所在:$branch"  
            git branch -D $branch
	    echo "剩余分支:"
	    git branch
done

git subtree split -P BOOT.XF.1.4   -b boot_images
git subtree split -P RPM.BF.1.8    -b rpm_proc
git subtree split -P SDM636.LA.2.1 -b sdm636_common
git subtree split -P SDM660.LA.2.1 -b   sdm660_common
git subtree split -P TZ.BF.4.0.7 -b     trustzone_images
git subtree split -P WDSP.9340.1.0 -b   wdsp_proc
git subtree split -P ADSP.VT.4.0 -b     adsp_proc
git subtree split -P BTFM.CHE.2.1.1 -b  btfm_proc
git subtree split -P CPE.TSF.2.0 -b     cpe_proc
git subtree split -P MPSS.AT.2.3  -b    modem_proc
git subtree split -P VIDEO.VE.4.4  -b   venus_proc
git subtree split -P WLAN.HL.1.0.1  -b  wlan_proc
git subtree split -P CDSP.VT.1.0 -b     cdsp_proc
git subtree split -P LA.UM.6.2/LINUX/android/vendor/qcom/proprietary -b proprietary

for branch in ${remote_path[@]};
do
	    echo $branch  
            git checkout $branch
            git remote remove $project_name_prefix
	    echo "git remote add $project_name_prefix ssh://admin@192.168.0.100:29418/$project_name_prefix/$branch.git"
	    echo "git push $project_name_prefix $branch:$local_ontim_branch"
            git remote add -f $project_name_prefix ssh://admin@192.168.0.100:29418/$project_name_prefix/$branch.git
            git push $project_name_prefix $branch:$local_ontim_branch -f 
done
