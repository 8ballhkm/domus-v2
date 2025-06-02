from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from django.db.models import Q, Max
from .models import Message
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import JsonResponse


def current_user_id(request):
    return {
        'current_user_id': request.user.id if request.user.is_authenticated else None
    }

def get_room_name(user1, user2):
    return f"{min(user1.id, user2.id)}_{max(user1.id, user2.id)}"


def chat_room(request, room_name):
    return render(request, 'chat_room.html', {
        'room_name': room_name
    })

@login_required
def chat_with_user(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    room_name = get_room_name(request.user, other_user)
    return render(request, 'chat_room.html', {
        'room_name': room_name,
        'other_user': other_user,
    })


@login_required
def chat_rooms_api(request):
    user = request.user

    # Get all distinct partner IDs from messages sent or received
    sent = Message.objects.filter(sender=user).values_list('receiver', flat=True)
    received = Message.objects.filter(receiver=user).values_list('sender', flat=True)
    partner_ids = set(sent).union(set(received))

    # For each partner, get latest message timestamp and content
    partners = []
    for pid in partner_ids:
        partner = CustomUser.objects.get(id=pid)
        last_message = Message.objects.filter(
            (Q(sender=user) & Q(receiver=partner)) | (Q(sender=partner) & Q(receiver=user))
        ).order_by('-timestamp').first()

        partners.append({
            'id': partner.id,
            'username': partner.username,
            'last_message': last_message.content if last_message else '',
            'last_timestamp': last_message.timestamp.isoformat() if last_message else '',
        })

    # Sort partners by latest message timestamp descending
    partners.sort(key=lambda x: x['last_timestamp'], reverse=True)

    return JsonResponse({'partners': partners})

@login_required
def chat_history_api(request, partner_id):
    user = request.user
    try:
        partner = CustomUser.objects.get(id=partner_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Partner not found'}, status=404)

    messages = Message.objects.filter(
        (Q(sender=user) & Q(receiver=partner)) | (Q(sender=partner) & Q(receiver=user))
    ).order_by('timestamp')

    data = [{
        'sender_id': msg.sender.id,
        'sender_username': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat(),
    } for msg in messages]

    return JsonResponse({'messages': data})
