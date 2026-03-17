import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volleyball_system.settings')
django.setup()

from core.models import Player, TrainingRecord, PlayerPerformance

def seed_training_data():
    players = Player.objects.all()
    if not players:
        print("No players found. Please run the main seeder first.")
        return

    training_types = [
        'jump_training', 'spike_training', 'serve_training', 
        'block_training', 'defense_drills', 'fitness'
    ]
    ratings = ['excellent', 'good', 'average']
    durations = ['45 minutes', '1 hour', '1 hour 15 minutes', '30 minutes']

    print(f"Seeding training records for {players.count()} players...")

    for player in players:
        # Add 3-5 training records per player
        for i in range(random.randint(3, 5)):
            days_ago = random.randint(1, 14)
            TrainingRecord.objects.create(
                player=player,
                training_type=random.choice(training_types),
                training_date=date.today() - timedelta(days=days_ago),
                duration=random.choice(durations),
                performance_rating=random.choice(ratings),
                notes=f"Focused session on {player.get_position_display()} specifics."
            )
    
    print("Updating existing performance records with separate error counts...")
    for perf in PlayerPerformance.objects.all():
        # Randomly split total_errors into attack and reception errors
        tot = perf.total_errors
        atk_err = random.randint(0, tot)
        rec_err = tot - atk_err
        perf.attack_errors = atk_err
        perf.reception_errors = rec_err
        perf.save()

    print("Seeding complete!")

if __name__ == '__main__':
    seed_training_data()
