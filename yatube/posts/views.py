from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


@cache_page(20, key_prefix='index_page')
def index(request):
    """Вьюшка для главной страницы."""
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = pagination(
        request,
        post_list,
        settings.POSTS_PER_PAGE
    )
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_post(request, slug):
    """Вьюшка для страницы групп."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(
        request,
        post_list,
        settings.POSTS_PER_PAGE
    )
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    """Вьюшка для страницы пользователя."""
    author = get_object_or_404(User, username=username)
    author_posts_list = author.posts.all()
    if author.following.filter(author=author).all():
        following = True
    else:
        following = False
    page_obj = pagination(
        request,
        author_posts_list,
        settings.POSTS_PER_PAGE
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Вьюшка для стриницы отдельного поста."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Вьюшка для создания поста."""
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


def pagination(request, posts_list, pages_on_screen):
    """Отдельный метод для пагинации."""
    paginator = Paginator(posts_list, pages_on_screen)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # user = Follow.objects.filter(user=request.user).select_related('author')
    # following_authors_list = User.objects.filter(following__in=user)
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(
        request,
        post_list,
        settings.POSTS_PER_PAGE
    )
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if not user == author and not Follow.objects.filter(user=user,
                                                        author=author).all():
        Follow.objects.create(user=user, author=author)
    return render(request, 'posts/follow.html')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return render(request, 'posts/follow.html')
