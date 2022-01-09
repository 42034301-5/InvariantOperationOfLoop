'''
@Time： 2022/1/1  23:27 
@Author: yx
@File: invariantOperationOfLoop.py
'''

import json

import re as rege
import json
import argparse
import copy
import random


# %%
parser = argparse.ArgumentParser(prog='inducelinearvariable', prefix_chars='-', description='induce linear variables',
                                 epilog="before using, check the input file")

parser.add_argument(
    'filename', help='the filename of input json', type=str, nargs=1)

cond_f = {"==": lambda x, y: x == y, "!=": lambda x, y: x != y, ">=": lambda x, y: x >=
          y, "<=": lambda x, y: x <= y, ">": lambda x, y: x > y, "<": lambda x, y: x < y}
arith_f = {"+": lambda x, y: x+y, "-": lambda x, y: x-y, "*": lambda x,
           y: x*y, "/": lambda x, y: x//y, "%": lambda x, y: x % y}
eserved_word = {"HALT", "=", "+", "-", "*", "/", "%", "?",
                ":", "!:", ">", "<", ">=", "<=", "==", "!=", "[", "]"}
reg = rege.compile('^[0-9]+$')


# %%
# 文件读写
program = {}
args = parser.parse_args()
filename = args.filename[0]
with open(filename, "r") as fp:
    program = json.load(fp)


class Item:

  def __init__(self, var='', arrIndex='-1'):
    self.var = var
    self.arrIndex = arrIndex

  def __eq__(self, other):
    if self.var == other.var and self.arrIndex == other.arrIndex:
      return True
    else:
      return False

  def getVar(self):
    return self.var

  def getArrIndex(self):
    return self.arrIndex

  def print(self):
    if var != '':
      print(self.var, end='')
      if self.arrIndex != '-1' :
        print('[' + self.arrIndex + ']', end='', sep = '')

class Expression:

  def __init__(self, result=Item, left=Item, right=Item, op='', order = -1):
    self.result = result
    self.left = left
    self.right = right
    self.op = op
    self.order = order

  def getResult(self):
    return self.result

  def getLeft(self):
    return self.left

  def getRight(self):
    return self.right

  def getOrder(self):
    return self.order

  def print(self):
    self.result.print()
    print('=', end='', sep='')
    self.left.print()
    if self.op != '[':
      print(self.op, end='', sep='')
    self.right.print()

    print()


info = program


'''for loops in info["loops"]:
  print(loops)
  for block in loops["loop_blks"]:
    print(info["blocks"][block]["code"])'''

expressions = list()

blocks = set()
for loops in info["loops"]:
  for bks in loops["loop_blks"]:
    blocks.add(bks)



for block in blocks:
  temExp = list()
  temExp.append(block)
  for i in range(0, len(info["blocks"][block]["code"])):
    codes = info["blocks"][block]["code"][i]
    items = codes.split()
    if items[0] == '?' or items[0] == '!:' or items[0] == 'HALT': # 跳转或停机语句
      continue
    # print(items)
    if items[len(items) - 2] == '=': # 等号右边只有一个变量（且不是数组变量）
      var = items[0]
      arrIndex = '-1'
      if items[1] == '[' :
        arrIndex = items[2]
      else:
        arrIndex = '-1'
      re = Item(var, arrIndex)
      left = Item(items[len(items) - 1])
      right = Item()
      op = ''
      temExp.append(Expression(re, left, right, op, str(i)))
    else:
      re = Item(items[0])
      op = items[3]
      if op != '[':
        left = Item(items[2])
        right = Item(items[4])
      else:
        left = Item(items[2], items[4])
        right = Item()
      temExp.append(Expression(re, left, right, op, str(i)))
  expressions.append(temExp)

'''for i in range(len(expressions)):
  for j in expressions[i]:
    if type(j) == str:
      print(j)
    else:
      j.print()
  print('------------------------------')'''


for loops in info['loops']:
  constItem = list()
  temcode = list()
  tem = dict()
  for bk in loops["loop_blks"]:
    tem[bk] = list()
    for exp in expressions:
      if (exp[0] == bk):
        temcode.extend(exp)

  while (True):
      lenLast = len(tem)
      number = '0'
      nums = 0
      for i in temcode:
        if type(i) == str:
          number = i
          nums = 0
          continue
        nums = nums + 1
        tag = True
        for j in temcode:
          if type(j) == str:
            continue
          if (j not in tem):
                iL = i.getLeft()
                iR = i.getRight()
                tiL = Item(i.getLeft().getArrIndex())
                tiR = Item(i.getRight().getArrIndex())
                tiRe = Item(i.getResult().getArrIndex())

                if (j.getResult() == iL or j.getResult() == iR or j.getResult() == tiL or j.getResult() == tiR or j.getResult() == tiRe):
                  tag = False
                  break
        if (tag):
          if i not in tem:
            tem[number].append(str(nums - 1))
      lenCur = len(tem)
      if (lenLast == lenCur):
            break
  constItem.append(tem)
  loops['remainedexp'] = constItem




'''for keys in constItem.keys():
  print(keys, ':')
  for t in constItem[keys]:
    print(t.order, '  ', end = '')
    t.print()
  print('--------------------------')'''


'''for loops in info["loops"]:
  loopexp = dict()
  for bks in loops["loop_blks"]:
    temexp = []
    for t in constItem[bks]:
      temexp.append(t.order)
    loopexp[bks] = temexp
  loops["remainedexp"] = loopexp'''

# %%
new_file = rege.sub('(.*)\\.json$', r'\g<1>_invariant.json', args.filename[0])
print("Saving output to:", new_file)
with open(new_file, "w") as fp:
    json.dump(info, fp, indent=2)



