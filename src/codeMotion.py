'''
@Time： 2022/1/2  11:46 
@Author: yx
@File: codeMotion.py
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

  def chan(self):
      s = ''
      if self.arrIndex == '-1':
          s += self.var
      else:
          s += self.var
          s += ' [ '
          s += self.arrIndex
          s += ' ]'
      return s

  def print(self):
    if self.var != '':
      print(self.var, end='')
      if self.arrIndex != '-1' :
        print('[' + self.arrIndex + ']', end='', sep = '')

class Expression:

  def __init__(self, result=Item, left=Item, right=Item, op='', bk = '-1'):
    self.result = result
    self.left = left
    self.right = right
    self.op = op
    self.bk = bk

  def init(self, str, bk = '-1'):
        items = str.split()
        if items[len(items) - 2] == '=':  # 等号右边只有一个变量（且不是数组变量）
            var = items[0]
            arrIndex = '-1'
            if items[1] == '[':
                arrIndex = items[2]
            else:
                arrIndex = '-1'
            re = Item(var, arrIndex)
            left = Item(items[len(items) - 1])
            right = Item()
            op = ''
            self.result = re
            self.left = left
            self.right = right
            self.op = op
            self.bk = bk
        else:
            re = Item(items[0])
            op = items[3]
            if op != '[':
                left = Item(items[2])
                right = Item(items[4])
            else:
                left = Item(items[2], items[4])
                right = Item()
            self.result = re
            self.left = left
            self.right = right
            self.op = op
            self.bk = bk

  def getResult(self):
    return self.result

  def getLeft(self):
    return self.left

  def getRight(self):
    return self.right

  def getBk(self):
    return self.bk

  def print(self):
    self.result.print()
    print('=', end='', sep='')
    self.left.print()
    if self.op != '[':
      print(self.op, end='', sep='')
    self.right.print()

    print()

  def change(self):
      s = ''
      s += self.result.chan()
      s += ' = '
      s += self.left.chan()
      if self.op != '[':
          s += ' '
          s += self.op
          s += ' '
          s += self.right.chan()
      return s

info = program

start_block = str(info['summary']['total_blocks'])
start_code = info['blocks'][str(info['summary']['total_blocks'] - 1)]['line_num'][1] + 1

def check1(s):
    for loop in info["loops"]:
        for bk in loop["loop_blks"]:
            for code in info['blocks'][bk]["code"]:
                if code[0] == '?' or code[0] == '!':
                    continue
                exp = Expression()
                exp.init(str=code, bk=bk)
                if exp.getBk() != s.getBk():
                    if (exp.getResult() == s.getResult()):
                        return False
                    if (exp.getResult() == s.getLeft() or exp.getResult() == s.getRight()):
                        if s.getBk() not in info['blocks'][exp.getBk()]['dom']:
                            return False
    return True

def takeoff(codes, loop):
    if(codes.__len__() == 0):
        return
    block = {
            "line_num": [],
            "next": [],
            "code": [],
            "defd": [],
            "used": [],
            "in": [],
            "out": [],
            "pre": [],
            "dom": []
        }
    global start_block
    block['next'].append(loop['loop_blks'][0])
    block['next'].append(None)
    firstblk = loop['loop_blks'][0]
    for i in info['blocks'][firstblk]['pre']:
        if i not in loop['loop_blks']:
            info['blocks'][i]['next'][info['blocks'][i]['next'].index(firstblk)] = start_block
        block['pre'].append(i)

    '''for i in loop['loop_blks']:
        for j in info['blocks'][i]['pre']:
            info['blocks'][j]['next'].remove(i)
            info['blocks'][i]['pre'].remove(j)
            block['pre'].append(j)
            info['blocks'][j]['next'].append(start_block)
        info['blocks'][i]['pre'].append(start_block)'''
    for e in codes:
        block['code'].append(e.change())
        info['blocks'][e.getBk()]['code'].remove(e.change())
    info['blocks'][start_block] = block
    info['summary']['total_blocks'] += 1
    start_block = str(int(start_block) + 1)

for loop in info["loops"]:
    motioncode = list()
    necessarybk = list()
    activevar = set()
    for bk in loop["loop_blks"]:
        for v in info['blocks'][bk]["out"]:
            activevar.add(v)
        tag = True
        for successor in info['blocks'][bk]["next"]:
            if successor not in loop["loop_blks"]:
                tag = False
                break
        if (tag):
            necessarybk.append(bk)
    temcode = list()
    for dic in loop["remainedexp"]:
        for kv in dic.items():
            for nums in kv[1]:
                temcode = info['blocks'][kv[0]]['code'][int(nums)]
                if temcode[0] == '?' or temcode[0] == '!':
                    continue
                code = Expression()
                code.init(str=temcode, bk=kv[0])
                re = code.getResult()
                if nums in necessarybk:
                    if (code not in motioncode and check1(code)):
                        motioncode.append(code)
                else:
                    if (code not in motioncode and check1(code)):
                        strR = ''
                        if re.getArrIndex() != '-1':
                            strR = re.getVar()+'['+re.getArrIndex()+']'
                        else:
                            strR= re.getVar()
                        if strR not in activevar:
                            motioncode.append(code)

    '''for i in motioncode:
        i.print()'''

    staticvar = list()
    for t in info['blocks'][loop['loop_blks'][0]]['in']:
        st = Item(t)
        staticvar.append(st)

    offcode = list()
    while (True):
        tag = True
        for code in motioncode:
            if (((code.getLeft() in staticvar) or (code.getLeft().getVar().isdigit())) and ((code.getRight() in staticvar) or (code.getRight().getVar().isdigit()))):
                motioncode.remove(code)
                offcode.append(code)
                if code.getResult() not in staticvar:
                    staticvar.append(code.getResult())
                tag = False
        if (tag):
            takeoff(offcode, loop)
            break

# %%
new_file = rege.sub('(.*)\\.json$', r'\g<1>_motion.json', args.filename[0])
print("Saving output to:", new_file)
with open(new_file, "w") as fp:
    json.dump(info, fp, indent=2)
