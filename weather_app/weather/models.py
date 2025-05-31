from django.db import models


class CitySearch(models.Model):
    name = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'поисковые запросы'
        ordering = ['-count']

    def __str__(self):
        return f'{self.name} ({self.count} поисков)'
