from django.contrib import admin
from .models import Player, Match, PlayerPerformance, Injury, TrainingRecord


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['jersey_number', 'name', 'position', 'age', 'experience', 'matches_played']
    list_filter = ['position']
    search_fields = ['name', 'jersey_number']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['opponent_name', 'match_date', 'match_type', 'result']
    list_filter = ['match_type', 'result']
    date_hierarchy = 'match_date'


@admin.register(PlayerPerformance)
class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'points_scored', 'attack_attempts', 'successful_attacks']
    list_filter = ['match']
    search_fields = ['player__name']


@admin.register(Injury)
class InjuryAdmin(admin.ModelAdmin):
    list_display = ['player', 'injury_type', 'injury_date', 'current_status']
    list_filter = ['current_status']
    search_fields = ['player__name', 'injury_type']


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ['player', 'training_type', 'training_date', 'duration', 'performance_rating']
    list_filter = ['training_type', 'performance_rating']
    search_fields = ['player__name']
    date_hierarchy = 'training_date'
