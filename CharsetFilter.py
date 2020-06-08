#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

'''
UTF-8字符集分析过滤工具 CharsetFilter
版本: V 1.0.3
更新：xmxoxo 2020/6/8

工具说明：本工具把UTF8字符集分成了39个子集，可对文本文件中的字符集进行分析，
统计各类字符的总数以及出现的种类数。同时还可以方便地过滤或者保留的字符，
特别适合NLP等领域中对不可见字符的过滤分析等处理。

注: 被分析的文本文件需要是UTF8格式

使用案例说明：

分析文本字符集，输出简要信息
python CharsetFilter.py --file ./111.txt 

分析文本字符集，输出详细信息，详细信息会保存到 xxx_report.txt 文件中
python CharsetFilter.py --file ./111.txt --report --detail

分析文本字符集，按默认值过滤(过滤 "尚未识别 0", "控制字符 3")，并保存过滤结果(自动命名)
python CharsetFilter.py --file ./111.txt --filter

分析文本字符集，仅保留 1,2,36,39，并保存过滤结果(自动命名)
python CharsetFilter.py --file ./111.txt --filter --remain 1 2 36 39

'''

import argparse
import os
import sys
import time

gblVersion = '1.0.3'

# 全局字典
gbl_lstName = [
    '其它字符',  #0 除以下标识的范围之外的字符，基本可认为是不可显示字符
    '系统字符',  #1 仅含三个：换行，制表，回车
    '英文半角',  #2 包含数字，字母，符号，空格
    '控制字符',  #3 非显示字符；
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
    '补充符号',  #23
    '部首补充',  #24
    '康熙部首',  #25
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

gbl_lstSeg = [
    ([0x0009, 0x000A, 0x000D]),  #1系统字符(保留制表/换行/回车)
    [0x0020, 0x007E],  #2英文半角(含空格)
    [0x007F, 0x00A0],  #3控制字符
    ([0x00A1, 0x076D], 
        [0x00780, 0x07B1], [0x07C0, 0x07fa], [0x0901,0x0E5B],
        [0X0E81, 0X0EDD],[0X0F00, 0X0FD4], [0x10D0,0x10FC], 0x1100),  #4扩展半角 
    [0x1101, 0x11FF],  #5韩文字符
    [0x1950, 0x1974],  #6傣文字符
    [0x1980, 0x19DF],  #7新傣文字
    (0x2010, [0x2012, 0x2027], [0x2030, 0x205E]),  #8标点字符
    (0x2070, 0x2071, [0x2074,0x208E], [0x2090,0x209C]) , #9上标下标
    [0x2100, 0x214F],  #10字母符号
    [0x2150, 0x218B],  #11数字表格
    [0x2190, 0x21FF],  #12箭头字符
    [0x2200, 0x22FF],  #13数学符号
    [0x2300, 0x23FF],  #14工程符号
    [0x2400, 0x2426],  #15控制图符
    [0x2440, 0x244A],  #16识别符号
    [0x2460, 0x24FF],  #17序号字符
    [0x2500, 0x257F],  #18制表字符
    ([0x2580, 0x2595], [0x25A0, 0x25FF],  0x25FD, 0x25FE),  #19方块元素
    ([0x2600, 0x26AF], [0x26B3,0x26BE], 
        0x26C4, 0x26C5, 0x26CE, 0x26D4, 
        0x26EA, 0x26F2, 0x26F3, 0x26F5, 0x26FA, 0x26FD),  #20杂项符号
    ([0x2701, 0x275E], [0x2761,0x27BF], 
        [0x27D0, 0x27EB], [0x27F0,0x27FF]),  #21装饰符号
    [0x2800, 0x28FF],  #22盲文符号  
    [0x2900, 0x2AFF],  #23补充符号
    [0x2E80, 0x2EF3],  #24部首补充
    [0x2F00, 0x2FD5],  #25康熙部首
    [0x2FF0, 0x2FFB],  #26汉字结构
    [0x3001, 0x303F],  #27标点符号
    [0x3040, 0x30FF],  #28日文字符
    [0x3131, 0x318E],  #29韩文字母
    [0x31C0, 0x31EF],  #30笔划字符
    [0x31F0, 0x31FF],  #31日文拼音
    [0x3200, 0x32FF],  #32带框字符
    [0x3300, 0x33FF],  #33日期单位
    [0x3400, 0x4DB5],  #34扩展汉字
    [0x4DC0, 0x4DFF],  #35易经字符
    [0x4e00, 0x9fa5],  #36基础汉字
    [0xA000, 0xA48C],  #37彝文字符	
    [0xAC00, 0xD7A3],  #38韩文字符
    (0xFE49, 0xFE51, 0xFE63, [0xFF01, 0xFF4F], [0xFFE0, 0xFFEE], 0xFFFC,0xFFFD),  #39全角字符
]

# 初始化二分法查找序号
gbl_lstIndex = [
    [0x0009, 0x000D],
    [0x0020, 0x007E],
    [0x007F, 0x00A0],
    [0x00A1, 0x1100],
    [0x1101, 0x11FF],
    [0x1950, 0x1974],
    [0x1980, 0x19DF],
    [0x2010, 0x205E],
    [0x2070, 0x209C],
    [0x2100, 0x214F],
    [0x2150, 0x218B],
    [0x2190, 0x21FF],
    [0x2200, 0x22FF],
    [0x2300, 0x23FF],
    [0x2400, 0x2426],
    [0x2440, 0x244A],
    [0x2460, 0x24FF],
    [0x2500, 0x257F],
    [0x2580, 0x25BD],
    [0x2600, 0x26FF],
    [0x2700, 0x27BF],
    [0x2800, 0x28FF],
    [0x2900, 0x2AFF],
    [0x2E80, 0x2EF3],
    [0x2F00, 0x2FD5],
    [0x2FF0, 0x2FFB],
    [0x3001, 0x303F],
    [0x3040, 0x30FF],
    [0x3131, 0x318E],
    [0x31C0, 0x31EF],
    [0x31F0, 0x31FF],
    [0x3200, 0x32FF],
    [0x3300, 0x33FF],
    [0x3400, 0x4DB5],
    [0x4DC0, 0x4DFF],
    [0x4e00, 0x9fa5],
    [0xA000, 0xA48C],
    [0xAC00, 0xD7A3],
    [0xFE49, 0xFFFD],
]

#经过的秒数 转成 时间长度
def getSpanTimes (lngTimeSpan):
    import time
    t = time.gmtime(float(round(lngTimeSpan,3)))
    #print(t)
    total_time = ''
    total_time += ('%d Years,'  % (t.tm_year-1970)) if t.tm_year>1970 else '' 
    total_time += ('%d Months,' % (t.tm_mon-1)) if t.tm_mon>1 else '' 
    total_time += ('%d Days '   % (t.tm_mday-1)) if t.tm_mday>1 else '' 
    total_time += time.strftime("%H:%M:%S", t)
    return total_time
    
# 核心类
class CharsetFilter():
    def __init__(self):
        pass

    # 读入文件
    @staticmethod
    def readtxtfile(fname):
        pass
        try:
            with open(fname,'r',encoding='utf-8') as f:  
                data=f.read()
            return data
        except :
            return ''

    # 保存文件
    @staticmethod   
    def savetofile(txt,filename):
        pass
        try:
            with open(filename,'w',encoding='utf-8') as f:  
                f.write(str(txt))
            return 1
        except :
            return 0

    #判断字符是否在指定的区间内
    @staticmethod
    def inArea (value, lstRange):
        pass
        if not lstRange:
            return False
        if type(lstRange) == list:
            if lstRange[0]<=value<=lstRange[1]:
                return 1
        if type(lstRange) == tuple:
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
        return False
   
    # 二分法查找，字符集区域判断 【2020/3/11】
    # 返回字符集索引号1-38
    def segIndex (self, intvalue):
        index = -1
        b = 0
        e = len(gbl_lstIndex)
        
        # 两端的极值优先过滤
        if intvalue<gbl_lstIndex[0][0] or intvalue> gbl_lstIndex[e-1][1]:
            return 0
        #print(intvalue)
        while 1:
            pos = (e+b) // 2
            #print('pos: %d, b: %d, e: %d ' % (pos,b,e) )
            x = gbl_lstIndex[pos]
            if x[0]<=intvalue<=x[1]:    
                index = pos
                break
            if pos==e==b:break
            if x[0]>intvalue: e = pos
            if x[1]<intvalue: b = pos+1
        
        # 详细判断
        if 0<=index<=e:
            #print(index, gbl_lstSeg[index])
            if self.inArea(intvalue, gbl_lstSeg[index]):
                index = pos
            else:
                index = -1
        
        return index+1


    '''
    对文本进行过滤, 
    remove: 删除哪些字符集，
         如果 remove 和 remain 同时未指定，则 remove = [0,3]
    remain: 保留哪些字符集，
    '''
    def txtfilter (self, txt, remove=[], remain = []):
        rettxt = ''
        if not txt:
            return ''

        #计算过滤字符集
        if not remove :
            if not remain:
                # 默认过滤 0,3
                remove = [0, 3]
            else:
                remove = list(range(40))
        delchar = list(set(range(40)).difference(set(remain)) & set(remove))

        for x in list(txt):
            index = self.segIndex (ord(x))
            if not index in delchar:
                rettxt += x
        return rettxt

    # 对文本进行分析, detail=1返回明细
    def charAnalyze (self, txt, detail=0):
        lstret = [0 for x in range(len(gbl_lstName))]
        listWord = [dict() for x in range(len(gbl_lstName))]
        for x in list(txt):
        #for x in iter(txt):
        #for i in range(len(txt)):
            #x = txt[i]
            intv = ord(x)
            index = self.segIndex (intv)
            lstret[index] +=1
            #记录
            if x in listWord[index].keys():
                listWord[index][x] += 1
            else:
                listWord[index][x] = 1

        # 统计结果
        strResult = ''
        for i in range(len(gbl_lstName)):
            if not detail: 
                strResult += '%2d-[%s] 总数:%10d  种类:[%8d]\n' %(i,gbl_lstName[i], lstret[i], len(listWord[i]) )
            else:
                strResult += '%2d-[%s] 总数:%10d  种类:[%8d]\n明细：%s\n' %(i,gbl_lstName[i], lstret[i], len(listWord[i]) , listWord[i])
        return strResult

# 命令行处理
def main():
    parser = argparse.ArgumentParser(description='文本字符集分析与过滤工具')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + gblVersion )
    parser.add_argument('-s','--showmap', action='store_true', help='显示字符集清单')
    parser.add_argument('--file', default='', help='待处理数据文件名，必选参数') # required=True,
    parser.add_argument('--report', action='store_false', help='是否进行分析,默认为否')
    parser.add_argument('--detail', action='store_true', help='是否输出明细报告,默认为否')
    parser.add_argument('--filter', action='store_true', help='是否进行过滤处理，默认为否')
    parser.add_argument('--remove', default=[0,3] , nargs='+', type=int, 
        help='指定要过滤的字符集,默认为[0,3];指定过滤字符集时将忽略保留字符集;')
    parser.add_argument('--remain', default=[] , nargs='+', type=int, 
        help='指定要保留的字符集,默认为全部;如果指定过滤字符集时将忽略保留字符集;')
    parser.add_argument('--outfile', default='', help='过滤后的输出文件名，未指定时将自动生成')

    args = parser.parse_args()

    showmap = args.showmap

    filename = args.file
    detail = args.detail
    report = args.report
    isfilter = args.filter
    remove = args.remove
    remain = args.remain
    outfile = args.outfile
    #print (args)
    #print(remain)
    #sys.exit()

    objC = CharsetFilter()
    # 输出字符集分类表
    if showmap:
        print('--%2s:%6s--' %  ('编号', '字符集名称') )
        for i in range(len(objC.lstName)):
            print('  %2d:%6s' %  (i, objC.lstName[i]) )
        return 0

    if not filename:
        print('请使用--file参数指定文件!')
        return 0

    txt = objC.readtxtfile(filename)
    if not txt:
        print('文件未找到!')
        return 0

    if report:
        start = time.time()
        print('正在分析文件,请稍候...')
        fn = os.path.split(filename)[1]
        strRet = objC.charAnalyze (txt, detail)
        if not detail:
            print(('[%s]字符集分析报告' % fn).center(40,'-') ) #+ '\n'
            print(strRet)
        else:
            reportfn = filename[:-4] + '_report.txt' 
            objC.savetofile(strRet, reportfn)
            print('文件分析报告保存为:%s' % reportfn)
        
        end = time.time()
        total_time = getSpanTimes(end-start)
        print('分析用时:%s' % total_time)

    if isfilter:
        start = time.time()
       
        #生成输出文件名
        if not outfile:
            outfile = filename[:-4] + '_out.txt'    

        print('正在过滤字符...')
        rettxt = ''
        rettxt = objC.txtfilter(txt, remove=remove, remain=remain)
        if rettxt:
            objC.savetofile(rettxt,outfile)
            print('文件已过滤，并保存为:%s' % outfile)
    
        end = time.time()
        total_time = getSpanTimes(end-start)
        print('过滤用时:%s' % total_time)

