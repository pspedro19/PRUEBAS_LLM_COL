#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    user = User.objects.get(username='kmj')
    print(f'✅ Usuario: {user.username} (ID: {user.id})')
    
    try:
        token = Token.objects.get(user=user)
        print(f'✅ Token existe: {token.key[:20]}...')
        print(f'📅 Token creado: {token.created}')
    except Token.DoesNotExist:
        print('❌ No tiene token! Creando...')
        token = Token.objects.create(user=user)
        print(f'✅ Token creado: {token.key[:20]}...')
        
    print(f'🔑 Token completo: {token.key}')
    
except User.DoesNotExist:
    print('❌ Usuario kmj no encontrado') 