from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_page(context, page_number):
    """Current URL's querystring with `page` replaced, for pagination links."""
    request = context["request"]
    params = request.GET.copy()
    params["page"] = page_number
    return f"?{params.urlencode()}"
