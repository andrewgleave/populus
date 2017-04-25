from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

MAX_BIO_LENGTH = 210


class BaseModel(models.Model):
    '''
    Custom model base class providing creation/mod timestamps
    '''

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfileManager(models.Manager):
    '''
    Manager methods for UserProfile model
    '''

    def create_slug(self, name):
        slug = slugify(name)
        count = 1
        while self.filter(slug=slug).exists() or slug in self.BAD_SLUGS:
            count += 1
            slug = '{}_{:d}'.format(slug, count)
        return slug


def user_avatar_path(instance, filename):
    '''
    user_avatar_path returns a formatted path within /media
    in which to store the avatar
    '''

    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(BaseModel):
    '''
    UserProfile represents our custom user attributes.

    This could be a custom User model but probably not worth
    the additional configuration here
    '''

    BAD_SLUGS = ('add', 'edit', 'remove')

    user = models.OneToOneField(User, related_name='profile')
    slug = models.SlugField(
        blank=True, unique=True, max_length=128, allow_unicode=True)
    photo = models.ImageField(blank=True, upload_to=user_avatar_path)
    bio = models.CharField(blank=True, max_length=MAX_BIO_LENGTH)
    site = models.URLField(blank=True)
    tags = ArrayField(blank=True, models.CharField(max_length=50))
    links = models.TextField(blank=True)

    class Meta:
        ordering = ['-id']
        get_latest_by = 'creation_date'

    objects = UserProfileManager()

    def __str__(self):
        return '{} ({})'.format(self.user.name, self.user.email)


#Signals
@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)