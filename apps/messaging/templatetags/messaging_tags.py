from django import template

register = template.Library()

@register.filter
def other_participant(conversation, user):
    """Get the other participant in a conversation."""
    return conversation.get_other_participant(user)