#!/bin/bash

rm -fr $WORKSPACE/tmmp
rm -fr $WORKSPACE/tmp
mkdir $WORKSPACE/tmmp

###-----------------------
function get_result(){
file_path=$WORKSPACE/tmmp/$1.txt
#echo  $'project\tbranch\tid\tnumber\tNb\tDescription\tname\turl\tlastUpdated\tstatus\ttopic\n' > $WORKSPACE/tmmp/$1_result.txt
echo  $'project\tbranch\tid\tnumber\tNb\tname\turl\tlastUpdated\tstatus\ttopic\n' > $WORKSPACE/tmmp/$1_result.txt
cat $file_path | gawk '
BEGIN {
    RS = "\nchange I";
    FS = "\n";
	
	regex_change = "change:[[:blank:]]*"
	regex_project = "^[[:blank:]]*project:[[:blank:]]*"
	regex_branch = "^[[:blank:]]*branch:[[:blank:]]*"
	regex_id = "^[[:blank:]]*id:[[:blank:]]*"
	regex_number = "^[[:blank:]]*number:[[:blank:]]*"
	regex_subject ="^[[:blank:]]*subject:[[:blank:]]*"
        regex_Nb_pre = "^[[:blank:]]*subject:[[:blank:]]*Nb:[[:blank:]]*"	
	regex_Nb_post= "[[:blank:]]*Description.*"
	#regex_Description= "^[[:blank:]]*subject:.*Description:[[:blank:]]*"					
        regex_name = "[[:blank:]]*name:[[:blank:]]*"
	regex_url = "[[:blank:]]*url:[[:blank:]]*"		
 	regex_lastUpdated_pre =	"[[:blank:]]*lastUpdated:[[:blank:]]*"
	regex_lastUpdated_post = "[[:blank:]]*CST"
	regex_status = 	"^[[:blank:]]*status:[[:blank:]]*"
	regex_topic = "^[[:blank:]]*topic:[[:blank:]]*"	
	}
{
    
    #chang = $1
    #gsub(regex_change, "", chang);
	project=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_project))
        {
            project= $i;
			gsub(regex_project, "", project);
            break;
        }
	
	}
        branch=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_branch))
        {
			branch = $i
			gsub(regex_branch, "", branch);
	  }
	
	}
	id=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_id))
        {
			id = $i
			gsub(regex_id, "", id);
	 }
	
	}
	number=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_number))
        {
			number = $i
			gsub(regex_number, "", number);
	 }
	
	}
	Nb=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_subject))
        {
			Nb= $i
			Description = $i
			gsub(regex_Nb_pre, "", Nb);
			gsub(regex_Nb_post, "", Nb);
			gsub(regex_Description, "", Description);
		}
	
	}
	lastUpdated=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_name))
        {
			name= $i
			gsub(regex_name, "", name);
		}
	
	}
	url=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_url))
        {
            url= $i;
			gsub(regex_url, "", url);
            break;
        }
	
	}
	lastUpdated=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_lastUpdated_pre))
        {
            lastUpdated= $i;
			gsub(regex_lastUpdated_pre, "", lastUpdated);
			gsub(regex_lastUpdated_post, "", lastUpdated);	
            break;
        }
	}
	status=NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_status))
        {
            status= $i
			gsub(regex_status, "", status);	
            break;
        }
    }
	topic = NA
	for (i = NF; i > 0; i--) {
        if (match($i, regex_topic))
        {
			topic = $i
			#printf("%s", topic)
			gsub(regex_topic, "", topic);
		}
	  }
	#printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", project, branch, id, number, Nb, Description, name, url, lastUpdated, status);
        printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", project, branch, id, number, Nb, name, url, lastUpdated, status);



}' | tee $WORKSPACE/tmp
cat $WORKSPACE/tmp >> $WORKSPACE/tmmp/$1_result.txt
rm $WORKSPACE/tmp
}
####---------------------------

#-----------高峰------------
if [ $gerrit_status == "open" ] ;then
    echo "ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date  status:open branch:$branch_name"
    ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date status:open branch:$branch_name limit:10000 > $WORKSPACE/tmmp/${end_date}_open.txt
    get_result ${end_date}_open
    echo "ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date  is:open NOT label:Verified+1 branch:$branch_name"
    ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date is:open NOT label:Verified+1 branch:$branch_name limit:10000 > $WORKSPACE/tmmp/${end_date}_open_not_Verified.txt
    get_result ${end_date}_open_not_Verified
    echo "ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date  is:open label:Verified+1 branch:$branch_name"
    ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date is:open label:Verified+1 branch:$branch_name limit:10000 > $WORKSPACE/tmmp/${end_date}_wait_merge.txt
    get_result ${end_date}_wait_merge
    python $WORKSPACE/tools/write2exel.py "$WORKSPACE/tmmp/${end_date}_open_result.txt $WORKSPACE/tmmp/${end_date}_open_not_Verified_result.txt $WORKSPACE/tmmp/${end_date}_wait_merge_result.txt" "$WORKSPACE/result.xls"
else
    echo "ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date status:$gerrit_status branch:$branch_name"
    ssh intoyv@intoyv.com -p 29418 gerrit query before:$end_date after:$start_date status:$gerrit_status branch:$branch_name limit:10000 > $WORKSPACE/tmmp/${end_date}_merge.txt
    get_result ${end_date}_merge
    python $WORKSPACE/tools/write2exel.py "$WORKSPACE/tmmp/${end_date}_merge_result.txt" "$WORKSPACE/result.xls"
fi
#-----------高峰------------

