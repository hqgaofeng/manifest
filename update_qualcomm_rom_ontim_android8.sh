#!/bin/bash

script_path=`pwd`
cd rom
LOCAL_PATH=`pwd`
pwd
MANIFEST_XML_FILE=$LOCAL_PATH/.repo/manifest.xml

USER_NAME="admin"
SERVER_IP="192.168.0.100"
SERVER_PORT="29418"
project_name_prefix="sdm"
local_qualcomm_branch="LA.UM.6.1"
local_ontim_branch="qualcomm/rom/caf"

outout_porject_list_name=$LOCAL_PATH/project_list_name
outout_porject_list_path=$LOCAL_PATH/project_list_path
outout_local_list_path=$LOCAL_PATH/local_path
new_remote_path=$script_path/new_remotepath
push_log=$script_path/pushlog
error_path=$script_path/error_path

function GetNameAndPath()
{
	echo > $outout_porject_list_name
	echo > $outout_porject_list_path
	while read LINE
	do
		command_line=`echo $LINE | grep "<project"`
		if [ "$command_line" ];then
			repo_name_sec=${LINE#*name=\"}
			repo_path_sec=${LINE#*path=\"}
			if [ "$repo_name_sec" ] && [ "$repo_path_sec" ];then
				repo_name=${repo_name_sec%%\"*}
				repo_path=${repo_path_sec%%\"*}
				echo "$repo_name" >> $outout_porject_list_name
				echo "$repo_path" >> $outout_porject_list_path
			fi
		fi
	done < $MANIFEST_XML_FILE
}
function CreatGerritProject()
{
	echo > $new_remote_path
	for project in `cat $outout_porject_list_name`;
	do
		echo $project
		remote_name_nb=`ssh -p $SERVER_PORT $USER_NAME@$SERVER_IP gerrit  ls-projects -m $project_name_prefix/$project | wc -l`
			
		if [ $remote_name_nb -gt 0 ];then
			echo "远程仓库:$project_name_prefix/$project 存在，不需要再次创建"
	        else	       
			echo "ssh -p $SERVER_PORT $USER_NAME@$SERVER_IP gerrit create-project --empty-commit $project_name_prefix/$project"
			ssh -p $SERVER_PORT $USER_NAME@$SERVER_IP gerrit create-project --empty-commit $project_name_prefix/$project
			echo "$project_name_prefix/$project" >> $new_remote_path

		fi
	done
}
function check_remote()
{
	cd $1
	remote=$(git remote -v | grep $project_name_prefix | wc -l)
	if [ $remote -gt 0 ];then
		echo remove remote $project_name_prefix
		git remote remove $project_name_prefix
	fi

}
function repo_sync()
{
	cd $LOCAL_PATH
	#repo sync
	local_pwd=$(repo forall -c pwd)
	echo "$local_pwd" > $outout_local_list_path
	repo start $local_qualcomm_branch --all
	repo checkout $local_qualcomm_branch
}
function pushLocalToRemote()
{
	rm -fr $error_path
	while read LINE
	do
		echo > $push_log
		cd $LINE
		pwd=`pwd`
		echo "当前所在目录是:$pwd"
		command_line=`git remote -v | grep fetch`
		repo_local_path_src=${command_line#*la/}
		repo_local_path_sr=${repo_local_path_src%%(*}
		repo_local_path=${repo_local_path_sr// /}
		check_remote $LINE
		echo $repo_local_path
		echo "git remote add $project_name_prefix ssh://$USER_NAME@$SERVER_IP:$SERVER_PORT/$project_name_prefix/$repo_local_path.git"
		echo "git push $project_name_prefix $local_qualcomm_branch:$local_ontim_branch"
		git remote add $project_name_prefix ssh://$USER_NAME@$SERVER_IP:$SERVER_PORT/$project_name_prefix/$repo_local_path.git
		git push $project_name_prefix $local_qualcomm_branch:$local_ontim_branch > $push_log 2>&1
		grep_result=$(grep -n "rejected" $push_log | wc -l)
		if [ $grep_result -gt 0 ];then
			echo "$pwd" >> $error_path
		fi
		cd -
	done < $outout_local_list_path
}

GetNameAndPath
CreatGerritProject
repo_sync
pushLocalToRemote
