from book.forms import BookForm, ReviewForm, WishlistForm
from user.forms import CustomUserForm
from chat.forms import MessageForm
from book.models import Book, ExchangeRequest, Notification, Review, Wishlist
from user.models import CustomUser
from chat.models import Message
from django.db.models import Q, Max, Prefetch
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




def book_list(request):
    if request.user.user_type == 'Owner':
        # Show seeker books to the owner
        books = Book.objects.filter(owner__user_type='Seeker').order_by('-created_at')
    else:
        # Show owner books to the seeker
        books = Book.objects.filter(owner__user_type='Owner').order_by('-created_at')

    # Prefetch reviews for all the books
    books = books.prefetch_related(
        Prefetch('review_set', queryset=Review.objects.select_related('reviewer').order_by('-created_at'))
    )

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
@login_required
def get_user_books(request):
    exclude_id = request.GET.get('exclude')
    books = Book.objects.filter(
        owner=request.user
    ).exclude(
        id=exclude_id
    ).exclude(
        status='Exchanged'
    )
    books_data = [{
        "id": book.id,
        "title": book.title,
        "author": book.author
    } for book in books]
    return JsonResponse({'books': books_data})

@login_required
def get_owner_books(request):
    book_id = request.GET.get('book_id')
    try:
        selected_book = Book.objects.get(id=book_id)
        owner_books = Book.objects.filter(
            owner=selected_book.owner
        ).exclude(
            id=book_id
        ).exclude(
            status='Exchanged'
        )
        book_list = [{
            'id': book.id,
            'title': book.title,
            'author': book.author
        } for book in owner_books]
        return JsonResponse({'books': book_list})
    except Book.DoesNotExist:
        return JsonResponse({'books': []})
# def get_user_books(request):
#     seeker = request.user
#     book_id = request.GET.get('book_id')

#     try:
#         target_book = Book.objects.get(pk=book_id)
#         owner = target_book.owner

#         seeker_books = Book.objects.filter(owner=seeker)
#         owner_books = Book.objects.filter(owner=owner)

#         data = {
#             'seeker_books': list(seeker_books.values('id', 'title', 'status')),
#             'owner_books': list(owner_books.values('id', 'title', 'status')),
#         }

#         return JsonResponse(data)

#     except Book.DoesNotExist:
#         return JsonResponse({'error': 'Book not found'}, status=404)
# def exchange(request, book_id):
#     # Book the user clicked to exchange
#     book = get_object_or_404(Book, id=book_id)

#     # Optional: Get user's own books to choose from to exchange
#     user_books = Book.objects.filter(owner=request.user, status="Available")

#     return render(request, 'exchange.html', {
#         'target_book': book,       # Book they want
#         'user_books': user_books   # Books they can offer in exchange
#     })

@login_required
def exchange_request(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.owner == request.user:
        messages.error(request, "You can't request an exchange for your own book.")
        return redirect('book_list')

    if ExchangeRequest.objects.filter(requested_book=book, sender=request.user).exists():
        messages.info(request, "You have already requested an exchange for this book.")
        return redirect('exchange_status')

    if request.method == 'POST':
        print("POST request received")
        offered_book_id = request.POST.get('offered_book_id')

        if not offered_book_id:
            messages.error(request, "Please select a book to offer in exchange.")
            return redirect('book_list')

        try:
            offered_book = Book.objects.get(id=offered_book_id, owner=request.user)
        except Book.DoesNotExist:
            messages.error(request, "Invalid book selection.")
            return redirect('book_list')

        # Create the exchange request
        ExchangeRequest.objects.create(
            requested_book=book,
            offered_book=offered_book,
            sender=request.user,
            receiver=book.owner
        )

        # Update book status to 'Requested'
        book.status = 'Exchanged'
        book.save()

        # Notify the owner
        Notification.objects.create(
            user=book.owner,
            message=f"{request.user.username} has requested to exchange the book '{book.title}'."
        )

        messages.success(request, "Exchange request sent.")
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
    exchanged_books = get_exchanged_books_for_user(request.user)

    if request.method == 'POST':
        book_id = request.POST['book_id']
        rating = request.POST['rating']
        comment = request.POST['comment']

        book = get_object_or_404(Book, id=book_id)

        Review.objects.create(
            user=request.user,
            book=book,
            rating=rating,
            comment=comment
        )

        messages.success(request, 'Review submitted successfully.')
        return redirect('add_reviews')

    return render(request, 'add_reviews.html', {'exchanged_books': exchanged_books})

def book_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        Review.objects.create(
            book=book,
            reviewer=request.user,
            rating=request.POST.get('rating'),
            review_text=request.POST.get('review_text'),
            review_type='book'
        )
        return redirect('book_review', book_id=book.id)  # Redirect to refresh the page and avoid resubmission

    book_reviews = Review.objects.filter(book=book)
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
    
# def book_details_view(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
#     review_queryset = Review.objects.filter(
#         review_type='book'
#     ).select_related('reviewer').order_by('-created_at')

#     book = Book.objects.prefetch_related(
#         Prefetch('review_set', queryset=review_queryset, to_attr='recent_reviews')
#     ).get(id=book_id)

#     user_books = Book.objects.filter(owner=request.user)

#     return render(request, 'book_details.html', {
#         'book': book,
#         'user_books': user_books
#     })

def book_details_view(request, book_id):
    # Fetch the book and its reviews
    review_queryset = Review.objects.filter(
        review_type='book'
    ).select_related('reviewer').order_by('-created_at')

    book = Book.objects.prefetch_related(
        Prefetch('review_set', queryset=review_queryset, to_attr='recent_reviews')
    ).get(id=book_id)

    # If user is authenticated, get their books; otherwise, empty queryset
    user_books = Book.objects.none()
    if request.user.is_authenticated:
        user_books = Book.objects.filter(owner=request.user)

    return render(request, 'book_details.html', {
        'book': book,
        'user_books': user_books
    })

@login_required
def search(request):
    query = request.GET.get('q', '')
    user = request.user

    # Base query matching title, author, genre, or location
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query) |
        Q(genre__icontains=query) |
        Q(location__icontains=query)
    )

    # Filter books based on user role
    if user.is_authenticated:
        if user.user_type == 'Seeker':
            # Seeker sees only Owner books
            books = books.filter(owner__user_type='Owner')
        elif user.user_type == 'Owner':
            # Owner sees only Seeker books
            books = books.filter(owner__user_type='Seeker')
    else:
        # Unauthenticated users see only Owner books
        books = books.filter(owner__user_type='Owner')

    books = books.order_by('-created_at')

    context = {
        'books': books,
        'query': query
    }
    return render(request, 'book_list.html', context)
