import os
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitap_pazari.settings')

import requests
import django
django.setup()

from django.contrib.auth.models import User
from faker import Faker


def set_user():
    fake = Faker(['en_US'])

    f_name = fake.first_name()  # Parantez ekledik
    l_name = fake.last_name()   # Parantez ekledik

    u_name = f'{f_name.lower()}_{l_name.lower()}'
    email = f'{u_name}@{fake.domain_name()}'
    print(f_name, l_name, email)

    user_check = User.objects.filter(username=u_name)
    
    while user_check.exists():
        u_name = u_name + str(random.randrange(1, 99))
        user_check = User.objects.filter(username=u_name)

    user = User(
        username=u_name,
        first_name=f_name,
        last_name=l_name,
        email=email,
        is_staff = fake.boolean(chance_of_getting_true=50),
    )   
    
    user.set_password('1234')
    user.save()
    print('Kullanıcı Kaydedildi.', u_name)
    
    
    
from pprint import pprint
from kitaplar.api.serializers import KitapSerializer
from datetime import datetime

def kitap_ekle(konu):
    fake = Faker(['en_US'])
    url = 'https://openlibrary.org/search.json'
    payload = {'q': konu}
    response = requests.get(url, params=payload)

    if response.status_code != 200:
        print('Hatalı istek yapıldı', response.status_code)
        return
        
    jsn = response.json()
    kitaplar = jsn.get('docs')

    for kitap in kitaplar:
        kitap_adi = kitap.get('title')
        yayin_yili = kitap.get('first_publish_year')

        # Eğer API'den yıl bilgisi geldiyse onu kullan, yoksa Faker'dan rastgele bir tarih al
        if yayin_yili:
            yayin_tarihi = datetime.strptime(f"{yayin_yili}-01-01", "%Y-%m-%d")
        else:
            yayin_tarihi = fake.date_time_between(start_date='-10y', end_date='now')

        data = dict(
            isim=kitap_adi,
            yazar=kitap.get('author_name', ['Bilinmeyen Yazar'])[0],
            aciklama='-'.join(kitap.get('ia', [])) if isinstance(kitap.get('ia'), list) else "Açıklama bulunamadı",
            yayin_tarihi=yayin_tarihi.strftime('%Y-%m-%d %H:%M:%S'),  # Django formatına uygun hale getirdik
        )

        serializer = KitapSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print('Kitap kaydedildi:', kitap_adi)
        else:
            print('Eklenmedi')
            print(serializer.errors)

