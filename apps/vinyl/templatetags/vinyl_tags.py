from django import template

register = template.Library()

@register.inclusion_tag('vinyl/pagination.html')
def render_pagination(page_obj, request):
    """Render pagination with preserved GET parameters"""
    return {
        'page_obj': page_obj,
        'request': request,
    }
