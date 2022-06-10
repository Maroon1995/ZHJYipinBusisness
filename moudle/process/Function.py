
import re
from typing import List

class HandleItem(object):

    def __init__(self, strx: str):
        """
        :param strx: 被处理的字符串
        """
        self.strx = strx

    def FirstCharZeros(self):
        """
        数值字符串第一个元素为0
        :return:
        """
        ItemStrs: str
        if self.strx.isdigit():  # 如果字符串中所有字符都是数值，则返回True

            Zero = re.findall(re.compile(r'^0\d+'), self.strx)
            if Zero:
                ItemStrs = self.strx[1:]
            else:
                ItemStrs = self.strx
        else:
            ItemStrs = self.strx

        return ItemStrs

    def romanNumberTransform(self):
        '''
        将罗马数值转换为阿拉伯数值
        :return:
        '''
        ItemStrs: str = self.strx.replace('XV', '15').replace('XIV', '14').replace('XIII', '13') \
            .replace('XII', '12').replace('XI', '11').replace('IX', '9').replace('VIII', '8') \
            .replace('VII', '7').replace('VI', '6').replace('IV', '4').replace('III', '3') \
            .replace('II', '2').replace('-V', '-5').replace('-I', '-1').replace('-X', '10')
        return ItemStrs

    def multizero(self):
        """
        '8.000N'和'8.0000N'造成的编码不统一
        :return:
        """
        reslist: List[str] = re.findall(re.compile(r'\.0+[A-Za-z]'), self.strx)
        if reslist:
            for el in reslist:
                # self.strx = re.sub(el,el[-1],self.strx)
                self.strx = self.strx.replace(el, el[-1])
        return self.strx

    def floattransform(self):
        """
        将字符串中包含小数的数值转换：2.023->2DIAN023
        :return:
        """
        floatlist: List[str] = re.findall(re.compile(r'\d+\.\d+'), self.strx)
        if floatlist:
            for el in floatlist:
                elem = el.replace('.', 'DIAN')
                self.strx = self.strx.replace(el, elem)
        return self.strx

    def deletesymbol(self):
        """
        去除字符串中的符号
        :return:
        """
        ItemStrs: str
        rcp = re.compile(r'\W+')
        symbols = re.findall(rcp, self.strx)
        if symbols:
            ItemStrs = re.sub(rcp, "", self.strx)  # 去除符号
        else:
            ItemStrs = self.strx

        return ItemStrs


