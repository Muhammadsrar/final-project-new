from book.forms import BookForm, ReviewForm, WishlistForm
from user.forms import CustomUserForm
from chat.forms import MessageForm
from book.models import Book, ExchangeRequest, Notification, Review, Wishlist
from user.models import CustomUser
from chat.models import Message
from django.db.models import Q, Max
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if notification.user == request.user:
        notification.is_read = True
        notification.save()
    return redirect('dashboard')


@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user.user_type not in ['Owner', 'Seeker']:
                messages.error(request, 'Only Owners and Seekers can list books!')
                return redirect('add_book')
            
            book = form.save(commit=False)
            book.owner = request.user 
            book.save()
            messages.success(request, 'Book added successfully!')

            matching_wishlist = Wishlist.objects.filter(book_title__iexact=book.title)
            for wishlist_item in matching_wishlist:
                user = wishlist_item.user  
                
                Notification.objects.create(
                    user=user,
                    message=f'The book "{book.title}" you wanted is now available!',
                    is_read=False
                )

                # messages.info(request, f'Notification sent to {user.username} about {book.title}.')

            return redirect('add_book')

    else:
        form = BookForm()
    
    return render(request, 'add_book.html', {'form': form})



@login_required
def my_books(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    
    books = Book.objects.filter(owner=request.user)

    return render(request, 'my_books.html', {'books': books})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
        messages.success(request, 'Book updated successfully!')            
        return redirect('edit_book',  book_id=book.id)  
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete() 
    messages.success(request, 'Book deleted successfully!')
    return redirect('my_books')


@login_required
def book_list(request):
    books = Book.objects.filter(owner__user_type='Owner').order_by('-created_at')
    return render(request, 'book_list.html', {'books': books})

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist_item = form.save(commit=False)
            wishlist_item.user = request.user
            wishlist_item.save()
            messages.success(request, "Book added to your wishlist!")
            return redirect('wishlist')
    else:
        form = WishlistForm()
    
    return render(request, 'add_wishlist.html', {'form': form})

@login_required
def wishlist(request):
    user_wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': user_wishlist})

@login_required
def delete_from_wishlist(request, wishlist_id):
    wishlist_item = Wishlist.objects.get(id=wishlist_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, "Book removed from your wishlist.")
    return redirect('wishlist')


def seeker_books(request):
    if request.user.is_authenticated and request.user.user_type == 'Seeker':
        books = Book.objects.filter(owner=request.user).values("id", "title", "status")
        return JsonResponse({"books": list(books)})
    return JsonResponse({"books": []})

# def exchange(request, book_id):
#     # Book the user clicked to exchange
#     book = get_object_or_404(Book, id=book_id)

#     # Optional: Get user's own books to choose from to exchange
#     user_books = Book.objects.filter(owner=request.user, status="Available")

#     return render(request, 'exchange.html', {
#         'target_book': book,       # Book they want
#         'user_books': user_books   # Books they can offer in exchange
#     })

# @login_required
# def exchange_request(request):
#     if request.method == "POST":
#         book_id = request.POST.get("book_id")
#         seeker_book_id = request.POST.get("seeker_book_id")

#         if not book_id or not seeker_book_id:
#             messages.error(request, "Please select a book to exchange.")
#             return redirect('exchange_status')

#         try:
#             book = Book.objects.get(id=book_id)  
#             seeker_book = Book.objects.get(id=seeker_book_id)  
            
#             existing_request = ExchangeRequest.objects.filter(
#                 requested_book=book,
#                 offered_book=seeker_book,
#                 sender=request.user,
#                 receiver=book.owner,
#                 status="Pending"
#             ).exists()

#             if existing_request:
#                 messages.warning(request, "Exchange request already exists.")
#             else:

#                 exchange = ExchangeRequest.objects.create(
#                     requested_book=book,
#                     offered_book=seeker_book,
#                     sender=request.user,
#                     receiver=book.owner,
#                     status="Pending"
#                 )


#                 Notification.objects.create(
#                     user=book.owner,
#                     message=f"You have a new exchange request for '{book.title}' from {request.user.username}.",
#                     is_read=False,
#                     exchange_request=exchange
#                 )


#                 messages.success(request, "Exchange request sent successfully.")

#         except Book.DoesNotExist:
#             messages.error(request, "Invalid book selection.")
        
#         return redirect('exchange_status')

#     return redirect('exchange_status')

@login_required
def exchange_request(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        seeker_book_id = request.POST.get("seeker_book_id")

        if not book_id or not seeker_book_id:
            messages.error(request, "Please select a book to exchange.")
            return redirect('exchange_status')

        try:
            book = Book.objects.get(id=book_id)  
            seeker_book = Book.objects.get(id=seeker_book_id)

            # Prevent the owner from requesting exchange on their own book
            if book.owner == request.user:
                messages.error(request, "You cannot request an exchange for your own book.")
                return redirect('exchange_status')

            existing_request = ExchangeRequest.objects.filter(
                requested_book=book,
                offered_book=seeker_book,
                sender=request.user,
                receiver=book.owner,
                status="Pending"
            ).exists()

            if existing_request:
                messages.warning(request, "Exchange request already exists.")
            else:
                exchange = ExchangeRequest.objects.create(
                    requested_book=book,
                    offered_book=seeker_book,
                    sender=request.user,
                    receiver=book.owner,
                    status="Pending"
                )

                Notification.objects.create(
                    user=book.owner,
                    message=f"You have a new exchange request for '{book.title}' from {request.user.username}.",
                    is_read=False,
                    exchange_request=exchange
                )

                messages.success(request, "Exchange request sent successfully.")

        except Book.DoesNotExist:
            messages.error(request, "Invalid book selection.")
        
        return redirect('exchange_status')

    return redirect('exchange_status')


@login_required

def exchanged_books(request):
    if request.user.user_type == 'Seeker':

        exchanged_books = ExchangeRequest.objects.filter(sender=request.user) | ExchangeRequest.objects.filter(receiver=request.user)
    elif request.user.user_type == 'Owner':

        exchanged_books = ExchangeRequest.objects.filter(sender=request.user) | ExchangeRequest.objects.filter(receiver=request.user)
    else:
        exchanged_books = ExchangeRequest.objects.none() 


    return render(request, 'exchanged_books.html', {'exchanged_books': exchanged_books})


@login_required

def add_reviews(request):
    if request.user.user_type == 'Seeker':

        exchanged_books = ExchangeRequest.objects.filter(sender=request.user) | ExchangeRequest.objects.filter(receiver=request.user)
    elif request.user.user_type == 'Owner':

        exchanged_books = ExchangeRequest.objects.filter(sender=request.user) | ExchangeRequest.objects.filter(receiver=request.user)
    else:
        exchanged_books = ExchangeRequest.objects.none() 
        

    print(f"Exchanged Books Found: {exchanged_books.count()}")

    return render(request, 'add_reviews.html', {'exchanged_books': exchanged_books})


def book_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book_reviews = Review.objects.filter(book=book)
    if request.method == 'POST':
        Review.objects.create(
            book=book,
            reviewer=request.user,
            rating=request.POST.get('rating'),
            review_text=request.POST.get('comment'),            
            review_type='book'
        )
        return render(request, 'book_review.html', {'book': book, 'reviews': book_reviews})

    return render(request, 'book_review.html', {'book': book, 'reviews': book_reviews})

def user_review(request, user_id):
    reviewed_user = get_object_or_404(CustomUser, id=user_id)
    
    user_reviews = Review.objects.filter(reviewed_user=reviewed_user)

    if request.method == 'POST':
        Review.objects.create(
            reviewed_user=reviewed_user,
            reviewer=request.user,
            rating=request.POST.get('rating'),
            review_text=request.POST.get('comment'), 
            review_type='user'
        )

        user_reviews = Review.objects.filter(reviewed_user=reviewed_user)

        return render(request, 'user_review.html', {'reviewed_user': reviewed_user, 'reviews': user_reviews})

    return render(request, 'user_review.html', {'reviewed_user': reviewed_user, 'reviews': user_reviews})


def view_reviews(request):
    if not request.user.is_authenticated:
        return redirect('login')

    submitted_reviews = Review.objects.filter(
        reviewer=request.user
    )

    user_reviews = Review.objects.filter(
        reviewed_user=request.user, 
        review_type='user'
    )
    
    book_reviews = Review.objects.filter(
        book__owner=request.user, 
        review_type='book'
    )

    context = {
        'submitted_reviews': submitted_reviews, 
        'user_reviews': user_reviews,
        'book_reviews': book_reviews,
    }
    return render(request, 'reviews.html', context)



@login_required
def exchange_status(request):
    sent_requests = ExchangeRequest.objects.filter(sender=request.user)

    received_requests = ExchangeRequest.objects.filter(receiver=request.user)

    return render(request, 'exchange_status.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

@login_required
def accept_exchange_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)
    
    if exchange_request.receiver != request.user:
        return redirect('exchange_status')
    
    exchange_request.requested_book.status = "Exchanged"
    exchange_request.offered_book.status = "Exchanged"
    exchange_request.requested_book.save()
    exchange_request.offered_book.save()
    
    exchange_request.status = "Accepted" 
    exchange_request.save()
    
    Notification.objects.create(
        user=exchange_request.sender,
        message=f"Your request for {exchange_request.requested_book.title} was accepted!",
        exchange_request=exchange_request
    )
    
    messages.success(request, "Exchange accepted successfully")
    return redirect('exchange_status')

@login_required
def reject_exchange_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)
    
    if exchange_request.receiver == request.user and exchange_request.status == "Pending":
        exchange_request.status = "Rejected"
        exchange_request.save()
        
        Notification.objects.create(
            user=exchange_request.sender,
            message=f"Your request for {exchange_request.requested_book.title} was rejected",
            exchange_request=exchange_request
        )
        messages.error(request, "Exchange request rejected")
    
    return redirect('exchange_status')

@login_required
def cancel_exchange_request(request, request_id):
    try:
        exchange_request = ExchangeRequest.objects.get(id=request_id)

        if exchange_request.sender != request.user:
            messages.error(request, "You can only cancel your own requests.")
            return redirect('exchange_status')

        exchange_request.requested_book.status = "Available"
        exchange_request.offered_book.status = "Rejected"
        exchange_request.requested_book.save()
        exchange_request.offered_book.save()

        exchange_request.status = "Canceled"
        exchange_request.save()

        exchange_request.delete()

        messages.success(request, "Exchange request canceled successfully.")
        return redirect('exchange_status')

    except ExchangeRequest.DoesNotExist:
        messages.error(request, "Invalid request.")
        return redirect('exchange_status')