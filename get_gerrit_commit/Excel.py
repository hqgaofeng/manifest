#!/usr/bin/python
# coding:utf-8
import os
import xlwt
import sys
import re
import commands

class excel(object):
    def __init__(self):
        self.workbook = xlwt.Workbook(encoding = 'utf-8')
        
    def GetFont(self,name = 'Tahoma',bold = True,height = 11*20,color=0):
        font = xlwt.Font()
        font.name = name
        font.bold = bold
        font.height = height#11号字体 11*20
        font.colour_index=color#黑色
        return font
    
    def GetBorders(self,left=1,right=1,top=1,bottom=1):
        borders = xlwt.Borders()
        borders.left = left                                   
        borders.right = right                                        
        borders.top = top                                        
        borders.bottom = bottom
        return borders

    def GetAlignment(self,horz=xlwt.Alignment.HORZ_CENTER,vert=xlwt.Alignment.VERT_CENTER):
        alignment = xlwt.Alignment()
        alignment.horz = horz
        alignment.vert = vert
        return alignment
        
    def GetStyle(self,font,borders,alignment):
        style = xlwt.XFStyle()
        #边框                                      
        style.borders = borders
        #字体
        style.font=font
        #居中
        style.alignment = alignment
        return style

    def SetCaption(self,sheet,line=0):
        #设置列宽
        sheet.col(5).width=256*40
        sheet.col(4).width=256*40
        sheet.col(6).width=256*35
        sheet.col(7).width=256*10
        sheet.col(2).width=256*40
        sheet.col(1).width=256*25
        sheet.col(0).width=256*40
        sheet.col(3).width=256*30
        sheet.col(8).width=256*10
        sheet.col(9).width=256*40
        #设置行高
        tall_style = xlwt.easyxf('font:height 480;')# 24pt
        sheet.row(0).set_style(tall_style)
        #设置标题
        style=self.GetStyle(self.GetFont(),self.GetBorders(),self.GetAlignment())
        sheet.write(line, 5, 'project',style)
        sheet.write(line, 4, 'branch',style)
        sheet.write(line, 6, 'id',style)
        sheet.write(line, 7, 'number',style)
        sheet.write(line, 2, 'DTS',style)
        sheet.write(line, 1, 'name',style)
        sheet.write(line, 0, 'url',style)
        sheet.write(line, 3, 'lastUpdated',style)
        sheet.write(line, 8, 'status',style)
        sheet.write(line, 9, 'topic',style)
        sheet.write(line, 10, 'insert',style)
        sheet.write(line, 11, 'delete',style)

def ExportResultToSheet(results,excs,sheet_name):
    
    sheet = excs.workbook.add_sheet(sheet_name, cell_overwrite_ok=True)
    excs.SetCaption(sheet)
    #恢复原状
    font=excs.GetFont(bold = False)
    alignment=excs.GetAlignment(xlwt.Alignment.HORZ_LEFT)
    style=excs.GetStyle(font,excs.GetBorders(),alignment)
    Write2Sheet(sheet,results,style)

def Write2Sheet(sheet,results,style):

    num=1
    for result in results:
        sheet.write(num, 0, xlwt.Formula('HYPERLINK("'+ result['url'] +'")'),style)
        sheet.write(num, 1, result['owner']['name'],style)
        sheet.write(num, 2, result['subject']['TicketNo'],style)
        sheet.write(num, 3, result['lastUpdated'],style)
        sheet.write(num, 4, result['branch'],style)
        sheet.write(num, 5, result['project'],style)
        sheet.write(num, 6, result['id'],style)
        sheet.write(num, 7, result['url'].split('/')[-1],style)
        sheet.write(num, 8, 'NEW',style)
        sheet.write(num, 9, "",style)
        sheet.write(num, 10,result['patchSets'][-1]['sizeInsertions'],style)
        sheet.write(num, 11,result['patchSets'][-1]['sizeDeletions'],style)
        num+=1
    return 0

if __name__ == "__main__":
    srcfile=sys.argv[1]
    destfile=sys.argv[2]
    srcfile_list=srcfile.split(' ')
    ExportResultToExcel(srcfile_list,destfile)
















