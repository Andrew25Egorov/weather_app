from django.db import models


class CitySearch(models.Model):
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    search_count = models.PositiveIntegerField(default=1)
    last_search = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'City Searches'
        ordering = ['-search_count']

    def __str__(self):
        return f'{self.city_name} ({self.search_count} searches)'

    def increment_search_count(self):
        self.search_count += 1
        self.save()
