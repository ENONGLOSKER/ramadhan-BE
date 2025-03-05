from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect
from .models import JadwalSalat, AdzanSound, PencapaianPengguna, MisiRamadan, AktivitasIbadah, PohonAmal
import pandas as pd
from django.urls import path
from django.template.response import TemplateResponse

class UploadFileForm(forms.Form):
    file = forms.FileField()

@admin.register(JadwalSalat)
class JadwalSalatAdmin(admin.ModelAdmin):
    list_display = ('id', 'tanggal', 'imsak','subuh', 'dzuhur', 'ashar', 'maghrib', 'isya')
    list_filter = ('tanggal',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload/', self.admin_site.admin_view(self.upload_view), name='upload_jadwal_salat'),
        ]
        return custom_urls + urls

    def upload_view(self, request):
        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    JadwalSalat.objects.create(
                        tanggal=row['tanggal'],
                        imsak=row['imsak'],
                        subuh=row['subuh'],
                        dzuhur=row['dzuhur'],
                        ashar=row['ashar'],
                        maghrib=row['maghrib'],
                        isya=row['isya'],
                    )
                self.message_user(request, "Data berhasil diupload.")
                return HttpResponseRedirect(request.path_info)
        else:
            form = UploadFileForm()
        context = {
            'form': form,
        }
        return TemplateResponse(request, "admin/upload.html", context)

    def get_menu(self, request):
        menu = super().get_menu(request)
        menu.append({
            'name': 'Upload Jadwal Salat',
            'url': '/admin/jadwal_salat/upload/',
            'icon': 'upload',
        })
        return menu

@admin.register(AdzanSound)
class AdzanSoundAdmin(admin.ModelAdmin):
    list_display = ('nama', 'file')
    list_filter = ('nama',)
@admin.register(PencapaianPengguna)
class PencapaianPenggunaAdmin(admin.ModelAdmin):
    list_display = ('user', 'misi', 'selesai_pada')

@admin.register(MisiRamadan)
class MisiRamadanAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'deskripsi', 'selesai')

@admin.register(AktivitasIbadah)
class AktivitasIbadahAdmin(admin.ModelAdmin):
    list_display = ('user', 'jenis_aktivitas', 'poin', 'dibuat_pada')

@admin.register(PohonAmal)
class PohonAmalAdmin(admin.ModelAdmin):
    list_display = ('user', 'daun', 'bunga', 'buah', 'terakhir_diupdate')


