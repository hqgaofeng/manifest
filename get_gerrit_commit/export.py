#!/usr/bin/pytyon
#coding:utf-8
import os
import sys
import pprint
import shutil
from gerritEx import gerritEx
from Excel import *

def format_print(result):
    print '\n'
    print 'url:',result['url']#url 1
    print 'owner:',result['owner']['name']#name 2
    print 'TicketNo:',result['subject']['TicketNo']
    print 'lastUpdated:',result['lastUpdated']
    print 'branch:',result['branch']
    print 'project:',result['project']
    print 'change_id:',result['id']
    print 'number:',result['url'].split('/')[-1]
    print 'status:','NEW'
    print 'topic:',''
    print 'insert:',result['patchSets'][-1]['sizeInsertions']
    print 'delete:',result['patchSets'][-1]['sizeDeletions']

def log(tag,results):
    print '*'*40+tag+'*'*40
    for i in results:format_print(i)

if __name__ == '__main__':

    branch_name=os.environ.get('branch_name')
    start_date=os.environ.get('start_date')
    end_date=os.environ.get('end_date')
    gerrit_status=os.environ.get('gerrit_status')#open,merged
    workspace=os.environ.get('WORKSPACE')
    destfile=os.path.join(workspace,'result.xls')
    
    gerrit=gerritEx()
    excs=excel()

    if gerrit_status=='open':
        #------所有打开状态查询
        cmd="--format=JSON --patch-sets before:%s after:%s status:open branch:%s" %(end_date,start_date,branch_name)
        open_query=gerrit.query(cmd)
        log('open',open_query[0])
        ExportResultToSheet(open_query[0],excs,'open')
        
        #-----所有打开状态中门禁没+1
        cmd="--format=JSON --patch-sets before:%s after:%s is:open NOT label:Verified+1 branch:%s" %(end_date,start_date,branch_name)
        open_NoV1_query=gerrit.query(cmd)
        log('open_NoV1',open_NoV1_query[0])
        ExportResultToSheet(open_NoV1_query[0],excs,'open_NoV1')
        
        #-----所有打开状态中门禁+1
        #cmd="--format=JSON --patch-sets before:%s after:%s is:open label:Verified+1 branch:%s" %(end_date,start_date,branch_name)
        #open_V1_query=gerrit.query(cmd)
        #ExportResultToSheet(open_V1_query[0],excs,'open_V1')
        
        #-----所有打开状态中门禁+1,Code-Review没+1
        cmd="--format=JSON --patch-sets before:%s after:%s is:open label:Verified+1 NOT Code-Review+1 branch:%s" %(end_date,start_date,branch_name)
        open_V1_NoCR1_query=gerrit.query(cmd)
        log('open_V1_NoCR1',open_V1_NoCR1_query[0])
        ExportResultToSheet(open_V1_NoCR1_query[0],excs,'open_V1_NoCR1')
        
        #-----所有打开状态中门禁+1,Code-Review+1,Code-Review没+2
        cmd="--format=JSON --patch-sets before:%s after:%s is:open label:Verified+1 Code-Review+1 NOT Code-Review+2 branch:%s" %(end_date,start_date,branch_name)
        open_V1_CR1_NoCR2_query=gerrit.query(cmd)
        log('open_V1_CR1_NoCR2',open_V1_CR1_NoCR2_query[0])
        ExportResultToSheet(open_V1_CR1_NoCR2_query[0],excs,'open_V1_CR1_NoCR2')
    elif gerrit_status=='merged':
        cmd="--format=JSON --patch-sets before:%s after:%s status:merged branch:%s" %(end_date,start_date,branch_name)
        merged_query=gerrit.get_query_all(cmd)
        log('merged',merged_query)
        ExportResultToSheet(merged_query,excs,'merged')

    excs.workbook.save(destfile)
