# -*- coding: utf-8 -*-

class EStateTransformException(Exception):
    pass

def send_email(mail):
    """ это такой декоратор, который отправит текст, что вернул метод, письмом на указанный адрес.
        ну, вроде как оповещение. """
    def true_decorator(fn):
        def new(*arg):
            text = fn(*arg)
            # тут уходит письмо на mail
            return text
        return new
    return true_decorator

def simple_transform(request, obj, transform):
    """ самый ординарный метод трансформации состояния. ничего не делает, просто существует """
    print "transform ", transform," on ", obj
    return ''

def publish_transform(request, obj, transform):
    from datetime import datetime

    obj.date_published = datetime.now()
    print "PUBLISH: %s"%datetime.now()

    return ''
