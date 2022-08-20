from django.db import models

class Room(models.Model):
    num=models.IntegerField(primary_key=True)
    code=models.CharField(max_length=16)
    name=models.CharField(max_length=30)
    password=models.CharField(max_length=60)
    color=models.CharField(max_length=10)
    game=models.IntegerField()
    max_player=models.IntegerField()
    players=models.JSONField()
    status=models.IntegerField()
    class Meta:
        db_table = "room"