from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# Create your models here.


class CommentManager(models.Manager):

    def filter_by_instance(self, instance, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        object_id = instance.id
        qs = super(CommentManager, self).filter(content_type=content_type, object_id=object_id)
        return qs.filter(parent=None)


class Comment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        if self.parent != None:
            return reverse("comments:comment_thread", kwargs={"id":self.parent.id, })
        return reverse("comments:comment_thread", kwargs={"id":self.id, })

    def get_delete_url(self):
        return reverse("comments:comment_delete", kwargs={"id":self.id, })

    class Meta():
        ordering = ["-timestamp"]


    def children(self):
        qs = Comment.objects.filter(parent=self)
        return qs