# 测试 
def test ():
    objC = CharsetFilter()
    txt = '中大1三K┫□＼，≯ó㈥l｡ ･ ･ ｡ ﾉ ♡不ε﹣￥▽￣ˊˋ﹉▲āōē﹑'
    #s = '｡ ･ ･ ｡ ﾉ ♡'
    #a = objC.segIndex(0x25b2)
    #a = objC.segIndex(0x2EF4)
    #a = objC.segIndex(0xFFFD)
    #a = objC.segIndex(0x0006)
    #a = objC.segIndex(0xFFFE)
    #a = objC.segIndex(0xFFA1)
    #a = objC.segIndex(0x2453)
    #a = objC.segIndex(0x2580) #0x25BD 0x2580
    #for x in txt:
    #    a = objC.segIndex(ord(x))
    #    print(x,hex(ord(x)),a)
    
    #print('-'*40)
    strRet = objC.charAnalyze (txt, detail=1)
    print('字符集分析报告'.center(40,'-'))
    print(strRet)
    
    remove = []
    remain = [2, 36] # 只保留 中文汉字 和 英文半角
    rettxt = objC.txtfilter(txt, remove=remove, remain=remain)
    print('过滤结果：\n%s' % rettxt)
    print('原始长度:%d, 过滤后长度:%d' % ( len(txt), len(rettxt)))

if __name__ == '__main__':
    pass
    #main()
    test()
