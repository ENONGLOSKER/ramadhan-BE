from rest_framework import serializers
from .models import JadwalSalat, AdzanSound, MisiRamadan, PencapaianPengguna, AktivitasIbadah, PohonAmal

class JadwalSalatSerializer(serializers.ModelSerializer):
    class Meta:
        model = JadwalSalat
        fields = "__all__"
        extra_kwargs = {
            'imsak': {'format': '%H:%M'},
            'subuh': {'format': '%H:%M'},
            'dzuhur': {'format': '%H:%M'},
            'ashar': {'format': '%H:%M'},
            'maghrib': {'format': '%H:%M'},
            'isya': {'format': '%H:%M'},
        }

class AdzanSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdzanSound
        fields = "__all__"

class MisiRamadanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MisiRamadan
        fields = '__all__'

class PencapaianPenggunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PencapaianPengguna
        fields = '__all__'

class AktivitasIbadahSerializer(serializers.ModelSerializer):
    class Meta:
        model = AktivitasIbadah
        fields = '__all__'

class PohonAmalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PohonAmal
        fields = '__all__'