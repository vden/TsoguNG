# Template tag
# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django import template
from core.types import Event
from django.db.models import Q

register = template.Library()

#from datetime import date, timedelta
def get_last_day_of_month(year, month, autoescape=False):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)

@register.inclusion_tag('month_cal.html')
def month_cal(year=date.today().year, month=date.today().month):
    now = date.today()
    
    event_list = Event.objects.filter(date_end__gte = now)\
        .filter(state__name = u"опубликованный")\
        .order_by("date_start")

    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday())
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []
    today = date.today()

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['today'] = False
        cal_day['event'] = False
        if day == today:
            cal_day['today'] = True
        for event in event_list:
            if day >= event.date_start.date() and day <= event.date_end.date():
                cal_day['event'] = True
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False  
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)

    import  math

    now = date.today()
    now_year = now.year - 1*int(now.month<9)
    
    sep = date(now_year, 9, 1)

    lw = int ( math.ceil ( ( now - sep ).days / 7. ) )
    start_week = 0
    if False: #learn_of_week=='нечетная':
        week=['нечетная','четная']
    else:
        week=['четная','нечетная']
    wn=int(now.strftime('%W'))
            
    ss = week[(wn-int(start_week))%2]+' неделя (%s/%s)'%(lw,wn)
    w =  '''<span title="%s неделя от 1 сентября %s года, %s неделя от начала года">%s</span>'''%(lw,now_year,  wn, ss)


    return {'calendar': month_cal, 'headers': week_headers, 'cweek': w, 'events': event_list}
