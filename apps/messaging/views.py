from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from apps.marketplace.models import Listing

User = get_user_model()

@login_required
def inbox_view(request):
    conversations = request.user.conversations.prefetch_related(
        'participants', 'messages'
    ).order_by('-updated_at')
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })

@login_required
def conversation_view(request, pk):
    conv = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'messages__sender'),
        pk=pk
    )
    if request.user not in conv.participants.all():
        return redirect('inbox')

    # Mark messages as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(conversation=conv, sender=request.user, body=body)
            conv.save()  # Update updated_at timestamp
        return redirect('conversation', pk=pk)

    other = conv.get_other_participant(request.user)
    return render(request, 'messaging/conversation.html', {
        'conversation': conv,
        'messages': conv.messages.order_by('created_at'),
        'other': other,
    })

@login_required
def start_conversation(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.seller == request.user:
        return redirect('listing-detail', pk=listing_id)

    # Find or create conversation
    existing = Conversation.objects.filter(
        participants=request.user,
        listing=listing
    ).filter(participants=listing.seller).first()

    if existing:
        return redirect('conversation', pk=existing.id)

    conv = Conversation.objects.create(listing=listing)
    conv.participants.add(request.user, listing.seller)
    return redirect('conversation', pk=conv.id)