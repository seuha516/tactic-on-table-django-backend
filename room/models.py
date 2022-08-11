from django.db import models

class Room(models.Model):
    roomId=models.IntegerField()
    name=models.CharField(max_length=30)
    password=models.CharField(max_length=60)
    game=models.IntegerField()
    maxPeople=models.IntegerField()
    status=models.IntegerField()
    players=models.JSONField()
    class Meta:
        db_table = "room"