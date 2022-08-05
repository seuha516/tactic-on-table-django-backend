# from django.db import models
# from django.utils.formats import localize
# from rest_api.models import User, Study
#
#
# class Message(models.Model):
#     user = models.ForeignKey(to=User, on_delete=models.PROTECT)
#     study = models.ForeignKey(to=Study, on_delete=models.PROTECT)
#     content = models.TextField()
#     on_created = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.user.username + " " + self.content + " " + localize(self.on_created)