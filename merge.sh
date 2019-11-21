#!/bin/bash
echo "********************************************************************************"
#description:自动merge common分支与GP分支（非指向仓）
echo "                       auto_cherry_pick.sh is called                                 "
echo "********************************************************************************"

#---------------check parameter---------------
# arg1: $repo_local_path       代码所在的根目录
# arg2: $target_branch         merge的目标分支
# arg3: $source_branch         merge的源分支
# arg4: $GERRIT_LOGUSER        gerrit登陆用户
# arg5: $GERRIT_REFSPEC        gerrit refs
# arg6: $GERRIT_PROJECT    需要做merge操作的白名单
# arg7: $GERRIT_CHANGE_URL    需要做merge操作的白名单
#-------------------------------------------

if [[ $# -lt 7 ]];then
	echo "[$0,Line:$LINENO] Error: The Number of parameter is incorrect"
	exit 1
fi

repo_local_path=$1
target_branch=$2
source_branch=$3
GERRIT_LOGUSER=$4
GERRIT_REFSPEC=$5
GERRIT_PROJECT=$6
GERRIT_CHANGE_URL=$7
GERRIT_PORT="29418"
PATH=$HOME/bin:$PATH
CI_SCRIPTS_PATH=`dirname $0`
source $CI_SCRIPTS_PATH/common.sh

# 定义存放log的目录
auto_merge_log_directory=$repo_local_path/mergeConflictFiles
# 定义全局是否发生冲突的变量
error_occur="false"
# 定义记录cherry-pick失败的log文件
merge_failed_file=$auto_merge_log_directory/merge_failed_file.cfg

# 函数功能：处理命令执行结果
function exit_err()
{
	if [ "$1" -ne 0 ]
	then
		echo "$2" 
		exit 1
	fi
	
	return 0
}

#函数功能：自动merge分支
function merge_branch()
{
	#解析GERRIT_REFSPEC
	gerrit_refspec=()
	split_str "$GERRIT_REFSPEC" ','
	alen=${#split_array[*]};
	for ((i=0;i< $alen;i++))   
	do 
		gerrit_refspec[$i]=${split_array[$i]}
	done

	#解析GERRIT_PROJECT
	gerrit_project=()
	split_str "$GERRIT_PROJECT" ','
	alen=${#split_array[*]};
	for ((i=0;i< $alen;i++))   
	do 
		gerrit_project[$i]=${split_array[$i]}
	done

	#解析GERRIT_CHANGE_URL http://10.11.26.10:8888/818
	GERRIT_CHANGE_URL=${GERRIT_CHANGE_URL:7}
	GERRIT_SERVER=${GERRIT_CHANGE_URL%%:*}

	alen=${#gerrit_project[*]};
	for ((i=0;i< $alen;i++))   
	do 
		#根据GERRIT_PROJECT路径确定git库在workspace下的路径
		GIT_PATH=`repo list 2>/dev/null | grep " ${gerrit_project[$i]}$" | sed 's/:.*$//'`
		GIT_PATH=$(echo ${GIT_PATH})
		if [[ ! -z "$GIT_PATH" ]];then
			if [[ ! -d "$GIT_PATH" ]];then
				echo "Warning:$GIT_PATH is not exist!"
				echo "Warning:$GIT_PATH is not exist!" | tee -a $merge_failed_file
				continue
			fi
			pushd $GIT_PATH
				# 创建临时分支
				git checkout -b temp_branch
				# 如果本地命名为target_branch的分支名存在，则将其删除
				if [[ $(git branch | grep "$target_branch") != "" ]];then
					echo "git branch -D $target_branch"
					git branch -D $target_branch
				fi
				# 创建本地分支
				echo "git checkout -b $target_branch origin/$target_branch"
				git checkout -b $target_branch origin/$target_branch
				git branch -D temp_branch
				
				if [[ $(echo "${gerrit_refspec[$i]}" | grep "refs/changes") != "" ]];then
					#cherry-pick gerrit临时库的最新merge到workspace的git库中
					temp_port="29418"
					if [ "${GERRIT_SERVER}" == "10.141.105.139" -o "${GERRIT_SERVER}" == "rnd-hisi-kirin-origin.ontim.com" ];then
						temp_port="39418"
					fi
					echo "git fetch ssh://${GERRIT_LOGUSER}@${GERRIT_SERVER}:${temp_port}/${gerrit_project[$i]} ${gerrit_refspec[$i]} && git cherry-pick -x FETCH_HEAD"
					git fetch ssh://${GERRIT_LOGUSER}@${GERRIT_SERVER}:${temp_port}/${gerrit_project[$i]} ${gerrit_refspec[$i]} && git cherry-pick -x FETCH_HEAD
					merge_status=$?
					# 显示merge的commit_id信息
					commit_id=$(cat .git/FETCH_HEAD | awk '{print $1}')
				else
					echo "git cherry-pick -x ${gerrit_refspec[$i]}"
					git cherry-pick -x ${gerrit_refspec[$i]}
					merge_status=$?
					commit_id=${gerrit_refspec[$i]}
				fi
				
				if [[ -f .git/MERGE_MSG ]]; then
					echo "Conflicts when cherry-pick commit $commit_id for project ${gerrit_project[$i]} from $source_branch to $target_branch" | tee -a $merge_failed_file
					echo "The conflicts files are as follows:" | tee -a $merge_failed_file
					cat .git/MERGE_MSG | tee -a $merge_failed_file
					# 将冲突文件保存到冲突目录下
					cat .git/MERGE_MSG > tmp_merge_conflict_file.cfg
					error_occur="true"
				
					# 将冲突文件进行记录
					while read oneline
					do
						code_dir=$(dirname $oneline)
						if [[ ! -d $auto_merge_log_directory/$GIT_PATH/$code_dir ]];then
							mkdir -p $auto_merge_log_directory/$GIT_PATH/$code_dir
						fi
						cp -rf $oneline $auto_merge_log_directory/$GIT_PATH/$code_dir
					done < tmp_merge_conflict_file.cfg

					rm -rf tmp_merge_conflict_file.cfg
				elif [[ "0" != "$merge_status" ]];then
					echo "Cherry-pick commit $commit_id for project:${gerrit_project[$i]} from $source_branch to $target_branch fail,please check the $auto_merge_log_directory for detail" | tee -a $merge_failed_file
					error_occur="true"
				fi
			popd
		else
			echo "Warning:$GIT_PATH is not exist!"
		fi
	done
	
	pushd $auto_merge_log_directory
	tar -zcvf merge_conflict.tar.gz *
	find . -path "./merge_conflict.tar.gz" -prune -o ! \( -iwholename "." \) -print | xargs rm -rf
	popd
	
	if [[ "$error_occur" == "true" ]];then
		echo "[$0,Line:$LINENO] Error:Cherry-pick commit $commit_id for project:${gerrit_project[$i]} from $source_branch to $target_branch fail,please check the $auto_merge_log_directory for detail!!!"
		exit "1"
	fi
	echo "===================End auto cherry pick the $source_branch branch to the $target_branch branch==================="
}

########################################  main program start ##########################################
echo "===================Start auto cherry pick the $source_branch branch's commit to the $target_branch branch==================="
# 进入到本地存放代码的目录下
pushd "$repo_local_path"

	# 创建存放自动merge log文件的目录
	if [[ -d "$auto_merge_log_directory" ]];then
		rm -rf $auto_merge_log_directory
	fi
	mkdir $auto_merge_log_directory

	# 自动merge代码
	merge_branch
popd
echo "Auto cherry pick successfull!!!"
echo "===================End auto cherry pick the $source_branch branch's commit to the $target_branch branch==================="
########################################  main program end ##########################################jslave@WUH1000103386:~/ci/workspace/Upload_hw_wh_nougat_mtk_MT6750_base_b200_zn_dviver_o
