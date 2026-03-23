from django.db import models
from django.conf import settings

class Grain(models.Model):
    CATEGORY_CHOICES = [
        ('cereal', 'Cereal'), ('legume', 'Legume'),
        ('seed', 'Seed'), ('supplement', 'Supplement'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    protein_percent = models.FloatField()
    fat_percent = models.FloatField()
    carb_percent = models.FloatField()
    fiber_percent = models.FloatField()
    calories_per_100g = models.FloatField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'grains'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.protein_percent}% protein)"


class FeedFormula(models.Model):
    PURPOSE_CHOICES = [
        ('racing', 'Racing'),
        ('breeding', 'Breeding'),
        ('molting', 'Molting'),
        ('maintenance', 'Maintenance'),
        ('young', 'Young Pigeons'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_formulas',
        null=True, blank=True
    )
    name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    target_protein = models.FloatField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feed_formulas'

    def __str__(self):
        return self.name


class FeedFormulaItem(models.Model):
    formula = models.ForeignKey(
        FeedFormula, on_delete=models.CASCADE, related_name='items'
    )
    grain = models.ForeignKey(Grain, on_delete=models.CASCADE)
    percentage = models.FloatField()

    class Meta:
        db_table = 'feed_formula_items'