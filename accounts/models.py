from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.
class Accounts(User):
    # account_id=models.AutoField(primary_key=True)
    elo=models.FloatField(default=1500,validators=[MinValueValidator(1000)])
    image=models.ImageField(default='default.png',blank=True) 
    fbLink=models.URLField(unique=False)  
    instLink=models.URLField(unique=False)
    valid=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural='Accounts'

    def __str__(self):
        return self.username