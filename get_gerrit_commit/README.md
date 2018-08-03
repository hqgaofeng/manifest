从gerrit获取提交，并分析称excel表格
需要传入四个参数
1.分支   ----	branch_name	
2.开始时间    -----start_date
3.结束时间     ------end_date
4.状态   ------gerrit_status



#!/bin/bash

pwd
cd $WORKSPACE/tools
python export.py
