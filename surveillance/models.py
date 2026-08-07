from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from regions.models import Region


# ============================================================
# CHOIX RÉUTILISÉS DANS PLUSIEURS MODÈLES
# ============================================================

class StatutFormulaire(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    SOUMIS = "soumis", "Soumis"


class EtatAction(models.TextChoices):
    NON = "non", "Non"
    EN_COURS = "en_cours", "En cours"
    OUI = "oui", "Oui"


class TypeCasMaladie(models.TextChoices):
    SUSPECT = "suspect", "Suspect"
    CONFIRME = "confirme", "Confirmé"


class ClassificationWNV(models.TextChoices):
    SUSPECT = "suspect", "Suspect"
    PROBABLE = "probable", "Probable"
    CONFIRME = "confirme", "Confirmé"


class Genre(models.TextChoices):
    FEMININ = "feminin", "Féminin"
    MASCULIN = "masculin", "Masculin"
    AUTRE = "autre", "Autre / non précisé"


class EvolutionMAPI(models.TextChoices):
    GUERISON = "guerison", "Guérison"
    DECES = "deces", "Décès"
    EN_COURS = "en_cours", "Évolution en cours"


class NiveauRisque(models.TextChoices):
    FAIBLE = "faible", "Faible"
    MODERE = "modere", "Modéré"
    ELEVE = "eleve", "Élevé"


class StatutEvenement(models.TextChoices):
    EN_COURS = "en_cours", "En cours"
    CLOTURE = "cloture", "Clôturé"


# ============================================================
# FORMULAIRE PRINCIPAL
# ============================================================

class Formulaire(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="formulaires",
        verbose_name="Utilisateur ayant saisi le formulaire",
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="formulaires",
        verbose_name="Région concernée",
    )

    date_debut_semaine = models.DateField(
        verbose_name="Date de début de la semaine ISO",
    )

    date_fin_semaine = models.DateField(
        verbose_name="Date de fin de la semaine ISO",
    )

    date_saisie = models.DateField(
        verbose_name="Date de saisie et de soumission",
    )

    semaine_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Numéro de semaine ISO",
    )

    annee_iso = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Année ISO",
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutFormulaire.choices,
        default=StatutFormulaire.BROUILLON,
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

    class Meta:
        ordering = ["-annee_iso", "-semaine_iso", "-date_saisie"]

        constraints = [
            models.UniqueConstraint(
                fields=["utilisateur", "annee_iso", "semaine_iso"],
                name="formulaire_unique_par_utilisateur_et_semaine",
            )
        ]

    def clean(self):
        super().clean()

        if self.date_fin_semaine < self.date_debut_semaine:
            raise ValidationError(
                {
                    "date_fin_semaine": (
                        "La date de fin ne peut pas être antérieure "
                        "à la date de début."
                    )
                }
            )

        debut_iso = self.date_debut_semaine.isocalendar()
        fin_iso = self.date_fin_semaine.isocalendar()

        if (debut_iso.year, debut_iso.week) != (
            fin_iso.year,
            fin_iso.week,
        ):
            raise ValidationError(
                {
                    "date_fin_semaine": (
                        "Les dates de début et de fin doivent appartenir "
                        "à la même semaine ISO."
                    )
                }
            )

        if self.utilisateur_id:
            if self.utilisateur.role == "region":
                if self.utilisateur.region_id is None:
                    raise ValidationError(
                        "Le compte régional n'est associé à aucune région."
                    )

                if self.region_id != self.utilisateur.region_id:
                    raise ValidationError(
                        {
                            "region": (
                                "La région du formulaire doit correspondre "
                                "à la région du compte connecté."
                            )
                        }
                    )

            elif self.utilisateur.role == "central_humain":
                if self.region_id is not None:
                    raise ValidationError(
                        {
                            "region": (
                                "Le formulaire du central humain ne doit "
                                "pas être associé à une région."
                            )
                        }
                    )

            else:
                raise ValidationError(
                    "Seuls une région ou le central humain peuvent "
                    "remplir ce formulaire."
                )

    def save(self, *args, **kwargs):
        informations_iso = self.date_debut_semaine.isocalendar()

        self.semaine_iso = informations_iso.week
        self.annee_iso = informations_iso.year

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        if self.region:
            auteur = self.region.nom
        else:
            auteur = "Central humain"

        return (
            f"{auteur} - semaine ISO "
            f"{self.semaine_iso}/{self.annee_iso}"
        )


