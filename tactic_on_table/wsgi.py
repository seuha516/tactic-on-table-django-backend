import sys, os

path = os.path.abspath(__file__ + '../..')

if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tactic_on_table.settings')

application = get_wsgi_application()
