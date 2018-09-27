#!/usr/bin/pytyon
#coding:utf-8
import commands
import json
import time
import xml.dom.minidom
import os
import sys
import optparse


def ParseManifest(manifest=".repo/manifest.xml"):
    # parse manifest.xml file,return a list [name, path, revision, upstream]
    try:
        tree = xml.dom.minidom.parse(manifest)
    except Exception as e:
        return []
    root = tree.documentElement
    projects = root.getElementsByTagName("project")
    remotes = root.getElementsByTagName("remote")

    default = root.getElementsByTagName("default")
    defaultremote = default[0].getAttribute("remote")
    defaultrevision = default[0].getAttribute("revision")

    remotename_to_fetch = {}
    for remote in remotes:
        name = remote.getAttribute("name")
        fetch = remote.getAttribute("fetch")
        remotename_to_fetch[name] = fetch

    projects_L = []
    for pro in projects:
        path = pro.getAttribute("path")
        name = pro.getAttribute("name")
        revision = pro.getAttribute("revision")
        upstream = pro.getAttribute("upstream")
        remote = pro.getAttribute("remote")
        if revision == "":
            revision = defaultrevision
        if not path:
            path = name
        if not remote:  # this will use default remote
            fetch = remotename_to_fetch.get(defaultremote)
        else:
            fetch = remotename_to_fetch.get(remote)
        # project name in manifest,project path in local, revision, upstream, fetch path.
        pro_L = [name, path, revision, upstream, fetch]
        projects_L.append(pro_L)
    projects_L.sort()
    return projects_L
    
def ParseJsonString(jsonstr_list, commitid,default_url="androidxian.huawei.com"):
    
    patch_info_L = []
    gerrit_info_L = []
    # 这里遍历这个json的列表，其中只会有一个json的匹配的
    for json_str in jsonstr_list:
        json_D = json.loads(json_str)
        # this is a changenumber
        patchsets_L = json_D.get("patchSets", [])#好几笔case用一个changeid会产生patch set 1,patch set 2,......
        for patch in patchsets_L:                #搜索对应commitid的patch
            patch_commit_id = patch.get("revision")
            if commitid == patch_commit_id or commitid in patch_commit_id:
                subject = json_D.get("subject", unicode("error: no subject", "utf-8"))
                patch_url = json_D.get("url", default_url)
                gerrit_project = json_D.get("project", unicode("error: no project", "utf-8"))
                gerrit_branch = json_D.get("branch", unicode("error: no branch", "utf-8"))
                task_number = json_D.get("number", 0)  # repo download will use this value
                patch_number = patch.get("number",0)
                patch_authorname = patch.get("author").get("name")
                patch_authoremail = patch.get("author").get("email")

                patch_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(patch.get("createdOn")))
                patch_date = unicode(patch_date, "utf-8")
                manifest_project=gerrit_project
                patch_files_L = []
                for files in patch.get("files", []):
                    filetemp = files.get("file", "")
                    if filetemp != "/COMMIT_MSG" and filetemp != "":
                        patch_files_L.append(filetemp)

                taskid = "%s/%s" % (task_number, patch_number)
                patch_info_L = [subject, patch_authoremail, patch_authorname, patch_url, patch_commit_id, patch_date, manifest_project, taskid, patch_files_L]
                gerrit_info_L = [gerrit_project, gerrit_branch, patch_commit_id]
                # 这里如果查到匹配的就立马返回, 不然会被后续的错误结果覆盖了
                return gerrit_info_L, patch_info_L
    # end 遍历jsonstr_list
    return gerrit_info_L, patch_info_L

def QueryPatchInfo(patch_id_l,gerrit_port="29418",gerrit_url="androidxian.huawei.com"):
    #will query, get each commitID infomation,such as project,branch,author,revision,changenumber, patch number
    #return a list.
    #save query commit id.

    projects_info = {}
    #querry commit id
    for commitid in patch_id_l:
        cmd="ssh -p %s pagilecdmatc@%s gerrit query --format=JSON --current-patch-set --patch-sets --files %40s" % (gerrit_port, gerrit_url, commitid)
        status, output = commands.getstatusoutput(cmd)
        if status:
            status, output = commands.getstatusoutput("grep name ~/.gitconfig | awk -F = '{print $2}' | tr -d \" \"")
            cmd="ssh -p %s %s@%s gerrit query --format=JSON --current-patch-set --patch-sets --files %40s" % (gerrit_port, output,gerrit_url, commitid)
            status, output = commands.getstatusoutput(cmd)
        print "gerrit query cmd: [%s]" % cmd
        jsonstr_list = output.splitlines()                 #分割为内容和 {"type":"stats","rowCount":1,"runTimeMilliseconds":22,"moreChanges":false}
        json_query_status = json.loads(jsonstr_list[-1])
        if json_query_status.get("type", "") == "stats":
            rowcount = json_query_status.get("rowCount")
            if rowcount == 0:
                raise Exception("query patch error rowcount is zero")
            elif rowcount >= 1:
                # 这里gerrit查询有时候会得出多个json的字符串，但是只有一个是正确的。
                # 如果这里需要解析多个json的字符串，这里最后匹配的还是会只有一个的
                gerrit_info_L, patch_info_L = ParseJsonString(jsonstr_list[0:-1], commitid)
                if patch_info_L and gerrit_info_L:
                    gerrit_project,gerrit_branch,head = gerrit_info_L[0],gerrit_info_L[1],gerrit_info_L[2]
                    projects_info.setdefault(gerrit_project, {}).setdefault("patch_info", []).append(patch_info_L)
                    projects_info.setdefault(gerrit_project, {}).setdefault("gerrit_project", gerrit_project)
                    projects_info.setdefault(gerrit_project, {}).setdefault("gerrit_branch", gerrit_branch)
                    projects_info.setdefault(gerrit_project).setdefault("head", head)
                else:
                    raise Exception("parse json string error")
            else:
                raise Exception("query patch info rowcount error")
        else:
            raise Exception("query patch info status error")
        #end if
    #end for commitid in patch_id_l:

    return projects_info

