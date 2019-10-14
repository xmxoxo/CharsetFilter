#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

'''
UTF-8字符集分析过滤工具 CharsetFilter
版本: V 1.0.1
更新：xmxoxo 2019/10/14

工具说明：本工具把UTF8字符集分成了40个子集，可对文本文件中的字符集进行分析，
统计各类字符的总数以及出现的种类数。同时还可以方便地过滤或者保留的字符，
特别适合NLP等领域中对不可见字符的过滤分析等处理。

使用案例说明：

分析文本字符集，输出简要信息
python CharsetFilter.py --file ./111.txt 

分析文本字符集，输出详细信息
python CharsetFilter.py --file ./111.txt --detail 1

分析文本字符集，按默认值过滤(过滤 "尚未识别 0", "控制字符 3")，并保存过滤结果(自动命名)
python CharsetFilter.py --file ./111.txt --filter 1

分析文本字符集，仅保留 1,2,36,39，并保存过滤结果(自动命名)
python CharsetFilter.py --file ./111.txt --filter 1 --remain_charset 1 2 36 39


'''

import argparse
import os
import sys

# 读入文件
def readtxtfile(fname):
    pass
    try:
        with open(fname,'r',encoding='utf-8') as f:  
            data=f.read()
        return data
    except :
        return ''

#保存文件
def savetofile(txt,filename):
    pass
    try:
        with open(filename,'w',encoding='utf-8') as f:  
            f.write(str(txt))
        return 1
    except :
        return 0

#判断字符是否在指定的区间内
def inArea (value, lstRange):
    pass
    if not lstRange:
        return 0
    for x in lstRange:
        if type(x) == int:
            if value == x:
                return 1
        if type(x) == list:
            if x[0]<=value<=x[1]:
                return 1
        if type(x) == tuple:
            if x[0]<value<x[1]:
                return 1
    return 0
    

#unicode字符集区域判断,判断某个字符所在的字符集
def segIndex (intvalue):
    lstSeg = [
        [0x0000, 0x001F],  #不可见字符(含制表/换行/回车)
        [0x0020, 0x007E],  #英文半角(含空格)
        [0x007F, 0x00A0],  #控制字符
        [0x00A1, 0x00FF],  #扩展半角
        [0x1100, 0x11FF],  #韩文字符
        [0x1950, 0x1974],  #傣文字符
        [0x1980, 0x19DF],  #新傣文字
        (0x2010,[0x2012,0x2027],[0x2030, 0x205E]),  #标点字符
        (0x2070, 0x2071,[0x2074,0x208E],[0x2090,0x209C]) , #上标下标
        [0x2100, 0x214F],  #字母符号
        [0x2150, 0x218B],  #数字表格
        [0x2190, 0x21FF],  #箭头字符
        [0x2200, 0x22FF],  #数学符号
        [0x2300, 0x23FF],  #工程符号
        [0x2400, 0x2426],  #控制图符
        [0x2440, 0x244A],  #识别符号
        [0x2460, 0x24FF],  #序号字符
        [0x2500, 0x257F],  #制表字符
        [0x2580, 0x259F],  #方块元素
        [0x2600, 0x26FF],  #杂项符号
        [0x2700, 0x27BF],  #装饰符号
        [0x2800, 0x28FF],  #盲文符号
        [0x2E80, 0x2EF3],  #部首补充
        [0x2F00, 0x2FD5],  #康熙部首
        [0x2FF0, 0x2FFB],  #汉字结构
        [0x3001, 0x303F],  #标点符号
        [0x3040, 0x30FF],  #日文字符
        [0x3131, 0x318E],  #韩文字母
        [0x31C0, 0x31EF],  #笔划字符
        [0x31F0, 0x31FF],  #日文拼音
        [0x3200, 0x32FF],  #带框字符及月份
        [0x3300, 0x33FF],  #日期单位
        [0x3400, 0x4DB5],  #扩展汉字
        [0x4DC0, 0x4DFF],  #易经字符
        [0x4e00, 0x9fa5],  #基础汉字
        [0xA000, 0xA48C],  #彝文字符	
        [0xAC00, 0xD7A3],  #韩文字符
        [0xFF01, 0xFF65],  #全角字符
    ]
    index = -1
    for i in range(len(lstSeg)):
        x = lstSeg[i]
        if type(x)==list:
            if x[0]<=intvalue<=x[1]:
                index = i
                break
        if type(x)==tuple:
            if inArea(intvalue, x):
                index = i
                break
    return index+1

#对文本文件进行过滤,保留哪些字符集
def txtfilter (txt, delchar = [0,3,]):
    pass
    rettxt = ''
    if not txt:
        return ''

    for x in list(txt):
        index = segIndex (ord(x))
        if not index in delchar:
            rettxt += x
    return rettxt