# ============================================================
# MALADIES À DÉCLARATION
# ============================================================

class Maladie(models.Model):
    nom = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nom de la maladie",
    )

    active = models.BooleanField(
        default=True,
        verbose_name="Disponible dans la liste",
    )

    def __str__(self):
        return self.nom


class FormulaireMaladie(models.Model):
    formulaire = models.ForeignKey(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="maladies_declarees",
        verbose_name="Formulaire",
    )

    maladie = models.ForeignKey(
        Maladie,
        on_delete=models.PROTECT,
        related_name="declarations",
        verbose_name="Maladie",
    )

    statut_enquete = models.CharField(
        max_length=20,
        choices=EtatAction.choices,
        default=EtatAction.NON,
        verbose_name="Enquête autour des cas",
    )

    date_enquete = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de l'enquête",
    )

    statut_riposte = models.CharField(
        max_length=20,
        choices=EtatAction.choices,
        default=EtatAction.NON,
        verbose_name="Riposte",
    )

    date_riposte = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de la riposte",
    )

    mesures_riposte = models.TextField(
        blank=True,
        verbose_name="Mesures de riposte",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["formulaire", "maladie"],
                name="maladie_unique_dans_un_formulaire",
            )
        ]

    def clean(self):
        super().clean()

        if self.statut_enquete == EtatAction.OUI and not self.date_enquete:
            raise ValidationError(
                {
                    "date_enquete": (
                        "La date de l'enquête est obligatoire "
                        "lorsque l'enquête est terminée."
                    )
                }
            )

        if self.statut_riposte == EtatAction.OUI:
            erreurs = {}

            if not self.date_riposte:
                erreurs["date_riposte"] = (
                    "La date de riposte est obligatoire."
                )

            if not self.mesures_riposte:
                erreurs["mesures_riposte"] = (
                    "Les mesures de riposte sont obligatoires."
                )

            if erreurs:
                raise ValidationError(erreurs)

    def __str__(self):
        return f"{self.maladie} - {self.formulaire}"


class CasMaladie(models.Model):
    formulaire_maladie = models.ForeignKey(
        FormulaireMaladie,
        on_delete=models.CASCADE,
        related_name="cas",
        verbose_name="Maladie déclarée",
    )

    type_cas = models.CharField(
        max_length=20,
        choices=TypeCasMaladie.choices,
        verbose_name="Type du cas",
    )

    date_confirmation = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de confirmation",
    )

    date_declaration = models.DateField(
        verbose_name="Date de déclaration",
    )

    hospitalise = models.BooleanField(
        default=False,
        verbose_name="Hospitalisé",
    )

    date_hospitalisation = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'hospitalisation",
    )

    decede = models.BooleanField(
        default=False,
        verbose_name="Décédé",
    )

    date_deces = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date du décès",
    )

    def clean(self):
        super().clean()

        erreurs = {}

        if (
            self.type_cas == TypeCasMaladie.CONFIRME
            and not self.date_confirmation
        ):
            erreurs["date_confirmation"] = (
                "La date de confirmation est obligatoire "
                "pour un cas confirmé."
            )

        if self.hospitalise and not self.date_hospitalisation:
            erreurs["date_hospitalisation"] = (
                "La date d'hospitalisation est obligatoire."
            )

        if not self.hospitalise and self.date_hospitalisation:
            erreurs["date_hospitalisation"] = (
                "Supprimez cette date puisque le cas "
                "n'est pas hospitalisé."
            )

        if self.decede and not self.date_deces:
            erreurs["date_deces"] = (
                "La date du décès est obligatoire."
            )

        if not self.decede and self.date_deces:
            erreurs["date_deces"] = (
                "Supprimez cette date puisque le cas "
                "n'est pas décédé."
            )

        if erreurs:
            raise ValidationError(erreurs)

    def __str__(self):
        return (
            f"{self.get_type_cas_display()} - "
            f"{self.formulaire_maladie.maladie}"
        )


# ============================================================
# WNV - ENTITÉS SÉPARÉES
# ============================================================

