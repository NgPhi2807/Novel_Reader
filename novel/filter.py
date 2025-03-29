from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()

@register.filter
def viet_timesince(value):
    delta = timesince(value, now())
    delta = delta.replace('minutes', 'phút').replace('minute', 'phút')
    delta = delta.replace('hours', 'giờ').replace('hour', 'giờ')
    delta = delta.replace('days', 'ngày').replace('day', 'ngày')
    delta = delta.replace('weeks', 'tuần').replace('week', 'tuần')
    delta = delta.replace('months', 'tháng').replace('month', 'tháng')
    delta = delta.replace('years', 'năm').replace('year', 'năm')
    return f"{delta} trước"
