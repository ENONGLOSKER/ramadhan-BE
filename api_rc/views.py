from django.shortcuts import render, get_object_or_404
from .models import JadwalSalat, AdzanSound

# api
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import JadwalSalat, AdzanSound, MisiRamadan, PencapaianPengguna, AktivitasIbadah, PohonAmal
from .serializers import JadwalSalatSerializer, AdzanSoundSerializer, MisiRamadanSerializer, PencapaianPenggunaSerializer, AktivitasIbadahSerializer, PohonAmalSerializer
import pandas as pd
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
def countdown_waktu_sholat(request):
    # Ambil tanggal hari ini
    tanggal_sekarang = timezone.now().date()

    try:
        # Ambil jadwal salat untuk hari ini
        jadwal = JadwalSalat.objects.get(tanggal=tanggal_sekarang)
    except JadwalSalat.DoesNotExist:
        return Response({"error": "Jadwal salat tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

    # Ambil waktu saat ini
    sekarang = timezone.now().time()

    # Daftar waktu solat beserta nama sholatnya
    waktu_sholat = [
        {"nama": "Imsak", "waktu": jadwal.imsak},
        {"nama": "Subuh", "waktu": jadwal.subuh},
        {"nama": "Dzuhur", "waktu": jadwal.dzuhur},
        {"nama": "Ashar", "waktu": jadwal.ashar},
        {"nama": "Maghrib", "waktu": jadwal.maghrib},
        {"nama": "Isya", "waktu": jadwal.isya},
    ]

    # Cari waktu solat berikutnya
    sholat_berikutnya = None
    for sholat in waktu_sholat:
        if sekarang < sholat["waktu"]:
            sholat_berikutnya = sholat
            break

    # Jika tidak ada sholat berikutnya hari ini, gunakan Imsak besok
    if not sholat_berikutnya:
        try:
            jadwal_besok = JadwalSalat.objects.get(tanggal=tanggal_sekarang + timedelta(days=1))
            sholat_berikutnya = {"nama": "Imsak (Besok)", "waktu": jadwal_besok.imsak}
        except JadwalSalat.DoesNotExist:
            return Response({"error": "Jadwal salat besok tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

    # Hitung selisih waktu
    waktu_berikutnya = datetime.combine(tanggal_sekarang, sholat_berikutnya["waktu"])
    sekarang_datetime = datetime.combine(tanggal_sekarang, sekarang)
    selisih = waktu_berikutnya - sekarang_datetime

    # Jika waktu sholat berikutnya adalah besok, tambahkan 1 hari
    if selisih.total_seconds() < 0:
        waktu_berikutnya += timedelta(days=1)
        selisih = waktu_berikutnya - sekarang_datetime

    # Format countdown
    jam, sisa = divmod(int(selisih.total_seconds()), 3600)
    menit, detik = divmod(sisa, 60)
    countdown = f"{jam:02}:{menit:02}:{detik:02}"

    # Kembalikan respons API
    return Response({
        "sholat_berikutnya": sholat_berikutnya["nama"],
        "waktu_berikutnya": sholat_berikutnya["waktu"].strftime("%H:%M"),
        "countdown": countdown
    })

# Endpoint untuk mendapatkan jadwal salat berdasarkan tanggal
@api_view(['GET'])
def jadwal_salat(request):
    #  mengambil nilai dari parameter "tanggal"
    tanggal = request.GET.get('tanggal', None) #`request.GET`: Ini merupakan objek yang menangkap semua informasi query string dari permintaan HTTP.

    if tanggal:
        # jika tanggalnya ada maka ambil data berdasarkan tanggal tersebut
        jadwal = JadwalSalat.objects.filter(tanggal=tanggal)
    else:
        jadwal = JadwalSalat.objects.all()

    serializer = JadwalSalatSerializer(jadwal, many=True)
    return Response(serializer.data)

# Endpoint untuk mendapatkan daftar suara adzan
@api_view(['GET'])
def adzan_sound(request):
    sounds = AdzanSound.objects.all()
    serializer = AdzanSoundSerializer(sounds, many=True)
    return Response(serializer.data)

# Endpoint untuk mendapatkan hitung mundur ke waktu iftar
@api_view(['GET'])
def hitung_mundur(request):
    # parameter
    tanggal = request.GET.get('tanggal', None)

    if not tanggal:
        return Response({"error": "Parameter 'tanggal' diperlukan."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        jadwal = JadwalSalat.objects.get(tanggal=tanggal)
        waktu_sekarang = timezone.now().astimezone().time()

        # Menghitung mundur untuk setiap waktu solat
        waktu_solat = [jadwal.imsak, jadwal.subuh, jadwal.dzuhur, jadwal.ashar, jadwal.maghrib, jadwal.isya]
        nama_solat = ['Imsak', 'Subuh', 'Dzuhur', 'Ashar', 'Maghrib', 'Isya']
        hasil = {}

        for i, waktu in enumerate(waktu_solat):
            waktu_lengkap = datetime.combine(jadwal.tanggal, waktu).replace(tzinfo=timezone.get_current_timezone())
            selisih = waktu_lengkap - timezone.now()

            if selisih.total_seconds() < 0:
                hasil[nama_solat[i]] = "Sudah lewat"
            else:
                hasil[nama_solat[i]] = str(timedelta(seconds=selisih.seconds))

        return Response({
            "tanggal": jadwal.tanggal,
            "hasil": hasil
        })
    except JadwalSalat.DoesNotExist:
        return Response({"error": "Jadwal salat tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

# Endpoint untuk mengupdate jadwal salat melalui file Excel (Admin Only)
@api_view(['POST'])
def update_jadwal_salat(request):
    file = request.FILES.get('file', None)
    if not file:
        return Response({"error": "File Excel diperlukan."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            JadwalSalat.objects.update_or_create(
                tanggal=row['tanggal'],
                defaults={
                    'imsak': row['imsak'],
                    'subuh': row['subuh'],
                    'dzuhur': row['dzuhur'],
                    'ashar': row['ashar'],
                    'maghrib': row['maghrib'],
                    'isya': row['isya'],
                }
            )
        return Response({"status": "success", "message": "Jadwal salat berhasil diupdate."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Endpoint untuk mendapatkan waktu sholat sekarang
@api_view(['GET'])
def waktu_sholat_sekarang(request):
    sekarang = timezone.now().astimezone().time()
    print(f'data sekarang {sekarang}')
    print(sekarang.strftime("%H:%M"))
    try:
        jadwal = JadwalSalat.objects.get(tanggal=timezone.now().date())
        sholat_sekarang = None
        sholat_berikutnya = None
        waktu_berikutnya = None

        if sekarang < jadwal.imsak:
            sholat_sekarang = "Imsak"
            sholat_berikutnya = "Subuh"
            waktu_berikutnya = jadwal.subuh
        elif sekarang < jadwal.subuh:
            sholat_sekarang = "Subuh"
            sholat_berikutnya = "Dzuhur"
            waktu_berikutnya = jadwal.dzuhur
        elif sekarang < jadwal.dzuhur:
            sholat_sekarang = "Dzuhur"
            sholat_berikutnya = "Ashar"
            waktu_berikutnya = jadwal.ashar
        elif sekarang < jadwal.ashar:
            sholat_sekarang = "Ashar"
            sholat_berikutnya = "Maghrib"
            waktu_berikutnya = jadwal.maghrib
        elif sekarang < jadwal.maghrib:
            sholat_sekarang = "Maghrib"
            sholat_berikutnya = "Isya"
            waktu_berikutnya = jadwal.isya
        else:
            sholat_sekarang = "Isya"
            sholat_berikutnya = "Imsak (Besok)"
            waktu_berikutnya = jadwal.imsak

        return Response({
            "sholat_sekarang": sholat_sekarang,
            "waktu": sekarang.strftime("%H:%M"),
            "sholat_berikutnya": sholat_berikutnya,
            "waktu_berikutnya": waktu_berikutnya.strftime("%H:%M")
        })
    except JadwalSalat.DoesNotExist:
        return Response({"error": "Jadwal salat tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

# misi ramadahan
# Endpoint untuk mendapatkan misi harian
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def misi_harian(request):
    tanggal_sekarang = timezone.now().date()
    misi = MisiRamadan.objects.filter(tanggal=tanggal_sekarang).first()

    if not misi:
        return Response({"error": "Tidak ada misi untuk hari ini."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MisiRamadanSerializer(misi)
    return Response(serializer.data)

# Endpoint untuk menandai misi sebagai selesai
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tandai_misi_selesai(request):
    tanggal_sekarang = timezone.now().date()
    misi = MisiRamadan.objects.filter(tanggal=tanggal_sekarang).first()

    if not misi:
        return Response({"error": "Tidak ada misi untuk hari ini."}, status=status.HTTP_404_NOT_FOUND)

    # Cek apakah pengguna sudah menyelesaikan misi ini
    if PencapaianPengguna.objects.filter(user=request.user, misi=misi).exists():
        return Response({"error": "Misi sudah ditandai sebagai selesai."}, status=status.HTTP_400_BAD_REQUEST)

    # Tandai misi sebagai selesai
    PencapaianPengguna.objects.create(user=request.user, misi=misi)
    return Response({"status": "success", "message": "Misi berhasil ditandai sebagai selesai."})

# Endpoint untuk melihat statistik pencapaian pengguna
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistik_pencapaian(request):
    pencapaian = PencapaianPengguna.objects.filter(user=request.user)
    total_misi = MisiRamadan.objects.count()
    total_selesai = pencapaian.count()

    serializer = PencapaianPenggunaSerializer(pencapaian, many=True)
    return Response({
        "total_misi": total_misi,
        "total_selesai": total_selesai,
        "pencapaian": serializer.data
    })


# phon
# Endpoint untuk menambahkan aktivitas ibadah
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tambah_aktivitas(request):
    jenis_aktivitas = request.data.get('jenis_aktivitas', None)
    if not jenis_aktivitas:
        return Response({"error": "Jenis aktivitas diperlukan."}, status=status.HTTP_400_BAD_REQUEST)

    # Tentukan poin berdasarkan jenis aktivitas
    poin_mapping = {
        'salat': 5,
        'baca_quran': 3,
        'sedekah': 2,
        'doa': 1,
    }
    poin = poin_mapping.get(jenis_aktivitas, 0)

    # Simpan aktivitas ibadah
    aktivitas = AktivitasIbadah.objects.create(
        user=request.user,
        jenis_aktivitas=jenis_aktivitas,
        poin=poin
    )

    # Update pertumbuhan pohon amal
    pohon_amal, _ = PohonAmal.objects.get_or_create(user=request.user)
    pohon_amal.update_pertumbuhan()

    serializer = AktivitasIbadahSerializer(aktivitas)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Endpoint untuk melihat pohon amal pengguna
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lihat_pohon_amal(request):
    pohon_amal, _ = PohonAmal.objects.get_or_create(user=request.user)
    serializer = PohonAmalSerializer(pohon_amal)
    return Response(serializer.data)

# Endpoint untuk membandingkan pohon amal dengan teman
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bandingkan_pohon_amal(request, user_id):
    try:
        pohon_amal_teman = PohonAmal.objects.get(user_id=user_id)
        pohon_amal_saya, _ = PohonAmal.objects.get_or_create(user=request.user)

        serializer_teman = PohonAmalSerializer(pohon_amal_teman)
        serializer_saya = PohonAmalSerializer(pohon_amal_saya)

        return Response({
            "pohon_saya": serializer_saya.data,
            "pohon_teman": serializer_teman.data
        })
    except PohonAmal.DoesNotExist:
        return Response({"error": "Pohon amal teman tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
