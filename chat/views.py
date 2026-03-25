from chat.forms import MessageForm
from user.models import CustomUser
from chat.models import Message
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Max

@login_required
def inbox(request, user_id):
    owner = get_object_or_404(CustomUser, id=user_id)
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=owner) |
        Q(sender=owner, receiver=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = owner
            message.is_read = False  
            message.save()
            return redirect('inbox', user_id=owner.id)
    else:
        form = MessageForm()

    return render(request, 'inbox.html', {
        'Owner': owner,
        'messages': messages,
        'form': form
    })
    
@login_required
def chat_list(request):
    user = request.user

    chat_users = CustomUser.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).annotate(
        last_message_time=Max('sent_messages__timestamp')  
    ).distinct().order_by('-last_message_time')  

    chat_partners = []
    for chat_user in chat_users:
        if chat_user != user:
            chat_partners.append({
                "user": chat_user,
                "last_message_time": Message.objects.filter(
                    Q(sender=user, receiver=chat_user) | Q(sender=chat_user, receiver=user)
                ).order_by('-timestamp').first().timestamp
            })

    chat_partners = sorted(chat_partners, key=lambda x: x['last_message_time'], reverse=True)

    return render(request, 'chat_list.html', {'chat_partners': chat_partners})

