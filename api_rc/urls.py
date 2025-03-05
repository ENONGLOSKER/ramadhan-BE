from django.urls import path
from .views import (
    jadwal_salat,
    adzan_sound,
    hitung_mundur,
    update_jadwal_salat,
    waktu_sholat_sekarang,
    misi_harian, tandai_misi_selesai, statistik_pencapaian,
    tambah_aktivitas, lihat_pohon_amal, bandingkan_pohon_amal,
    countdown_waktu_sholat,
)

urlpatterns = [
    path('countdown_waktu/', countdown_waktu_sholat, name='countdown_waktu'),
    path('jadwal-salat/', jadwal_salat, name='jadwal-solat'),
    path('adzan-sound/', adzan_sound, name='adzan-sound'),
    path('hitung-mundur/', hitung_mundur, name='hitung-mundur'),
    path('update-jadwal-salat/', update_jadwal_salat, name='update-jadwal-salat'),
    path('waktu-sholat-sekarang/', waktu_sholat_sekarang, name='waktu-sholat-sekarang'),
    # misi
    path('misi-harian/', misi_harian, name='misi-harian'),
    path('tandai-misi-selesai/', tandai_misi_selesai, name='tandai-misi-selesai'),
    path('statistik-pencapaian/', statistik_pencapaian, name='statistik-pencapaian'),
    # pohon
    path('tambah-aktivitas/', tambah_aktivitas, name='tambah-aktivitas'),
    path('lihat-pohon-amal/', lihat_pohon_amal, name='lihat-pohon-amal'),
    path('bandingkan-pohon-amal/<int:user_id>/', bandingkan_pohon_amal, name='bandingkan-pohon-amal'),
]