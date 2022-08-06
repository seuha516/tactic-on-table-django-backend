from django.db import models

class Account(models.Model):
    username=models.CharField(max_length=16, primary_key=True)
    hashed_password=models.CharField(max_length=255)
    email=models.CharField(max_length=50)
    nickname=models.CharField(max_length=12)
    image=models.CharField(max_length=255)
    total_score=models.IntegerField()
    score=models.JSONField()
    class Meta:
        db_table = "account"

class Match_record(models.Model):
    num=models.IntegerField()
    game=models.IntegerField()
    players=models.JSONField()
    result=models.JSONField()
    date=models.DateTimeField()
    class Meta:
        db_table = "match_record"