# -*- coding: utf-8 -*-
import mimetools

import urllib2_file
import urllib2

def __serialized(obj):
    
    return obj

def __transform_field(obj_a, t):
    k, v_dict = t
    
    d =  v_dict.internal_transform
    stub = {}

    sobj = __serialized(obj_a)
    for (k,v) in d.items():
        if v[0] == '"':
            stub[k] = v[1:-1]
        else:
            stub[v] = sobj[k]
    return stub

def __correct_text(txt):
    """ т.к. мы изменили все слаги на корректные --
    нужно изменить и ссылки в тексте """
    import re
    rx = re.compile(r'\.(\d{4}-\d{2}-\d{2})\.(\d+)')
    
    return rx.sub(r'-\1-\2', txt)

def __create_new_object(t, stub, parent):
    stub['parent'] = parent
    stub['slug'] = stub['slug'].replace('.','-')

    state_hack = {'visible': '1', 'published': '2', 'hidden': '4', 'main_published': '3', 'private': '4'}
    stub['state'] = state_hack[stub['state']]

    category_hack = {'Новость Университета': '1',
                     'Новость ИнТра':'2',
                     'Новость ИГиГа':'3',
                     'Новость ИНиГа':'4',
                     'Новость Гуманитарного института':'5',
                     'Новость ТИ':'6',
                     'Новость ИМиБ':'7',
                     'Новость кафедры геоинформатики':'8',
                     'Новость кафедры физвоспитания':'9',
                     'Новость лицея':'10'}
    if stub.has_key('category'):
        stub['category'] = stub['category'].decode('koi8-r').encode('utf-8')
        stub['category'] = category_hack.get(stub['category'], "1")

    files = []

    import tempfile, os
    for k in stub.keys():
        try:
            stub[k] = str(stub[k])
            if stub[k] == 'None': stub[k] = ''

            if stub[k][:4] == 'http' and t != 'Dissertation':
                # данные, сохраняем
                try:
                    suffix = stub['slug'].split('-')[-1:][0].lower()
                except:
                    suffix = "jpg"
                if len(suffix)>3: suffix = "jpg"
                f = tempfile.NamedTemporaryFile(suffix=".%s"%suffix)
                f.write(urllib2.urlopen(stub[k]).read())
                f.flush()
                stub[k] = open(f.name, 'rb')
                files.append(f)
            else:
                try:
                    f = stub[k].decode('utf-8')
                except:
                    stub[k] = stub[k].decode('koi8-r').encode('utf-8')
        except Exception, E:
            print "EXC", stub[k], "EXC:", str(E)

    import base64, urllib, simplejson
    
    if stub.has_key('text'):
        stub['text'] = __correct_text(stub['text'])
    
    try:
        htmlFile = urllib2.urlopen('http://www.tsogu.ru/xml/%s/'%t.lower(), stub)
    except urllib2.HTTPError, E:
        if E.code == 201:
            pk = simplejson.loads(E.read())[0]['pk']
            print "CREATING %s in %s"%(t, parent), stub['title'], "RESULT:", pk
            return pk
        else:
            print "===URL EXC:", simplejson.loads(E.read())['model-errors'] #, dir(E)
            print stub
            raise


def __get_zodb_list(trf_table, r, verbose=True, parent=None):    
    types = eval(urllib2.urlopen(r+"get_types").read())

    for t in types:
        t_real = t.replace(" ", "%20")
        t = t.replace(" ", "")

        if not trf_table.debug().has_key(t):
            print "!!!!! TYPE IS NOT DEFINED !!!!!", t
            continue
        trf = trf_table.debug()[t]
        fields = urllib2.quote(",".join(trf[1].internal_transform.keys()))
        print "TRANSFERRING", r, t
        objs = eval( urllib2.urlopen(r+"export/?type=%s&fields=%s"%(t_real,fields)).read() )

        for obj in objs:
            new_stub = __transform_field(obj, trf)   
            try:
                new_parent = __create_new_object(trf[0], new_stub, parent)
            except:
                continue

            if t in ('Folder', 'PloneArticle', 'Headline', 'ATFolder'):
                print "----RECURSION", r+obj['id']
                __get_zodb_list(trf_table, r+obj['id']+'/', verbose, new_parent)
    return

def run(trf_table, args):
    print "Imma RUN function"
    (a,b,c,d) = args
    print "i will transfer from %s to %s (creds %s)"%(a,c,b)
    root_name = a
    creds = b
    
    if d == 'verbose': v = True
    
    root = a
    r = __get_zodb_list(trf_table, root, v, c)
        

def run1(a,b):
    print "Imma RUN1 function"
    
