from django import template
from django.utils.safestring import mark_safe
import markdown2

register = template.Library()

# Create a markdown processor with comprehensive extras configuration
# This matches the configuration used in the preview function
markdowner = markdown2.Markdown(extras=[
    'fenced-code-blocks',
    'tables',
    'break-on-newline',
    'header-ids',
    'strike',
    'footnotes'
])

@register.filter
def markdownify(text):
    """Convert markdown to HTML"""
    if not text:
        return ''
    return mark_safe(markdowner.convert(text))

@register.filter
def get(dictionary, key):
    """Get a value from a dictionary by key"""
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter
def replace(value, arg):
    """Replace all occurrences of the first argument with the second."""
    if not value or not arg:
        return value
    
    args = arg.split(',')
    if len(args) != 2:
        return value
    
    return value.replace(args[0], args[1]) 