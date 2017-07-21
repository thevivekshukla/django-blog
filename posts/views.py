from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from comments.forms import CommentForm
from comments.models import Comment

from .forms import PostForm
from .models import Post
# Create your views here.



def post_list(request):
    object_list = Post.objects.active()
    if request.user.is_superuser:
        object_list = Post.objects.all()
    elif request.user.is_staff:
        object_list = Post.objects.all_of_user(request.user)

    #search functionality
    query_list = []
    q = request.GET.get("q")
    if q:
        query = q.split()
        for q in query:
            query_list += object_list.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(user__username__icontains=q) |
                Q(slug__icontains=q)
            ).distinct()
        object_list = query_list


    paginator = Paginator(object_list, 5)

    page = request.GET.get("p")

    try:
        objects = paginator.page(page)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        objects = paginator.page(1)

    context = {
        "objects": objects,
        "title": "All posts",
    }

    return render(request, "post_list.html", context)



@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('accounts:login'))
def post_create(request):

    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        print(form.cleaned_data)
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Post successfully created.")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": "Create New Post",
        "form": form,
    }

    return render(request, "post_form.html", context)




def post_detail(request, slug):
    instance = get_object_or_404(Post, slug=slug)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id,
    }

    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        object_id = int(comment_form.cleaned_data.get("object_id"))
        content = comment_form.cleaned_data.get("content")
        parent_obj = None
        user = request.user

        parent_id = request.POST.get("parent_id")
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs and parent_qs.count()==1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
                                content=content,
                                parent=parent_obj,
                                content_type=content_type,
                                object_id=object_id,
                                user=user,
                            )

        if created:
            messages.success(request, "Comment successfully submitted.")
            return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
        else:
            messages.error(request, "Some error occured, comment cannot be posted.")
            return HttpResponseRedirect(instance.get_absolute_url())


    context = {
        "title": instance.title,
        "instance": instance,
        "comment_form": comment_form,
    }

    return render(request, "post_detail.html", context)




@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('accounts:login'))
def post_update(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not the author of this post.")
        return HttpResponseRedirect(instance.get_absolute_url())
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)

    if form.is_valid():
        print(form.cleaned_data)
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Post successfully updated.")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": "Update Post",
        "form": form,
    }

    return render(request, "post_form.html", context)




@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('accounts:login'))
def post_delete(request, slug):
    instance = get_object_or_404(Post, slug=slug)

    if instance.user != request.user and not request.user.is_superuser:
        messages.error(request, "You cannot delete this post as you are not the author.")
        return HttpResponseRedirect(instance.get_absolute_url())

    response = request.POST.get("response")
    if response == "Yes":
        instance.delete()
        messages.success(request, "Post successfully deleted.")
        return HttpResponseRedirect("/")
    elif response == "No":
        messages.warning(request, "Post deletion cancelled.")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
    }

    return render(request, "post_delete.html", context)



@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('accounts:login'))
def post_draft(request):

    object_list = Post.objects.all_of_user(request.user).filter(draft=True)
    if request.user.is_superuser:
        object_list = Post.objects.all().filter(draft=True)

    paginator = Paginator(object_list, 5)

    page = request.GET.get("p")

    try:
        objects = paginator.page(page)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        objects = paginator.page(1)

    context = {
        "objects": objects,
        "title": "All Drafts",
    }

    return render(request, "post_list.html", context)




@user_passes_test(lambda u:u.is_staff, login_url=reverse_lazy('accounts:login'))
def post_published(request):

    object_list = Post.objects.all_of_user(request.user).filter(draft=False)
    if request.user.is_superuser:
        object_list = Post.objects.all().filter(draft=False)

    paginator = Paginator(object_list, 5)

    page = request.GET.get("p")

    try:
        objects = paginator.page(page)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        objects = paginator.page(1)

    context = {
        "objects": objects,
        "title": "All published posts",
    }

    return render(request, "post_list.html", context)
