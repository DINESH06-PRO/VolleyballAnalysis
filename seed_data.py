# -*- coding: utf-8 -*-
"""
Demo data seed script for Volleyball Team Analysis System.
Run with: python seed_data.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volleyball_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Player, Match, PlayerPerformance, Injury
from datetime import date, timedelta
import random

print("🏐 Seeding Volleyball Team Analysis System...")

# ── SUPERUSER ──────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@volleyball.com', 'admin123')
    print("✅ Superuser created: admin / admin123")
else:
    print("ℹ️  Superuser 'admin' already exists.")

# ── PLAYERS ────────────────────────────────────────────────
players_data = [
    {'name': 'Marcus Rivera',    'jersey_number': 7,  'position': 'setter',         'height': 188.0, 'age': 24, 'experience': 6},
    {'name': 'Jordan Kim',       'jersey_number': 3,  'position': 'libero',          'height': 175.5, 'age': 22, 'experience': 4},
    {'name': 'Alex Thompson',    'jersey_number': 11, 'position': 'middle_blocker',  'height': 198.0, 'age': 26, 'experience': 8},
    {'name': 'Dante Morales',    'jersey_number': 5,  'position': 'outside_hitter',  'height': 193.0, 'age': 23, 'experience': 5},
    {'name': 'Chris Nakamura',   'jersey_number': 9,  'position': 'opposite',        'height': 196.5, 'age': 25, 'experience': 7},
    {'name': 'Felix Santos',     'jersey_number': 14, 'position': 'middle_blocker',  'height': 200.0, 'age': 28, 'experience': 10},
]

players = []
for pd in players_data:
    p, created = Player.objects.get_or_create(
        jersey_number=pd['jersey_number'],
        defaults={**pd, 'matches_played': 0}
    )
    players.append(p)
    if created:
        print(f"  ✅ Player: {p.name}")

# ── MATCHES ────────────────────────────────────────────────
matches_data = [
    {'opponent_name': 'Blue Spikes FC',    'match_date': date.today() - timedelta(days=28), 'match_type': 'tournament', 'result': 'win'},
    {'opponent_name': 'Red Titans',         'match_date': date.today() - timedelta(days=21), 'match_type': 'practice',   'result': 'loss'},
    {'opponent_name': 'Golden Eagles',      'match_date': date.today() - timedelta(days=14), 'match_type': 'tournament', 'result': 'win'},
    {'opponent_name': 'Storm Breakers',     'match_date': date.today() - timedelta(days=7),  'match_type': 'tournament', 'result': 'win'},
    {'opponent_name': 'Iron Wolves',        'match_date': date.today() - timedelta(days=3),  'match_type': 'practice',   'result': 'loss'},
]

matches = []
for md in matches_data:
    m, created = Match.objects.get_or_create(
        opponent_name=md['opponent_name'],
        match_date=md['match_date'],
        defaults={**md}
    )
    matches.append(m)
    if created:
        print(f"  ✅ Match: vs {m.opponent_name}")

# ── PERFORMANCE STATS ──────────────────────────────────────
stat_presets = {
    'setter':        dict(attack_attempts=8,  successful_attacks=5,  blocks_attempted=6,  successful_blocks=4, total_serves=25, successful_serves=21, service_errors=2, reception_success=30, digs=18, total_errors=3, points_scored=8),
    'libero':        dict(attack_attempts=2,  successful_attacks=1,  blocks_attempted=0,  successful_blocks=0, total_serves=20, successful_serves=17, service_errors=1, reception_success=40, digs=28, total_errors=2, points_scored=3),
    'middle_blocker':dict(attack_attempts=25, successful_attacks=17, blocks_attempted=18, successful_blocks=11, total_serves=22, successful_serves=18, service_errors=2, reception_success=15, digs=8, total_errors=5, points_scored=20),
    'outside_hitter':dict(attack_attempts=35, successful_attacks=24, blocks_attempted=12, successful_blocks=6, total_serves=24, successful_serves=19, service_errors=3, reception_success=22, digs=15, total_errors=6, points_scored=27),
    'opposite':      dict(attack_attempts=30, successful_attacks=22, blocks_attempted=14, successful_blocks=8, total_serves=23, successful_serves=18, service_errors=2, reception_success=12, digs=10, total_errors=4, points_scored=24),
}

for match in matches:
    for player in players:
        if PlayerPerformance.objects.filter(player=player, match=match).exists():
            continue
        base = stat_presets[player.position].copy()
        # Add small random variation
        for k in base:
            base[k] = max(0, base[k] + random.randint(-3, 4))
        pp = PlayerPerformance.objects.create(player=player, match=match, **base)

# Update match counts
for p in players:
    p.matches_played = p.performances.count()
    p.save()

print(f"  ✅ Performance stats generated for {len(players)} players × {len(matches)} matches")

# ── INJURIES ───────────────────────────────────────────────
injuries_data = [
    {'player': players[1], 'injury_type': 'Ankle Sprain (Grade 2)', 'injury_date': date.today() - timedelta(days=10), 'recovery_period': '3 weeks', 'current_status': 'recovering'},
    {'player': players[3], 'injury_type': 'Knee Tendinitis',         'injury_date': date.today() - timedelta(days=25), 'recovery_period': '2 weeks', 'current_status': 'cleared'},
]
for inj_data in injuries_data:
    inj, created = Injury.objects.get_or_create(
        player=inj_data['player'],
        injury_type=inj_data['injury_type'],
        defaults=inj_data
    )
    if created:
        print(f"  ✅ Injury: {inj.player.name} — {inj.injury_type}")

print("\n🎉 Demo data seeded successfully!")
print("─" * 45)
print("  URL:      http://127.0.0.1:8000/")
print("  Username: admin")
print("  Password: admin123")
print("─" * 45)
