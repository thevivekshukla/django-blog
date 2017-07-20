from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CommentForm
from .models import Comment

# Create your views here.


@login_required
def comment_delete(request, id):
    instance = get_object_or_404(Comment, id=id)
    if not (request.user == instance.user or request.user.is_superuser or instance.content_object.user == request.user):
        messages.error(request, "You don't have permission to delete this comment.")
        return HttpResponseRedirect(instance.content_object.get_absolute_url())

    response = request.POST.get("response")
    if response == "Yes":
        content_object = instance.content_object
        instance.delete()
        messages.success(request, "Comment successfully deleted.")
        return HttpResponseRedirect(content_object.get_absolute_url())
    elif response == "No":
        messages.info(request, "Comment is not deleted.")
        return HttpResponseRedirect(instance.content_object.get_absolute_url())

    context = {
        "title": 'Delete "{}" ?'.format(instance.content),
        "instance": instance,
    }

    return render(request, "comment_delete.html", context)



def comment_thread(request, id):

    instance = get_object_or_404(Comment, id=id)

    if instance.parent != None:
        return HttpResponseRedirect(instance.parent.get_absolute_url())

    initial_data = {
        "content_type": instance.content_type,
        "object_id": instance.object_id,
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
            return HttpResponseRedirect(new_comment.get_absolute_url())
            # return HttpResponseRedirect(request.path)
        else:
            messages.error(request, "Some error occured, comment cannot be posted.")
            return HttpResponseRedirect(request.path)



    context = {
        "title": "Comment for: {}".format(instance.content_object.title),
        "comment": instance,
        "comment_form": comment_form,
    }

    return render(request, "comment_thread.html", context)
