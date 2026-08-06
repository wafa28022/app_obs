from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from regions.models import Region


class UtilisateurManager(BaseUserManager):
    """
    Gestionnaire permettant de créer les utilisateurs avec leur adresse e-mail
    au lieu d'un nom d'utilisateur.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")

        email = self.normalize_email(email)

        utilisateur = self.model(
            email=email,
            **extra_fields,
        )

        utilisateur.set_password(password)
        utilisateur.full_clean()
        utilisateur.save(using=self._db)

        return utilisateur

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "encadrement")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    ROLE_REGION = "region"
    ROLE_CENTRAL_HUMAIN = "central_humain"
    ROLE_CNVZ = "cnvz"
    ROLE_ENCADREMENT = "encadrement"

    ROLE_CHOICES = [
        (ROLE_REGION, "Région"),
        (ROLE_CENTRAL_HUMAIN, "Central humain"),
        (ROLE_CNVZ, "CNVZ"),
        (ROLE_ENCADREMENT, "Encadrement"),
    ]

    # Le champ username de Django n'est plus utilisé.
    username = None

    email = models.EmailField(
        unique=True,
        verbose_name="Adresse e-mail",
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        verbose_name="Rôle",
    )

    region = models.OneToOneField(
        Region,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="utilisateur",
        verbose_name="Région",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    def clean(self):
        super().clean()

        if self.role == self.ROLE_REGION and self.region is None:
            raise ValidationError(
                {"region": "Une région doit être associée à un compte régional."}
            )

        if self.role != self.ROLE_REGION and self.region is not None:
            raise ValidationError(
                {
                    "region": (
                        "Seul un utilisateur de rôle Région peut être associé "
                        "à une région."
                    )
                }
            )

    def __str__(self):
        return self.email