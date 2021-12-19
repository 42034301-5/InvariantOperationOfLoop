'''
@Time： 2021/12/19  16:18 
@Author: yx
@File: try01.py
'''
class Expression:

    def __init__(self, result = '', left= '', right= '', op= ''):
        self.result = result
        self.left = left
        self.right = right
        self.op = op

    def __deepcopy__(self):
        tem = Expression(self.result, self.left, self.right, self.op)
        return tem

    def getResult(self):
        return self.result

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def print(self):
        print(self.result + ' = ' + self.left + self.op + self.right, end = '', sep = '')
        if (self.op == '['):
            print(']', end = '')
        print()

fp = open("in.txt", "r")
options = ['+', '-', '*', '/', '%', '[']
exp = list()

while True:
    str = fp.readline()
    if not str:
        break
    else:
        result = ''
        left = ''
        right = ''
        op = ''
        lstart = 0
        rstart = 0
        for i in range(0, str.__len__()):
            if (result == ''): # 取等号坐边的数字
                if (str[i] == '='):
                    result = str[0 : i].strip()
                    lstart = i + 1
            elif (left == ''): # 取左操作数，符号和右操作数
                if (str[i] in options):
                    left = str[lstart : i].strip()
                    op = str[i] # 对操作符赋值
                    right = str[(i + 1) : ].strip()
                    if (right[right.__len__() - 1] == ']'):
                        right = right[ : right.__len__() - 1]
            i += 1
        exp.append(Expression(result, left, right, op))


'''for i in range(len(exp)):
    exp[i].print()'''

varSet = set()
constItem = set()
for i in range(len(exp)):
    varSet.add(exp[i].getResult())
    varSet.add(exp[i].getLeft())
    varSet.add(exp[i].getRight())

while (True):
    lenLast = len(constItem)
    for i in range(len(exp)):
        tag = True
        for j in range(len(exp)):
            if ((j not in constItem) and (exp[i].left == exp[j].result or exp[i].right == exp[j].result)):
                tag = False
                break
        if (tag):
            constItem.add(i)
    lenCur = len(constItem)
    if (lenLast == lenCur):
        break


for item in constItem:
    exp[item].print()



