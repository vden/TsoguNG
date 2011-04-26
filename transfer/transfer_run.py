#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys, re

class LFunction(object):
    def __init__(self, method, name):
        self.method = method
        self.name = name

    def __str__(self):
        return self.name

    def set_args(self, trf, args):
        self.args = []
        self.trf = trf
        for arg in args:
            if arg[0] == '"' and arg[-1:] == '"': arg = arg[1:-1]
            self.args.append(arg)

    def start(self):
        return self.method(self.trf, self.args)

class LFunctionList(object):
    def __init__(self):
        self.funlist = {}

    def add(self, fn):
        self.funlist[str(fn)] = fn

    def get(self, fn_name):
        try:
            return self.funlist[fn_name]
        except:
            raise Exception("E: Function %s is not defined!"%fn_name)

class Token(object):
    token = ''
    token_type = -1

    def __init__(self, str_token):
        self.token = str_token
        self.val = None

    def check_valid_rvalue(self, rval):
        import re
        rx = re.compile(r'^[a-zA-Z0-9]*$')
        if rx.match(rval) or ( (rval[0] == rval[-1:]) and (rval[0] == '"') ):
            return True
        else:
            return False

    def check_valid_lvalue(self, rval):
        import re
        rx = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*$')
        if rx.match(rval):
            return True
        else:
            return False
        
    def __internal_parse_transform(self, s):
        s = s.strip()
        if s[0] != '{' or s[-1:] != '}':
            raise Exception("E: Incorrect transform dictionary!")

        res = {}
        s = s.strip('{}')
        for pair in s.split(","):
            try:            
                (k, v) = pair.split('=')
            except:
                raise Exception("E: Incorrect transform line!")
            k = k.strip()
            v = v.strip()
            res[k] = v

        return res
        
    def __parse(self, s, t):
        s = [x.strip() for x in s]
        self.token_type = t
        if t == 0:
            # found transform
            (fr,to) = [x.strip() for x in s[0].split('->')]
            if not self.check_valid_lvalue(fr) or not self.check_valid_lvalue(to):
                raise Exception("Invalid lvalue in transform")
            else:
                self.val = (fr, to, s[1])
                
                # видимо, у меня в роду были индусы...
                self.internal_transform =  self.__internal_parse_transform(s[1])
        elif t == 1:
            # found assignment
            if not self.check_valid_rvalue(s[1]):
                raise Exception("Invalid rvalue in assignment")
            else:
                self.val = s
        else:
            # found statement
            if not self.check_valid_lvalue(s[0]):
                raise Exception("Invalid lvalue in transform")
            for i in s[1].split():
                if not self.check_valid_rvalue(i):
                    raise Exception("Invalid rvalue in assignment")
            self.val = s

    __parse_transform = lambda self, s: self.__parse(s, t=0)
    __parse_assign = lambda self, s: self.__parse(s, t=1)
    __parse_statement = lambda self, s: self.__parse(s, t=2)

    def compute(self):
        lvalue = self.token.split('=', 1)
        if isinstance(lvalue, list) and (len(lvalue)>1):
            rvalue = lvalue[1].strip()
            lvalue = lvalue[0].strip()
            
            if (lvalue.find('->')>0):
                self.__parse_transform((lvalue,rvalue))
            else:
                self.__parse_assign((lvalue,rvalue))
        else:
            self.__parse_statement((lvalue[0].split(' ',1)))
        return self

    @classmethod
    def is_transform(cls, token):
        return token.token_type == 0
    @classmethod        
    def is_assign(cls, token):
        return token.token_type == 1
    @classmethod
    def is_statement(cls, token):
        return token.token_type == 2
    
    @classmethod
    def process_transform(cls, token):
        pass

class AssignTable(object):
    def __init__(self, token_list):
        self.assign = {}
        for t in token_list:
            if Token.is_assign(t):
                self.assign[t.val[0]] = t.val[1]

    def debug(self):
        return self.assign

    def find_var(self, var):
        try:
            return self.assign[var]
        except:
            raise Exception("Variable %s not found!"%var)
            

class TransformTable(object):
    def __init__(self, token_list):
        self.trf = {}
        for t in token_list:
            if Token.is_transform(t):
                self.trf[t.val[0]] = (t.val[1], t)
                
    def debug(self):
        return self.trf
                
class ProgramFlow(object):
    def __init__(self, token_list, st_tbl):
        self.st_tbl = st_tbl
        self.stmt = []
        for t in token_list:
            if Token.is_statement(t):
                # проверить каждый аргумент: строка/переменная/эксепшн
                args = t.val[1].split()
                args_res = []
                for i in args:
                    if i[0]=='"' and i[-1:] == '"' and i[0] == i[-1:]:
                        args_res.append(i)
                    else:
                        args_res.append(self.st_tbl.find_var(i))
                self.stmt.append((t.val[0], args_res))
    def debug(self):
        return self.stmt
        
    def flow_iter(self):
        return self.stmt

class Program(object):
    text = ''
    pointer = 0
    tokens = []

    def __init__(self, f):
        self.text = f.read().strip()
        f.close()
        self.parsed = False
        self.flist = LFunctionList()

        import transfer_lib as tlib
        self.flist.add(LFunction(tlib.run, "run"))
        self.flist.add(LFunction(tlib.run1, "run1"))

    def debug(self):
        return (len(self.text),)

    def __next_token(self):
        esc = False
        sym = u"0x00"
        str_token = u''
        while (sym != u';') or ((sym==u';') and (esc == True)):
            sym = self.text[self.pointer]
            self.pointer += 1
            str_token += sym
            if sym == u'"' and esc == True: esc=False
            elif sym == u'"': esc = True

        self.tokens.append(Token(str_token[:-1].strip()).compute())
        return (self.pointer >= len(self.text)) and -1 or self.pointer

    def parse(self):
        res = 1
        while res>0:
            res = self.__next_token()

        print "Text parsed"

        self.assign_table = AssignTable( self.tokens)
        print "ASSIGN TABLE", self.assign_table.debug()

        self.transform_table = TransformTable( self.tokens)
        print "TRANSFORM TABLE", self.transform_table.debug()

        self.pflow = ProgramFlow(self.tokens, self.assign_table)
        print "PROGRAM FLOW", self.pflow.debug()

        self.parsed = True

    def resolve(self, fname, fargs):
        # найти библиотечную функцию и выполнить ее с 
        # указанными параметрами
        fn = self.flist.get(fname)
        fn.set_args(self.transform_table, fargs)
        
        return fn

    def run(self, argv):
        for f in self.pflow.flow_iter():
#            print "executing %s with args %s"%(f[0], f[1]) 
            self.resolve(f[0], f[1]).start()

if __name__ == '__main__':
    prg = Program(open(sys.argv[1]))
    print prg.debug()
    prg.parse()
    prg.run(None)
    
