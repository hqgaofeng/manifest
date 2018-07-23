#!/usr/bin/python
# coding:utf-8
import os
import xlwt
import xlrd
import sys
import re
#reload(sys)
#sys.setdefaultencoding('gbk')
#防止处理汉字时报错
reload(sys)
sys.setdefaultencoding('utf8')

class excel(object):
    def __init__(self,excel_file=None):
        if excel_file:
            self.workbook=xlrd.open_workbook(excel_file)
        else:
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


def ReadFromExcel(excel_file):
    excs=excel(excel_file)
    sheet_lable='open'
    sheet = excs.workbook.sheet_by_name(sheet_lable)
    rows = sheet.nrows
    print 'starting to read excel table.......','Total apks:',rows-1
    #f=open('apk_list.txt','w')
    for i in range(rows):  # 循环逐行打印
        if i < 1:  # 跳过第一行
            continue
        col0=(sheet.row_values(i)[0]).strip()
        col1=(sheet.row_values(i)[1]).strip()
        col2=(sheet.row_values(i)[2]).strip()
        col3=(sheet.row_values(i)[3]).strip()
        col4=(sheet.row_values(i)[4]).strip()
        col5=(sheet.row_values(i)[5]).strip()
        col6=(sheet.row_values(i)[6]).strip()
        col7=(sheet.row_values(i)[7]).strip()
        col8=(sheet.row_values(i)[8]).strip()
        #f.write(business)
        print col0,col1,col2,col3,col4,col5,col6,col7,col8
    #f.close()



def ExportResultToExcel(srcfile_list,destfile):
    
    excs=excel()
    sheet = excs.workbook.add_sheet('open', cell_overwrite_ok=True)
    excs.SetCaption(sheet)
    #恢复原状
    font=excs.GetFont(bold = False)
    alignment=excs.GetAlignment(xlwt.Alignment.HORZ_LEFT)
    style=excs.GetStyle(font,excs.GetBorders(),alignment)
    Write2Sheet(sheet,srcfile_list[0],style)
    if len(srcfile_list) ==1:
        excs.workbook.save(destfile)
        return
    sheet = excs.workbook.add_sheet('open_not_Verified', cell_overwrite_ok=True)
    excs.SetCaption(sheet)
    Write2Sheet(sheet,srcfile_list[1],style)
    sheet = excs.workbook.add_sheet('wait_merge', cell_overwrite_ok=True)
    excs.SetCaption(sheet)
    Write2Sheet(sheet,srcfile_list[2],style)
    excs.workbook.save(destfile)
    print 'export finished!'

def SetCaption(excel,sheet,line=0):
    #设置列宽
    sheet.col(0).width=256*65
    sheet.col(1).width=256*40
    sheet.col(2).width=256*45
    sheet.col(3).width=256*10
    sheet.col(4).width=256*40
    sheet.col(5).width=256*25
    sheet.col(6).width=256*40
    sheet.col(7).width=256*30
    sheet.col(8).width=256*10
    sheet.col(9).width=256*40
    #设置行高
    tall_style = xlwt.easyxf('font:height 480;')# 24pt
    sheet.row(0).set_style(tall_style)
    #设置标题
    style=excel.GetStyle(excel.GetFont(),excel.GetBorders(),excel.GetAlignment())
    sheet.write(line, 0, 'project',style)
    sheet.write(line, 1, 'branch',style)
    sheet.write(line, 2, 'id',style)
    sheet.write(line, 3, 'number',style)
    sheet.write(line, 4, 'DTS',style)
    sheet.write(line, 5, 'name',style)
    sheet.write(line, 6, 'url',style)
    sheet.write(line, 7, 'lastUpdated',style)
    sheet.write(line, 8, 'status',style)
    sheet.write(line, 9, 'topic',style)

def Write2Sheet(sheet,file,style):
    with open(file,'r') as f:
        num = 0
        for i in f:
            info=i.strip()
            info=re.split('\t',i)
            if len(info)<=1:
                continue
            #print info
            #continue
            if num==0:
                num+=1
                continue
            sheet.write(num, 0, info[0],style)
            sheet.write(num, 1, info[1],style)
            sheet.write(num, 2, info[2],style)
            sheet.write(num, 3, info[3],style)
            sheet.write(num, 4, info[4],style)
            sheet.write(num, 5, info[5],style)
            sheet.write(num, 6, xlwt.Formula('HYPERLINK("'+ info[6] +'")'),style)
            sheet.write(num, 7, info[7],style)
            sheet.write(num, 8, info[8],style)
            sheet.write(num, 9, "",style)
            num+=1
    return 0

if __name__ == "__main__":
    #srcfile=sys.argv[1]
    #destfile=sys.argv[2]
    #srcfile_list=srcfile.split(' ')
    #ExportResultToExcel(srcfile_list,destfile)
    ReadFromExcel(os.path.join(os.getcwd(),'result.xls'))
    pass
