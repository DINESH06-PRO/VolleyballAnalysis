import os
import django
import sys
import io
import random
from datetime import date, timedelta

# Fix encoding for potential production terminal issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volleyball_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Player, Match, PlayerPerformance, Injury, TrainingRecord

def seed_all():
    print("--- Starting Production Seeding ---")

    # 1. Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@volleyball.com', 'admin123')
        print("User created: admin / admin123")

    # 2. Players
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
            defaults={**pd}
        )
        players.append(p)

    # 3. Matches
    matches_data = [
        {'opponent_name': 'Blue Spikes FC',    'match_date': date.today() - timedelta(days=28), 'match_type': 'tournament', 'result': 'win'},
        {'opponent_name': 'Red Titans',         'match_date': date.today() - timedelta(days=21), 'match_type': 'practice',   'result': 'loss'},
        {'opponent_name': 'Golden Eagles',      'match_date': date.today() - timedelta(days=14), 'match_type': 'tournament', 'result': 'win'},
    ]

    matches = []
    for md in matches_data:
        m, created = Match.objects.get_or_create(
            opponent_name=md['opponent_name'],
            match_date=md['match_date'],
            defaults={**md}
        )
        matches.append(m)

    # 4. Performance
    stat_presets = {
        'setter':        dict(attack_attempts=8,  successful_attacks=5,  blocks_attempted=6,  successful_blocks=4, total_serves=25, successful_serves=21, points_scored=8),
        'libero':        dict(attack_attempts=2,  successful_attacks=1,  blocks_attempted=0,  successful_blocks=0, total_serves=20, successful_serves=17, points_scored=3),
        'middle_blocker':dict(attack_attempts=25, successful_attacks=17, blocks_attempted=18, successful_blocks=11, total_serves=22, successful_serves=18, points_scored=20),
        'outside_hitter':dict(attack_attempts=35, successful_attacks=24, blocks_attempted=12, successful_blocks=6, total_serves=24, successful_serves=19, points_scored=27),
        'opposite':      dict(attack_attempts=30, successful_attacks=22, blocks_attempted=14, successful_blocks=8, total_serves=23, successful_serves=18, points_scored=24),
    }

    for match in matches:
        for player in players:
            if not PlayerPerformance.objects.filter(player=player, match=match).exists():
                base = stat_presets[player.position].copy()
                for k in base:
                    base[k] = max(0, base[k] + random.randint(-2, 2))
                PlayerPerformance.objects.create(player=player, match=match, **base)

    # 5. Training
    training_types = ['jump_training', 'spike_training', 'serve_training', 'block_training', 'defense_drills', 'fitness']
    for player in players:
        if player.trainingrecord_set.count() < 3:
            for _ in range(3):
                TrainingRecord.objects.create(
                    player=player,
                    training_type=random.choice(training_types),
                    training_date=date.today() - timedelta(days=random.randint(1, 10)),
                    duration="1 hour",
                    performance_rating="good"
                )

    print("--- Seeding Complete ---")

if __name__ == '__main__':
    seed_all()
