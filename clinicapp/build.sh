
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r ../requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
echo "from django.contrib.auth.models import User; \
User.objects.get_or_create(username='admin', email='admin@example.com', \
defaults={'is_staff': True, 'is_superuser': True}) \
if not User.objects.filter(username='admin').exists() else User.objects.filter(username='admin').first()" \
| python manage.py shell
