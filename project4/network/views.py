from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Post
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

 
def index(request):
    # Перевірка, чи користувач аутентифікований
    if request.user.is_authenticated:
        # Отримати всі дописи автора, відсортовані за датою створення у зворотньому порядку
        author_posts = Post.objects.filter(user=request.user).order_by('-created_at')
        
        # Ініціалізувати об'єкт Paginator з постами автора та кількістю постів на сторінку (у нашому випадку - 10)
        paginator = Paginator(author_posts, 10)
        
        # Отримати номер поточної сторінки з параметру запиту (якщо не вказано, використовувати 1)
        page_number = request.GET.get('page', 1)
        
        # Отримати об'єкт сторінки за номером
        page = paginator.get_page(page_number)
        
        # Передати об'єкт сторінки у шаблон для відображення
        return render(request, "network/index.html", {'page': page})
    else:
        # Користувач не аутентифікований, повернути порожній список постів
        return render(request, "network/index.html", {'page': []})




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url='register')
def create_post_view(request):
    if request.method == 'POST':
        content = request.POST['post-text']  
        post = Post(user=request.user, content=content)
        post.save()
        return redirect('index')
    return render(request, 'network/create_post.html')
   

@login_required(login_url='register')
def all_posts_view(request):
    posts = Post.objects.all().order_by('-created_at')

    paginator = Paginator(posts, 10)  # Розділити список постів на сторінки, по 10 постів на сторінку
    page_number = request.GET.get('page')  # Отримати номер поточної сторінки

    page = paginator.get_page(page_number)  # Отримати об'єкт сторінки з постами

    return render(request, 'network/all_posts.html', {'page': page})




@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = False

    if request.user != profile_user:
        is_following = request.user in profile_user.followers.all()

    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'is_following': is_following,
        'posts': posts
    }

    return render(request, 'network/profile.html', context)



@login_required(login_url='register')
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    request.user.following.add(user_to_follow)
    messages.success(request, f'You are now following {user_to_follow.username}.')
    return redirect('profile', username=username)

@login_required(login_url='register')
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)
    messages.success(request, f'You have unfollowed {user_to_unfollow.username}.')
    return redirect('profile', username=username)



def subscriptions_view(request):
    user = request.user
    subscriptions = user.following.all()
    posts = Post.objects.filter(user__in=subscriptions).order_by('-created_at')

    paginator = Paginator(posts, 10)  # Розділити список постів на сторінки, по 10 постів на сторінку
    page_number = request.GET.get('page')  # Отримати номер поточної сторінки

    page = paginator.get_page(page_number)  # Отримати об'єкт сторінки з постами

    return render(request, 'network/following.html', {'page': page})
 
 

def update_post(request, post_id):
    if request.method == "POST":
        # Отримання допису за його ідентифікатором
        post = Post.objects.get(pk=post_id)
        
        # Перевірка, чи користувач є власником допису
        if post.user == request.user:
            # Отримання змінених даних з POST-запиту
            content = request.POST.get("content")
            
            # Оновлення вмісту допису
            post.content = content
            post.save()
            
            # Повернення успішного стану оновлення
            return JsonResponse({"success": True})
        else:
            # Повернення помилки, якщо користувач не є власником допису
            return JsonResponse({"success": False, "error": "You are not the owner of the post."})
    else:
        # Повернення помилки, якщо метод запиту не є POST
        return JsonResponse({"success": False, "error": "Invalid request method."})
 
 

def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        # Видаляємо лайк, якщо користувач вже вподобав допис
        post.likes.remove(user)
        is_liked = False
    else:
        # Додаємо лайк, якщо користувач ще не вподобав допис
        post.likes.add(user)
        is_liked = True

    likes_count = post.likes.count()

    return JsonResponse({"likes": likes_count, "is_liked": is_liked})

def posts(request):
    posts = Post.objects.all()
    context = {"page": posts}
    return render(request, "network/posts.html", context)

   