class DeclarationWNV(models.Model):
    formulaire = models.OneToOneField(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="declaration_wnv",
        verbose_name="Formulaire",
    )

    statut_enquete = models.CharField(
        max_length=20,
        choices=EtatAction.choices,
        default=EtatAction.NON,
        verbose_name="Enquête autour des cas",
    )

    date_enquete = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de l'enquête",
    )

    statut_riposte = models.CharField(
        max_length=20,
        choices=EtatAction.choices,
        default=EtatAction.NON,
        verbose_name="Riposte",
    )

    date_riposte = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de la riposte",
    )

    mesures_riposte = models.TextField(
        blank=True,
        verbose_name="Mesures de riposte",
    )

    def __str__(self):
        return f"WNV - {self.formulaire}"


class CasWNV(models.Model):
    declaration_wnv = models.ForeignKey(
        DeclarationWNV,
        on_delete=models.CASCADE,
        related_name="cas",
        verbose_name="Déclaration WNV",
    )

    classification = models.CharField(
        max_length=20,
        choices=ClassificationWNV.choices,
        verbose_name="Classification du cas",
    )

    decede = models.BooleanField(
        default=False,
        verbose_name="Décédé",
    )

    date_deces = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date du décès",
    )

    def clean(self):
        super().clean()

        if self.decede and not self.date_deces:
            raise ValidationError(
                {
                    "date_deces": (
                        "La date du décès est obligatoire "
                        "pour un cas décédé."
                    )
                }
            )

        if not self.decede and self.date_deces:
            raise ValidationError(
                {
                    "date_deces": (
                        "Supprimez cette date puisque le cas "
                        "n'est pas décédé."
                    )
                }
            )

    def __str__(self):
        return self.get_classification_display()


# ============================================================
# MAPI
# ============================================================

class CasMAPI(models.Model):
    formulaire = models.ForeignKey(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="cas_mapi",
        verbose_name="Formulaire",
    )

    age = models.PositiveSmallIntegerField(
        verbose_name="Âge",
    )

    genre = models.CharField(
        max_length=20,
        choices=Genre.choices,
        verbose_name="Genre",
    )

    type_vaccin = models.CharField(
        max_length=200,
        verbose_name="Type de vaccin administré",
    )

    date_administration_vaccin = models.DateField(
        verbose_name="Date d'administration du vaccin",
    )

    date_apparition_symptomes = models.DateField(
        verbose_name="Date d'apparition des symptômes",
    )

    type_symptomes = models.TextField(
        verbose_name="Type de symptômes",
    )

    hospitalise = models.BooleanField(
        default=False,
        verbose_name="Hospitalisé",
    )

    date_hospitalisation = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'hospitalisation",
    )

    evolution = models.CharField(
        max_length=20,
        choices=EvolutionMAPI.choices,
        verbose_name="Évolution",
    )

    def clean(self):
        super().clean()

        erreurs = {}

        if self.hospitalise and not self.date_hospitalisation:
            erreurs["date_hospitalisation"] = (
                "La date d'hospitalisation est obligatoire."
            )

        if not self.hospitalise and self.date_hospitalisation:
            erreurs["date_hospitalisation"] = (
                "Supprimez cette date puisque le cas "
                "n'est pas hospitalisé."
            )

        if (
            self.date_apparition_symptomes
            < self.date_administration_vaccin
        ):
            erreurs["date_apparition_symptomes"] = (
                "La date d'apparition des symptômes ne peut pas "
                "précéder l'administration du vaccin."
            )

        if erreurs:
            raise ValidationError(erreurs)

    def __str__(self):
        return f"Cas MAPI - {self.formulaire}"


# ============================================================
# SURVEILLANCE SENTINELLE
# ============================================================

class SurveillanceSentinelle(models.Model):
    SEUIL_ILI = 7.13

    formulaire = models.OneToOneField(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="surveillance_sentinelle",
        verbose_name="Formulaire",
    )

    proportion_ili = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Proportion ILI (%)",
    )

    nombre_sari = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre de cas SARI hospitalisés",
    )

    proportion_diarrhees = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Proportion de diarrhées aiguës (%)",
    )

    proportion_conjonctivites = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Proportion de conjonctivites aiguës (%)",
    )

    @property
    def situation_seuil_ili(self):
        if self.proportion_ili is None:
            return "Non renseigné"

        if self.proportion_ili > self.SEUIL_ILI:
            return "Au-dessus du seuil"

        if self.proportion_ili < self.SEUIL_ILI:
            return "Au-dessous du seuil"

        return "Égal au seuil"

    def __str__(self):
        return f"Surveillance sentinelle - {self.formulaire}"


