from django.db import models

class Game(models.Model):
    num=models.IntegerField(primary_key=True)
    data=models.JSONField()
    class Meta:
        db_table = "game"