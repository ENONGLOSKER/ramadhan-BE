from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class JadwalSalat(models.Model):
    # lokasi = models.CharField(max_length=100, unique=True)  # Nama lokasi (misalnya: Jakarta, Bandung)
    tanggal = models.DateField()  # Tanggal jadwal salat
    imsak = models.TimeField()  # Waktu imsak
    subuh = models.TimeField()  # Waktu subuh
    dzuhur = models.TimeField()  # Waktu dzuhur
    ashar = models.TimeField()  # Waktu ashar
    maghrib = models.TimeField()  # Waktu maghrib
    isya = models.TimeField()  # Waktu isya

    def __str__(self):
        return f"{self.tanggal}"

class AdzanSound(models.Model):
    nama = models.CharField(max_length=100)  # Nama suara adzan (misalnya: Adzan Turki, Adzan Mesir)
    file = models.FileField(upload_to='adzan_sounds/')  # File suara adzan

    def __str__(self):
        return self.nama
    
class MisiRamadan(models.Model):
    tanggal = models.DateField()  # Tanggal misi
    deskripsi = models.TextField()  # Deskripsi misi
    selesai = models.BooleanField(default=False)  # Status misi (selesai/belum)

    def __str__(self):
        return f"Misi {self.tanggal}: {self.deskripsi}"

class PencapaianPengguna(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Pengguna yang menyelesaikan misi
    misi = models.ForeignKey(MisiRamadan, on_delete=models.CASCADE)  # Misi yang diselesaikan
    selesai_pada = models.DateTimeField(auto_now_add=True)  # Waktu misi diselesaikan

    def __str__(self):
        return f"{self.user.username} menyelesaikan misi: {self.misi.deskripsi}"
    
class AktivitasIbadah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Pengguna yang melakukan aktivitas
    jenis_aktivitas = models.CharField(max_length=100)  # Jenis aktivitas (salat, baca Quran, sedekah, dll)
    poin = models.IntegerField()  # Poin yang didapat dari aktivitas
    dibuat_pada = models.DateTimeField(auto_now_add=True)  # Waktu aktivitas dilakukan

    def __str__(self):
        return f"{self.user.username} - {self.jenis_aktivitas} ({self.poin} poin)"

class PohonAmal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Pengguna pemilik pohon
    daun = models.IntegerField(default=0)  # Jumlah daun
    bunga = models.IntegerField(default=0)  # Jumlah bunga
    buah = models.IntegerField(default=0)  # Jumlah buah
    terakhir_diupdate = models.DateTimeField(auto_now=True)  # Waktu terakhir pohon diupdate

    def __str__(self):
        return f"Pohon Amal {self.user.username}"

    def update_pertumbuhan(self):
        # Hitung total poin dari aktivitas ibadah
        total_poin = AktivitasIbadah.objects.filter(user=self.user).aggregate(models.Sum('poin'))['poin__sum'] or 0

        # Tentukan pertumbuhan pohon berdasarkan poin
        self.daun = total_poin // 1  # 1 poin = 1 daun
        self.bunga = total_poin // 5  # 5 poin = 1 bunga
        self.buah = total_poin // 10  # 10 poin = 1 buah
        self.save()