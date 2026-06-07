from django.db import models


class RemoteConfig(models.Model):
    """
    Singleton table (always pk=1) that holds remotely-controlled feature flags
    for the external company app. Edit values from Django admin — /admin/.
    """
    cam = models.BooleanField(
        default=False,
        verbose_name='Camera enabled',
        help_text='Controls whether the camera feature is active in the external app.',
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = 'app_remote_config'
        verbose_name  = 'Remote Config'
        verbose_name_plural = 'Remote Config'

    def __str__(self):
        return f'Remote Config (cam={"ON" if self.cam else "OFF"})'

    # ── Singleton enforcement ─────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Block deletion — the row should always exist
        pass

    @classmethod
    def get(cls):
        """Return the single config row, creating it with defaults if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
