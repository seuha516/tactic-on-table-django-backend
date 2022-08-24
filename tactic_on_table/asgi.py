import os, django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tactic_on_table.settings')

django.setup()

application = get_default_application()