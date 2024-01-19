from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    RANK_CHOICES = [
        ('-', '-'),
        ('CertyfikowanyWielkiChlop', 'CertyfikowanyWielkiChlop'),
        ('CertyfikowanyNarkoman', 'CertyfikowanyNarkoman'),
        ('CertyfikowanyAptekarz', 'CertyfikowanyAptekarz'),
        ('CertyfikowanyDomownik', 'CertyfikowanyDomownik'),
    ]
    username = models.CharField(max_length=32, unique=True)
    rank = models.CharField(max_length=50, choices=RANK_CHOICES, null=True, blank=True, default = '-')
    is_staff = models.BooleanField(default=False)
    image_certyfikowany_wielki_chlop = models.ImageField(upload_to='rank_images/CertyfikowanyWielkiChlop.jpg', null=True, blank=True)
    image_certyfikowany_narkoman = models.ImageField(upload_to='rank_images/', null=True, blank=True)

    USERNAME_FIELD = 'username'
    objects = CustomUserManager()
    def __str__(self):
        return self.username
    
    def get_rank_image_name(self):
        for rank_choice in self.RANK_CHOICES:
            if rank_choice[0] == self.rank:
                print(f"{rank_choice[0]}.jpg")
                return f"{rank_choice[0]}.jpg"