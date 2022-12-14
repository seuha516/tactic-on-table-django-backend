from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<code>\w+)/$', consumers.ChatConsumer),
    re_path(r'ws/chat/(?P<code>\w+)/(?P<password>\w+)/$', consumers.ChatConsumer),
]