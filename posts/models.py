from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from comments.models import Comment

from markdown_deux import markdown

# Create your models here.

class PostManager(models.Manager):

    def active(self, *args, **kwargs):
        qs = super(PostManager, self).filter(draft=False)
        return qs

    def all_of_user(self, user, *args, **kwargs):
        qs = super(PostManager, self).filter(
                        (models.Q(user=user) & models.Q(draft=True)) |
                        models.Q(draft=False)
                        ).distinct()
        return qs


def upload_location(instance, filename):
    #new post or first post
    try:
        new_id = Post.objects.all().last().id +1
    except:
        new_id = 1
    #for post update
    try:
        if instance.id:
            new_id = instance.id
    except:
        pass

    return "{}/{}".format(new_id, filename)


class Post(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=180)
    content = models.TextField()
    image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    slug = models.SlugField(unique=True)
    draft = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = PostManager()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"slug":self.slug, })

    def get_marked_content(self):
        return mark_safe(markdown(self.content))

    class Meta():
        ordering = ["-update"]


    @property
    def get_content_type(self):
        qs = ContentType.objects.get_for_model(self.__class__)
        return qs

    @property
    def comments(self):
        qs = Comment.objects.filter_by_instance(self)
        return qs




def create_slug(instance, new_slug=None):
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    check_slug = Post.objects.filter(slug=slug)
    if check_slug.exists():
        slug = "{}-{}".format(slug, check_slug.last().id )
        slug = create_slug(instance, slug)
    return slug

def pre_save_post_receiver(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)
