#!/bin/sh
set -e

echo "🍔 LanchoPro iniciando..."

echo "📦 Aplicando migrations..."
python manage.py migrate --noinput

echo "👤 Verificando usuário admin..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
u = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
p = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, password=p, email='admin@lanchopro.com')
    print('Superusuário criado:', u)
else:
    print('Superusuário já existe:', u)
"

echo "🌱 Verificando dados iniciais..."
python manage.py shell -c "
from estoque.models import Produto
if Produto.objects.count() == 0:
    import subprocess
    subprocess.run(['python', 'manage.py', 'seed_data'], check=True)
    print('Dados iniciais criados!')
else:
    print('Dados já existem:', Produto.objects.count(), 'produtos')
"

echo "🚀 Iniciando Gunicorn..."
exec gunicorn config.wsgi:application \
    --workers 2 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
