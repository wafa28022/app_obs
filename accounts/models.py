from django.contrib.auth.models import AbstractUser
from django.db import models
from regions.models import Region

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('region', 'Région'),
        ('central', 'Central'),
        ('encadrement', 'Encadrement'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    region = models.OneToOneField(
        Region, on_delete=models.CASCADE,
        null=True, blank=True, related_name='utilisateur'
    )

    def __str__(self):
        return self.username