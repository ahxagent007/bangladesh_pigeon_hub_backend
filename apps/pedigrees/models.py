from django.db import models
from apps.pigeons.models import Pigeon

class PedigreeRecord(models.Model):
    """Links a pigeon to its parents for pedigree tracking."""
    pigeon = models.OneToOneField(
        Pigeon, on_delete=models.CASCADE, related_name='pedigree'
    )
    sire = models.ForeignKey(  # Father
        Pigeon, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sire_of'
    )
    dam = models.ForeignKey(   # Mother
        Pigeon, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='dam_of'
    )
    notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pedigree_records'

    def __str__(self):
        return f"Pedigree of {self.pigeon.name}"

    def get_ancestors(self, depth=3):
        """Recursively fetch ancestor tree up to given depth."""
        def build_tree(pigeon, current_depth):
            if not pigeon or current_depth == 0:
                return None
            tree = {'pigeon': pigeon, 'sire': None, 'dam': None}
            try:
                record = pigeon.pedigree
                tree['sire'] = build_tree(record.sire, current_depth - 1)
                tree['dam'] = build_tree(record.dam, current_depth - 1)
            except PedigreeRecord.DoesNotExist:
                pass
            return tree
        return build_tree(self.pigeon, depth)