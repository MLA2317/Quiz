from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models.signals import pre_save

Profile = settings.AUTH_USER_MODEL


class AccountManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if username is None:
            raise TypeError('User should have a username')

        user = self.model(username=username, **extra_fields)  # user yasavolamiz
        user.set_password(password)
        user.save(using=self._db)  # db - bu settingdagi defoult database dan foydalansin
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        if password is None:
            raise TypeError("Password should not be None")

        user = self.create_user(
            username=username,
            password=password,
            **extra_fields
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Account(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, verbose_name='Username', db_index=True)
    avatar = models.ImageField(upload_to='account/', null=True)
    bio = models.TextField()
    is_superuser = models.BooleanField(default=False, verbose_name='Super user')
    is_staff = models.BooleanField(default=False, verbose_name='Staff user')
    is_active = models.BooleanField(default=True, verbose_name='Active user')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='Modified Date')

    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def image_tag(self):
        if self.avatar:
            return mark_safe(f"<a href='{self.avatar.url}'><img src='{self.avatar.url}' style='height:43px;'/></a>")
        else:
            return f"Not found"

    @property
    def avatar_url(self):
        if self.avatar:
            if settings.DEBUG:
                return f"{settings.LOCALE_BASE_URL}{self.avatar.url}"
            return f"{settings.PROD_BASE_URL}{self.avatar.url}"
        return None

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        data = {
            'refresh': str(refresh),  # bu - access token ni yangilab beradi
            'access': str(refresh.access_token)  # bu - saytga kirish un ruhsat
        }
        return data



