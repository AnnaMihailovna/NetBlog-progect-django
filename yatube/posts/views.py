from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()

POST_PER_PAGE = 10


def get_page(request, post_list):
    paginator = Paginator(post_list, POST_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(60 * 20)
def index(request):
    posts = Post.objects.all().select_related('author', 'group')
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(
        User.objects.prefetch_related('posts'), username=username)
    page_obj = get_page(request, author.posts.all())
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, list_of_posts)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect(reverse('posts:profile',
                    kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect(reverse('posts:profile',
                    kwargs={'username': author}))