#对文件的字符进行分析
def charAnalyze (txt, detail = 0):
    char = 0
    word = 0
    other = 0
    lstName = [
        '尚未识别',  #0 除以下标识的范围之外的字符，基本可认为是没有用的字符
        '系统字符',  #1 包括换行，制表，回车等
        '英文半角',  #2 包含数字，字母，符号，空格
        '控制字符',  #3 可删除，会影响文本处理
        '扩展半角',  #4 一些半角符号
        '韩文字符',  #5
        '傣文字符',  #6
        '新傣文字',  #7
        '标点字符',  #8
        '上标下标',  #9
        '字母符号',  #10
        '数字符号',  #11 
        '箭头字符',  #12
        '数学符号',  #13 全角数学符号
        '工程符号',  #14
        '控制图符',  #15
        '识别符号',  #16
        '序号字符',  #17 带圆圈的序号字符
        '制表字符',  #18
        '方块元素',  #19
        '杂项符号',  #20
        '装饰符号',  #21
        '盲文符号',  #22
        '部首补充',  #23
        '康熙部首',  #24
        '汉字结构',  #26
        '标点符号',  #27
        '日文字符',  #28
        '韩文字母',  #29
        '笔划字符',  #30
        '日文拼音',  #31
        '带框月份',  #32
        '日期单位',  #33
        '扩展汉字',  #34
        '易经字符',  #35 
        '基础汉字',  #36 基本汉字
        '彝文字符',  #37
        '韩文字符',  #38
        '全角字符',  #39 全角的标点符号
    ]
        
    lstret = [0 for x in range(len(lstName))]
    listWord = [dict() for x in range(len(lstName))]
    #print(txt)
    for x in list(txt):
        intv = ord(x)
        index = segIndex (intv)
        lstret[index] +=1
        wkey = x
        '''
        if showcode:
            if index ==0:
                pass
                wkey = hex(intv)
            else:
                wkey = x
        '''
        #记录
        if wkey in listWord[index].keys():
            listWord[index][wkey] += 1
        else:
            listWord[index][wkey] = 1

    #统计结果
    strResult = ''
    #print('-'*30)
    for i in range(len(lstName)):
        #除了2，35这两类，其它的都显示明细
        #and (i in [2,35]):
        if (not detail): 
            #print('字符类型:[%s] 总个数:%8d 种类:[%6d] ' %(lstName[i], lstret[i], len(listWord[i]) ))
            strResult += '[%s]: 总个数:%8d 种类:[%6d]\n' %(lstName[i], lstret[i], len(listWord[i]) )
        else:
            #print('字符类型:[%s] 总个数:%8d 种类:[%6d] \n明细：%s' %(lstName[i], lstret[i], len(listWord[i]) , listWord[i]))
            strResult += '[%s]: 总个数:%8d 种类:[%6d] \n明细：%s\n' %(lstName[i], lstret[i], len(listWord[i]) , listWord[i])
    #print(strResult)
    return strResult

#命令行
def Main_cli ():
    import sys,os

    f = "" #'./testdat/0011.txt'
    if len(sys.argv)>1:
        fn = sys.argv[1]
    else:
        fn = f
    #参数2 是否显示明细
    parm = 0
    if len(sys.argv)>2:
        parm = int(sys.argv[2])

    txt = readtxtfile(fn)
    if not txt:
        print('文件未找到!')
        return 0

    print(('[%s]字符分析' % fn).center(40,'-') )
    charAnalyze (txt, parm)
    
    print('正在过滤字符...')
    rettxt = ''
    #rettxt = txtfilter (txt)
    if rettxt:
        fn = fn[:-4] + '_out.txt'
        savetofile(rettxt,fn)
        print('文件已过滤保存为:%s' % fn)

#命令行处理
def main():
    parser = argparse.ArgumentParser(description='文本字符集分析与过滤工具')
    parser.add_argument('--file', default='',required=True, help='待处理数据文件名，必选参数')
    parser.add_argument('--detail', default=0, type=int, help='是否输出明细,默认为否')
    parser.add_argument('--filter', default=0, type=int, help='是否进行过滤处理，默认为否')
    parser.add_argument('--remove_charset', default=[0,3] , nargs='+', type=int, 
        help='指定要过滤的字符集,默认为[0,3];指定过滤字符集时将忽略保留字符集;')
    parser.add_argument('--remain_charset', default=[] , nargs='+', type=int, 
        help='指定要保留的字符集,默认为全部;指定过滤字符集时将忽略保留字符集;')
    parser.add_argument('--outfile', default='', help='过滤后的输出文件名，未指定时将自动生成')

    args = parser.parse_args()
    
    filename = args.file
    detail = args.detail
    filter = args.filter
    remove_charset = args.remove_charset
    remain_charset = args.remain_charset
    outfile = args.outfile
    #print (args)
    #print(remain_charset)
    #sys.exit()

    txt = readtxtfile(filename)
    if not txt:
        print('文件未找到!')
        return 0

    print('正在分析文件,请稍候...')
    fn = os.path.split(filename)[1]
    strRet = ('[%s]字符集分析报告' % fn).center(40,'-') + '\n'
    strRet += charAnalyze (txt, detail)
    if not detail:
        print(strRet)
    else:
        reportfn = filename[:-4] + '_report.txt' 
        savetofile(strRet,reportfn)
        print('文件分析报告保存为:%s' % reportfn)

    if filter:
        #计算过滤字符集
        if remove_charset:
            delchar = remove_charset
        else:
            delchar = list(set(range(40)).difference(set(remain_charset)))
        #生成输出文件名
        if not outfile:
            outfile = filename[:-4] + '_out.txt'    

        print('正在过滤字符...')
        rettxt = ''
        rettxt = txtfilter (txt , delchar)
        if rettxt:
            savetofile(rettxt,outfile)
            print('文件已过滤保存为:%s' % outfile)


if __name__ == '__main__':
    pass
    main()
