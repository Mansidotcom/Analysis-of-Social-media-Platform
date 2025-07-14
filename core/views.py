from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from core.utils import is_spam
from .models import Post


from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random

import os
from django.conf import settings



@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # User suggestions
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        try:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)
        except User.DoesNotExist:
            continue

    new_suggestions_list = [x for x in list(all_users) if x not in list(user_following_all)]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in new_suggestions_list if x not in list(current_user)]
    random.shuffle(final_suggestions_list)

    username_profile_list = []
    for user in final_suggestions_list[:4]:
        profile = Profile.objects.filter(id_user=user.id).first()
        if profile:
            username_profile_list.append(profile)

    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts': feed_list,
        'suggestions_username_profile_list': username_profile_list
    })

@login_required(login_url='signin')

def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption', '')

        # Debug prints
        print(f"Caption received: {caption}")
        spam_result = is_spam(caption)
        print(f"Spam detected? {spam_result}")

        if image:
            Post.objects.create(
                user=user,
                image=image,
                caption=caption,
                is_spam=spam_result
            )
        return redirect('/')
    return redirect('/')



@login_required(login_url='signin')
def search(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})
    username_profile_list = []

    if request.method == 'POST':
        username = request.POST.get('username', '')
        username_object = User.objects.filter(username__icontains=username)

        for user in username_object:
            profile = Profile.objects.filter(id_user=user.id).first()
            if profile:
                username_profile_list.append(profile)

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect('/')

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
    else:
        like_filter.delete()
        post.no_of_likes -= 1

    post.save()
    return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    try:
        user_object = User.objects.get(username=pk)
        user_profile, _ = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})
    except User.DoesNotExist:
        return redirect('/')

    user_posts = Post.objects.filter(user=pk)
    user_post_length = user_posts.count()

    follower = request.user.username
    user = pk

    button_text = 'Unfollow' if FollowersCount.objects.filter(follower=follower, user=user).exists() else 'Follow'

    user_followers = FollowersCount.objects.filter(user=pk).count()
    user_following = FollowersCount.objects.filter(follower=pk).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        follow_obj = FollowersCount.objects.filter(follower=follower, user=user).first()

        if follow_obj:
            follow_obj.delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)

        return redirect('/profile/' + user)
    return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'id_user': request.user.id})

    if request.method == 'POST':
        image = request.FILES.get('image')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')

        if image:
            user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                Profile.objects.create(user=user, id_user=user.id)
                return redirect('settings')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('signin')

    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')



def post_message(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if not content:
            messages.error(request, "Content can't be empty.")
            return redirect('/')

        label = is_spam(content)

        Post.objects.create(user=request.user, content=content, is_spam=(label == "spam"))
        return redirect('/')

    return redirect('/')

