#!/usr/bin/python
# coding:utf-8
import os
import xml
import xml.dom.minidom as dom
import codecs

#更多信息参考http://www.w3school.com.cn/x.asp
class xmlExt(object):
    def __init__(self,xml_file):
        self.tree = dom.parse(xml_file)#document
        self.root = self.tree.documentElement

# ==由于minidom默认的writexml()函数在读取一个xml文件后，修改后重新写入如果加了newl='\n',会将原有的xml中写入多余的行
#　 ==因此使用下面这个函数来代替
def writexml_ex(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        dom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == dom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            if node.nodeType is not dom.Node.TEXT_NODE:
                node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))

dom.Element.writexml = writexml_ex

def ParseXml(xml_file):        
    xmls=xmlExt(xml_file)
    #read
    prop_nodes = xmls.root.getElementsByTagName("prop")
    print prop_nodes
    prop_childs=prop_nodes[0].getElementsByTagName("modify")
    print prop_childs
    modify_property=prop_childs[0].getAttribute("default_update_file")
    print modify_property
    modify_childs=prop_childs[0].getElementsByTagName("property")
    print modify_childs
    for i in modify_childs:
        name=i.getAttribute("name")
        value=i.getAttribute("value")
        print name,value
    modify_childs_1=prop_childs[0].getElementsByTagName("other")
    print modify_childs_1[0].childNodes[0].data

    print prop_nodes[0].getElementsByTagName("property")
    
def CreateXml():
    # =====从一个空xml文档开始
    impl = xml.dom.getDOMImplementation()
    dom = impl.createDocument(None,'All_Students',None)
    root = dom.documentElement
    # --创建一个节点，并添加到root下
    student = dom.createElement('student')
    root.appendChild(student)
    # --创建一个子节点，并设置属性
    nameE = dom.createElement('name')
    value = u'陈奕迅'
    nameE.setAttribute("attr",value)
    nameN = dom.createTextNode(value)
    nameE.appendChild(nameN)
    student.appendChild(nameE)
    # -- 写进文件,如果出现了unicode，指定文件的编码
    f = codecs.open('1.xml','w','utf-8')
    dom.writexml(f,addindent='  ',newl='\n',encoding = 'utf-8')
    f.close()

def AddNode():
    xmls=xmlExt('1.xml')
    age = xmls.tree.createElement('age')
    value = '50'
    age.setAttribute("attr",value)
    ageN = xmls.tree.createTextNode(u'年龄')
    age.appendChild(ageN)
    
    student=xmls.root.getElementsByTagName("student")
    student[0].appendChild(age)
    
    f = codecs.open('1.xml','w','utf-8')
    xmls.tree.writexml(f,addindent='  ',newl='\n',encoding = 'utf-8')
    f.close()
    
def ModifyNode():
    xmls=xmlExt('1.xml')
    age=xmls.root.getElementsByTagName("age")
    age[0].setAttribute("attr",'100')
    age[0].childNodes[0].data=u'超龄'
    f = codecs.open('1.xml','w','utf-8')
    xmls.tree.writexml(f,addindent='  ',newl='\n',encoding = 'utf-8')
    f.close()
    
def DeleteNode():
    xmls=xmlExt('1.xml')
    #age=xmls.root.getElementsByTagName("age")
    # --删除节点属性
    #age[0].removeAttribute('attr')
    # --删除节点,必须先要获取要删除节点的父节点，用父节点removeChild删除节点
    age=xmls.root.getElementsByTagName('age')
    age_node=age[0]
    age_node.parentNode.removeChild(age_node)
    f = codecs.open('1.xml','w','utf-8')
    xmls.tree.writexml(f,addindent='  ',newl='\n',encoding = 'utf-8')
    f.close()
    
if __name__ == "__main__":

    #ParseXml(os.path.join('C:\Users\zwx526175\Downloads','product.xml'))
    #CreateXml()
    #AddNode()
    #ModifyNode()
    DeleteNode()

    
