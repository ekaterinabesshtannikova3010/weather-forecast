from django.db import models
from django.contrib.auth.models import User

class CitySearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    city_name = models.CharField(max_length=100)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'city_name')

    def __str__(self):
        return f"{self.city_name} searched {self.search_count} times by {self.user.username}"
