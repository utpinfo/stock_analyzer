from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring(get_params, **kwargs):
    """
    返回修改指定 querystring 參數後的字串
    """
    params = get_params.copy()
    for k, v in kwargs.items():
        params[k] = v
    return urlencode(params)