# ============================================================
# SURVEILLANCE BASÉE SUR LES ÉVÉNEMENTS
# ============================================================

class Evenement(models.Model):
    TYPE_CHOICES = [
        ("biologique", "Biologique"),
        ("chimique", "Chimique"),
        ("radiologique", "Radiologique"),
        ("nucleaire", "Nucléaire"),
    ]

    formulaire = models.ForeignKey(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="evenements",
        verbose_name="Formulaire",
    )

    identifiant_evenement = models.CharField(
        max_length=50,
        verbose_name="Identifiant de l'évènement",
    )

    type_evenement = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type d'évènement",
    )

    nature_evenement = models.CharField(
        max_length=250,
        verbose_name="Nature de l'évènement",
    )

    autre_nature = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Autre nature à préciser",
    )

    date_occurrence = models.DateField(
        verbose_name="Date d'occurrence",
    )

    lieu_occurrence = models.CharField(
        max_length=200,
        verbose_name="Lieu d'occurrence",
    )

    date_detection = models.DateField(
        verbose_name="Date de détection",
    )

    source_detection = models.CharField(
        max_length=250,
        verbose_name="Source de détection",
    )

    autre_source_detection = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Autre source de détection",
    )

    date_confirmation = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de confirmation",
    )

    source_verification = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Source de vérification",
    )

    niveau_risque = models.CharField(
        max_length=20,
        choices=NiveauRisque.choices,
        verbose_name="Évaluation rapide du risque",
    )

    mesures_riposte = models.TextField(
        blank=True,
        verbose_name="Mesures de riposte",
    )

    date_debut_riposte = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début de la riposte",
    )

    date_fin_riposte = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin de la riposte",
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutEvenement.choices,
        default=StatutEvenement.EN_COURS,
        verbose_name="Statut de l'évènement",
    )

    difficultes = models.TextField(
        blank=True,
        verbose_name="Difficultés d'investigation et de riposte",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["formulaire", "identifiant_evenement"],
                name="identifiant_evenement_unique_par_formulaire",
            )
        ]

    def clean(self):
        super().clean()

        erreurs = {}

        if self.date_detection < self.date_occurrence:
            erreurs["date_detection"] = (
                "La date de détection ne peut pas précéder "
                "la date d'occurrence."
            )

        if (
            self.date_fin_riposte
            and not self.date_debut_riposte
        ):
            erreurs["date_debut_riposte"] = (
                "Indiquez d'abord la date de début de la riposte."
            )

        if (
            self.date_debut_riposte
            and self.date_fin_riposte
            and self.date_fin_riposte < self.date_debut_riposte
        ):
            erreurs["date_fin_riposte"] = (
                "La date de fin ne peut pas précéder "
                "la date de début de la riposte."
            )

        if erreurs:
            raise ValidationError(erreurs)

    def __str__(self):
        return self.identifiant_evenement


# ============================================================
# CONCLUSIONS DES DEUX GRANDES PARTIES
# ============================================================

class ConclusionIndicateurs(models.Model):
    formulaire = models.OneToOneField(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="conclusion_indicateurs",
        verbose_name="Formulaire",
    )

    conclusions = models.TextField(
        blank=True,
        verbose_name="Principales conclusions",
    )

    difficultes = models.TextField(
        blank=True,
        verbose_name="Difficultés",
    )

    recommandations = models.TextField(
        blank=True,
        verbose_name="Recommandations",
    )

    def __str__(self):
        return f"Conclusion indicateurs - {self.formulaire}"


class ConclusionEvenements(models.Model):
    formulaire = models.OneToOneField(
        Formulaire,
        on_delete=models.CASCADE,
        related_name="conclusion_evenements",
        verbose_name="Formulaire",
    )

    conclusions = models.TextField(
        blank=True,
        verbose_name="Principales conclusions",
    )

    difficultes = models.TextField(
        blank=True,
        verbose_name="Difficultés",
    )

    recommandations = models.TextField(
        blank=True,
        verbose_name="Recommandations",
    )

    def __str__(self):
        return f"Conclusion évènements - {self.formulaire}"