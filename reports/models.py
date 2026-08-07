from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from surveillance.models import Formulaire


# ============================================================
# CHOIX POUR LE STATUT DU RAPPORT GLOBAL
# ============================================================

class StatutRapportGlobal(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    GENERE = "genere", "Généré"


# ============================================================
# RAPPORT HEBDOMADAIRE DU CNVZ
# ============================================================

class RapportCNVZ(models.Model):
    depose_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rapports_cnvz_deposes",
        verbose_name="Déposé par",
    )

    titre = models.CharField(
        max_length=200,
        verbose_name="Titre du rapport",
    )

    date_debut_semaine = models.DateField(
        verbose_name="Date de début de la semaine ISO",
    )

    date_fin_semaine = models.DateField(
        verbose_name="Date de fin de la semaine ISO",
    )

    semaine_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Numéro de semaine ISO",
    )

    annee_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Année ISO",
    )

    fichier_rapport = models.FileField(
        upload_to="rapports_cnvz/%Y/%m/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "ppt", "pptx"],
            )
        ],
        verbose_name="Rapport CNVZ ",
    )

    depose_le = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date et heure du dépôt",
    )

    modifie_le = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification",
    )

    class Meta:
        ordering = [
            "-annee_iso",
            "-semaine_iso",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["annee_iso", "semaine_iso"],
                name="rapport_cnvz_unique_par_semaine",
            )
        ]

        verbose_name = "Rapport CNVZ"
        verbose_name_plural = "Rapports CNVZ"

    def clean(self):
        super().clean()

        erreurs = {}

        if self.date_fin_semaine < self.date_debut_semaine:
            erreurs["date_fin_semaine"] = (
                "La date de fin ne peut pas être antérieure "
                "à la date de début."
            )

        debut_iso = self.date_debut_semaine.isocalendar()
        fin_iso = self.date_fin_semaine.isocalendar()

        if (debut_iso.year, debut_iso.week) != (
            fin_iso.year,
            fin_iso.week,
        ):
            erreurs["date_fin_semaine"] = (
                "Les deux dates doivent appartenir "
                "à la même semaine ISO."
            )

        if self.depose_par_id:
            if self.depose_par.role != "cnvz":
                erreurs["depose_par"] = (
                    "Seul un utilisateur de rôle CNVZ peut "
                    "déposer un rapport CNVZ."
                )

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        informations_iso = self.date_debut_semaine.isocalendar()

        self.semaine_iso = informations_iso.week
        self.annee_iso = informations_iso.year

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Rapport CNVZ - semaine ISO "
            f"{self.semaine_iso}/{self.annee_iso}"
        )


# ============================================================
# RAPPORT GLOBAL
# ============================================================

class RapportGlobal(models.Model):
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rapports_globaux_crees",
        verbose_name="Créé par",
    )

    date_debut_semaine = models.DateField(
        verbose_name="Date de début de la semaine ISO",
    )

    date_fin_semaine = models.DateField(
        verbose_name="Date de fin de la semaine ISO",
    )

    semaine_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Numéro de semaine ISO",
    )

    annee_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Année ISO",
    )

    formulaires = models.ManyToManyField(
        Formulaire,
        related_name="rapports_globaux",
        blank=True,
        verbose_name="Formulaires humains consolidés",
    )

    rapport_cnvz = models.OneToOneField(
        RapportCNVZ,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rapport_global",
        verbose_name="Rapport CNVZ associé",
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutRapportGlobal.choices,
        default=StatutRapportGlobal.BROUILLON,
        verbose_name="Statut",
    )

    cree_le = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le",
    )

    modifie_le = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le",
    )

    date_generation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de génération",
    )

    class Meta:
        ordering = [
            "-annee_iso",
            "-semaine_iso",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["annee_iso", "semaine_iso"],
                name="rapport_global_unique_par_semaine",
            )
        ]

        verbose_name = "Rapport global"
        verbose_name_plural = "Rapports globaux"

    def clean(self):
        super().clean()

        erreurs = {}

        if self.date_fin_semaine < self.date_debut_semaine:
            erreurs["date_fin_semaine"] = (
                "La date de fin ne peut pas être antérieure "
                "à la date de début."
            )

        debut_iso = self.date_debut_semaine.isocalendar()
        fin_iso = self.date_fin_semaine.isocalendar()

        if (debut_iso.year, debut_iso.week) != (
            fin_iso.year,
            fin_iso.week,
        ):
            erreurs["date_fin_semaine"] = (
                "Les deux dates doivent appartenir "
                "à la même semaine ISO."
            )

        if self.cree_par_id:
            if self.cree_par.role != "encadrement":
                erreurs["cree_par"] = (
                    "Seul un utilisateur de rôle Encadrement "
                    "peut créer un rapport global."
                )

        if self.rapport_cnvz_id:
            if (
                self.rapport_cnvz.annee_iso != debut_iso.year
                or self.rapport_cnvz.semaine_iso != debut_iso.week
            ):
                erreurs["rapport_cnvz"] = (
                    "Le rapport CNVZ doit correspondre "
                    "à la même semaine ISO."
                )

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        informations_iso = self.date_debut_semaine.isocalendar()

        self.semaine_iso = informations_iso.week
        self.annee_iso = informations_iso.year

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Rapport global - semaine ISO "
            f"{self.semaine_iso}/{self.annee_iso}"
        )


# ============================================================
# CONCLUSION GLOBALE
# ============================================================

class ConclusionGlobale(models.Model):
    rapport_global = models.OneToOneField(
        RapportGlobal,
        on_delete=models.CASCADE,
        related_name="conclusion_globale",
        verbose_name="Rapport global",
    )

    redigee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="conclusions_globales_redigees",
        verbose_name="Rédigée par",
    )

    texte = models.TextField(
        verbose_name="Conclusion globale",
    )

    creee_le = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créée le",
    )

    modifiee_le = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifiée le",
    )

    class Meta:
        verbose_name = "Conclusion globale"
        verbose_name_plural = "Conclusions globales"

    def clean(self):
        super().clean()

        if (
            self.redigee_par_id
            and self.redigee_par.role != "encadrement"
        ):
            raise ValidationError(
                {
                    "redigee_par": (
                        "Seul un utilisateur de rôle Encadrement "
                        "peut rédiger la conclusion globale."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Conclusion de {self.rapport_global}"