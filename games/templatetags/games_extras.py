from django import template

register = template.Library()

def check_membership(test_string):
    return 'Hello %s' % test_string

register.simple_tag(check_membership)

