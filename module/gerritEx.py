'''
Created on 2018-6-12

@author: zWX526175
'''
#!/usr/bin/pytyon
#coding:utf-8

import sys
import commands
import subprocess
import json
import pprint
import re
import time
import paramiko

'''resolve execute commands.getoutput exception'''
def getoutputWindow(cmd):
    pipe = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE).stdout
    return pipe.read()

commands.getoutput=getoutputWindow

'''
return type is a dict list , dict struct as following:
{u'branch':,
 u'commitMessage':,
 u'createdOn':,
 u'id': ,
 u'lastUpdated':,
 u'number':,
 u'open':,
 u'owner': {u'email':,
            u'name':,
            u'username':},
 u'project': ',
 u'status': ,
 u'subject': {'Description':,
              'TicketNo': },
 u'url':}
 '''
class gerritEx(object):
    def __init__(self,host="google.com",port="29418",user="pagilecdmatc"):
        self.cmd="ssh -p %s %s@%s gerrit query"%(port,user,host)
   
    '''type,rowCount,runTimeMilliseconds,moreChanges''' 
    '''get less than 500 results'''
    def query(self,cmd):
        result=[]
        cmd=self.cmd+' '+cmd      
        output=commands.getoutput(cmd)
        lines=output.splitlines()
        extra_info_re=re.compile('TicketNo:(.*) Description:(.*)')
        for jsonstr in lines[0:-1]:
            json_query_status = json.loads(jsonstr)
            '''get TicketNo and Description'''
            subject=json_query_status.get("subject")
            info=extra_info_re.match(subject)
            if info:
                TicketNo=info.group(1)
                Description=info.group(2)
            else:
                TicketNo=""
                Description=""
            json_query_status['subject']={'TicketNo':TicketNo,'Description':Description}
            
            '''format date time'''
            createdOn=json_query_status.get("createdOn")
            lastUpdated=json_query_status.get("lastUpdated")
            x = time.localtime(createdOn)
            json_query_status['createdOn']=time.strftime('%Y-%m-%d %H:%M:%S',x)
            x = time.localtime(lastUpdated)
            json_query_status['lastUpdated']=time.strftime('%Y-%m-%d %H:%M:%S',x)
            result.append(json_query_status)

        status=json.loads(lines[-1])
        return result,status
    
    '''get more than 500 results'''
    def get_query_all(self,cmd):
        patches=[]
        result,status=self.query(cmd)
        patches.extend(result)
        i=0
        SEGMENT=500
        while status.get("moreChanges"):
            i+=1
            cmds=cmd + " " + "--start" + " " + str(i*SEGMENT)
            print cmds
            result,status=self.query(cmds)
            patches.extend(result)
        return patches


class git(object):
        
    def excute_in_host(self,cmd,hostname='10.119.34.170',username='jslave',password='jslave123'):
        s=paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(hostname=hostname, username=username, password=password)
        stdin,stdout,stderr=s.exec_command(cmd)
        return stdout.read()
    
    def git_command(self,gitcmd,gitpath=None,revision=None,paras=None):
        #gitcmd='git log'
        gitpath='workspace/*Main/android_code/vendor/mediatek/proprietary/packages/apps/HwContacts'
        revision=['a6aa3fb5ac2db2c0017eb3c8edd1463c463a884d','4f62526379ebb67ab966658f6c9345139326a7b5']
        #paras=['--pretty="format:%H"']
        
        if gitpath:
            cmd='cd %s;'% gitpath
        cmd=cmd + gitcmd
        if revision:
            cmd=cmd + ' ' + '...'.join(revision)
            
        if paras:
            cmd=cmd + ' ' + ' '.join(paras)
        print cmd
        return self.excute_in_host(cmd)


if __name__ == '__main__':
    
    #===========================================================================
    # cmd="--format=JSON before:2018-06-13 after:2018-03-01 status:merged branch:hw/cbg/android/mtk_alps_o1/Trunk_Dura_20171226"
    #query=gerritEx()
    # patches=query.get_query_all(cmd)
    # print len(patches)
    #===========================================================================
    
    #cmd='cd workspace/*Main/android_code/vendor/mediatek/proprietary/packages/apps/HwContacts;git log a6aa3fb5ac2db2c0017eb3c8edd1463c463a884d...4f62526379ebb67ab966658f6c9345139326a7b5  --pretty=\"format:%H\"'
    g=git()
    commit=g.git_command('git log',paras=['--pretty=%H'])
    commits=commit.splitlines()
    print commits
    query=gerritEx()
    for i in commits:
        cmd="--format=JSON --patch-sets --files status:merged branch:hw/cbg/android/mtk_alps_o1/Trunk_Dura_20171226 commit:%s"%i
        #print cmd
        result,status=query.query(cmd)
        if result:
            print 
            
    
    

    