def GenPatchInfo(patch_cfg_file, patches_info):
    save_patch_list = []
    for gerrit_project, info in patches_info.items():
        patch_info = info.get("patch_info", [])
        for patch in patch_info:
            project = patch[6] #in manifest.xml project name
            taskid = patch[7]

            save_patch_list.append("%s:%s\n" % (project, taskid))

    #save repo download info to file
    with open(patch_cfg_file, "w") as fd:
        print "save patch info to [%s] for repo download" % patch_cfg_file
        fd.writelines(save_patch_list)

        
def RepoDownloadPatch(android_code,project, refchange):
    cmd = "cd %s;%s download %s %s" % (android_code,"~/bin/repo", project, refchange)
    print "repo download cmd: [%s]" % cmd
    ret= os.system(cmd)
    if ret != 0:
        print "repo download patch fail"

def GenPatchZip(androidRoot,patch_zip_file, patches_info, manifest_file):
    if patch_zip_file.endswith(".zip"):
        patch_zip_file = patch_zip_file[0:-4]

    patch_output_path = os.path.dirname(manifest_file)
    patch_output_path = os.path.join(patch_output_path, "odvb_patch")
    if not os.path.exists(patch_output_path):
        os.makedirs(patch_output_path)

    #aaisrepo = AaisRepo(self.android_env)

    old_projects = ParseManifest(manifest_file)#manifest_file要是repo manifest保存的带revision的
    old_projects_D = {}
    for pro in old_projects:
        old_projects_D[pro[0]] = pro

    for gerrit_project, info in patches_info.items():
        patch_info = info.get("patch_info", [])
        for patch in patch_info:
            local = os.getcwd()
            project = patch[6] #in manifest.xml project name
            taskid = patch[7]
            old_revision = old_projects_D.get(project)[2]
            new_revision = patch[4]
            #print patch,new_revision,old_revision
            #return
            path = old_projects_D.get(project)[1]
            output_path = os.path.join(patch_output_path, path)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            RepoDownloadPatch(androidRoot,project, taskid)

            os.chdir(path)
            cmd = "git format-patch -o %s %s..%s" % (output_path, old_revision, new_revision)
            #git format-patch -o ${out_root}/${REPO_PATH} ${rev_manifest}..${rev_current}
            print "git format-path cmd: [%s]" % cmd
            os.system(cmd)

            os.chdir(local) #change to old worksapce

    #save output patch to zip file
    try:
        shutil.make_archive(patch_zip_file, "zip", patch_output_path)
    except Exception as e:
        print "make zip format archive file fail: %s, will try .tar.gz format" % (e)
        shutil.make_archive(patch_zip_file, "gztar", patch_output_path)
   
def RunShellScript(shellFile,*param):
    if os.path.isfile(shellFile):
        cmd="bash %s" % shellFile
        for otherarg in param:
            cmd += " \"%s\" " % (otherarg)
        print "exec shell cmd: %s" % (cmd)
        ret = os.system(cmd)
        ret >>= 8   #右移八位对应shell里面的exit的返回值
        if ret != 0:
            print "exec shell fail: %s" % (cmd)
            raise Exception("build fail")
    else:
        print shellFile,"is  not exist"

def RunShellcmd(cmd):
    print "run shell cmd: [%s]" % cmd
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("run shell cmd fail")
        
def ParseArgs():
    parser = optparse.OptionParser()

    build_option_group = optparse.OptionGroup(parser, "Build options")
    build_option_group.add_option("-c", "--code-root", dest="code_root",
                                  help="build root path", default="")                                
    build_option_group.add_option("-i", "--commit-id", dest="commit_id",
                                  help="commit id", default="")
                                                              
    parser.add_option_group(build_option_group)
    (options, args) = parser.parse_args()
    return (options, args)
    
if __name__=="__main__":
    sys.stdout = sys.stderr
    #环境变量
    (options, args) = ParseArgs()
    code_root=options.code_root.strip()
    commit_id=options.commit_id.strip()

    print "code_root:",code_root
    print "commit_id:",commit_id

    if commit_id == "":
        raise Exception("error:commit_id is not allow empty!")

    patchRoot=os.path.join(code_root,"patch")
    RunShellcmd("mkdir -p %s" %patchRoot)
       
    #查询patch信息
    commitID_L=commit_id.split(",")
    patches_info=QueryPatchInfo(commitID_L)
    patch_cfg_file = os.path.join(patchRoot, "patch.cfg")
    GenPatchInfo(patch_cfg_file, patches_info)
    
    #下载patch
    RunShellScript("odvb_down_patch.sh",code_root)



