from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


POSITION_CHOICES = [
    ('setter', 'Setter'),
    ('libero', 'Libero'),
    ('middle_blocker', 'Middle Blocker'),
    ('outside_hitter', 'Outside Hitter'),
    ('opposite', 'Opposite'),
]

MATCH_TYPE_CHOICES = [
    ('practice', 'Practice'),
    ('tournament', 'Tournament'),
]

RESULT_CHOICES = [
    ('win', 'Win'),
    ('loss', 'Loss'),
]

INJURY_STATUS_CHOICES = [
    ('active', 'Active (Injured)'),
    ('recovering', 'Recovering'),
    ('cleared', 'Cleared to Play'),
]

TRAINING_TYPE_CHOICES = [
    ('jump_training', 'Jump Training'),
    ('spike_training', 'Spike / Attack Training'),
    ('serve_training', 'Serve Training'),
    ('block_training', 'Block Training'),
    ('defense_drills', 'Defense & Reception Drills'),
    ('fitness', 'Fitness & Conditioning'),
    ('team_tactics', 'Team Tactics & Strategy'),
    ('scrimmage', 'Scrimmage / Practice Match'),
    ('other', 'Other'),
]

RATING_CHOICES = [
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('average', 'Average'),
    ('poor', 'Poor'),
    ('needs_improvement', 'Needs Improvement'),
]


class Player(models.Model):
    name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField(unique=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text='Height in cm')
    age = models.PositiveIntegerField()
    experience = models.PositiveIntegerField(help_text='Years of experience')
    photo = models.ImageField(upload_to='players/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def matches_played(self):
        return self.performances.count()

    class Meta:
        ordering = ['jersey_number']

    def __str__(self):
        return f"#{self.jersey_number} {self.name} ({self.get_position_display()})"

    def get_avg_performance_score(self):
        perfs = self.performances.all()
        if not perfs:
            return 0
        scores = [p.performance_score for p in perfs]
        return round(sum(scores) / len(scores), 1)

    def get_strengths_weaknesses(self):
        perfs = self.performances.all()
        if not perfs:
            return [], []
        
        total = len(perfs)
        avg_attack = sum(p.attack_success_rate for p in perfs) / total
        avg_serve = sum(p.serve_accuracy for p in perfs) / total
        avg_block = sum(p.block_efficiency for p in perfs) / total
        avg_errors = sum(
            (p.total_errors / max(p.attack_attempts + p.total_serves, 1)) * 100
            for p in perfs
        ) / total

        strengths = []
        weaknesses = []

        if avg_attack >= 70:
            strengths.append({'label': 'Strong Attacker', 'value': f'{avg_attack:.1f}%'})
        elif avg_attack < 40:
            weaknesses.append({'label': 'Weak Attack', 'detail': 'Spike technique needs improvement', 'value': f'{avg_attack:.1f}%'})

        if avg_serve >= 75:
            strengths.append({'label': 'Accurate Server', 'value': f'{avg_serve:.1f}%'})
        elif avg_serve < 50:
            weaknesses.append({'label': 'Poor Serving', 'detail': 'Serve consistency needs work', 'value': f'{avg_serve:.1f}%'})

        if avg_block >= 60:
            strengths.append({'label': 'Effective Blocker', 'value': f'{avg_block:.1f}%'})
        elif avg_block < 40:
            weaknesses.append({'label': 'Weak Blocking', 'detail': 'Jump and block technique needed', 'value': f'{avg_block:.1f}%'})

        if avg_errors > 20:
            weaknesses.append({'label': 'High Error Rate', 'detail': 'Ball control and consistency', 'value': f'{avg_errors:.1f}%'})
        elif avg_errors <= 10:
            strengths.append({'label': 'Low Error Rate', 'value': f'{avg_errors:.1f}%'})

        return strengths, weaknesses

    def get_training_recommendations(self):
        _, weaknesses = self.get_strengths_weaknesses()
        recommendations = []
        labels = [w['label'] for w in weaknesses]

        if 'Weak Attack' in labels:
            recommendations.append({
                'drill': 'Spike Technique & Arm Swing Training',
                'duration': '45 min',
                'frequency': '4x per week',
                'icon': 'bi-lightning-charge',
            })
        if 'Poor Serving' in labels:
            recommendations.append({
                'drill': 'Serve Training Drills (Target Practice)',
                'duration': '30 min',
                'frequency': 'Daily',
                'icon': 'bi-record-circle',
            })
        if 'Weak Blocking' in labels:
            recommendations.append({
                'drill': 'Jump & Block Training (Plyometric Drills)',
                'duration': '40 min',
                'frequency': '3x per week',
                'icon': 'bi-shield-fill',
            })
        if 'High Error Rate' in labels:
            recommendations.append({
                'drill': 'Ball Control & Consistency Drills',
                'duration': '30 min',
                'frequency': '5x per week',
                'icon': 'bi-bullseye',
            })
        if not recommendations:
            recommendations.append({
                'drill': 'Maintain Current Training Regimen',
                'duration': '60 min',
                'frequency': '5x per week',
                'icon': 'bi-trophy',
            })
        return recommendations


class Match(models.Model):
    opponent_name = models.CharField(max_length=100)
    match_date = models.DateField()
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_date']

    def __str__(self):
        return f"vs {self.opponent_name} ({self.match_date}) - {self.get_result_display()}"


class PlayerPerformance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='performances')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='performances')

    # Raw stats
    attack_attempts = models.PositiveIntegerField(default=0)
    successful_attacks = models.PositiveIntegerField(default=0)
    blocks_attempted = models.PositiveIntegerField(default=0)
    successful_blocks = models.PositiveIntegerField(default=0)
    total_serves = models.PositiveIntegerField(default=0)
    successful_serves = models.PositiveIntegerField(default=0)
    service_errors = models.PositiveIntegerField(default=0)
    reception_success = models.PositiveIntegerField(default=0)
    digs = models.PositiveIntegerField(default=0)
    attack_errors = models.PositiveIntegerField(default=0)
    reception_errors = models.PositiveIntegerField(default=0)
    total_errors = models.PositiveIntegerField(default=0)
    points_scored = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('player', 'match')
        ordering = ['-match__match_date']

    def __str__(self):
        return f"{self.player.name} - {self.match}"

    @property
    def attack_success_rate(self):
        if self.attack_attempts == 0:
            return 0
        return round((self.successful_attacks / self.attack_attempts) * 100, 1)

    @property
    def serve_accuracy(self):
        if self.total_serves == 0:
            return 0
        return round((self.successful_serves / self.total_serves) * 100, 1)

    @property
    def block_efficiency(self):
        if self.blocks_attempted == 0:
            return 0
        return round((self.successful_blocks / self.blocks_attempted) * 100, 1)

    @property
    def performance_score(self):
        score = (self.attack_success_rate * 0.4) + \
                (self.serve_accuracy * 0.3) + \
                (self.block_efficiency * 0.3)
        return round(score, 1)


class Injury(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='injuries')
    injury_type = models.CharField(max_length=100)
    injury_date = models.DateField()
    recovery_period = models.CharField(max_length=100, help_text='e.g. 2 weeks, 1 month')
    current_status = models.CharField(max_length=20, choices=INJURY_STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-injury_date']

    def __str__(self):
        return f"{self.player.name} - {self.injury_type} ({self.injury_date})"


class TrainingRecord(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='training_records')
    training_type = models.CharField(max_length=30, choices=TRAINING_TYPE_CHOICES)
    training_date = models.DateField()
    duration = models.CharField(max_length=60, help_text='e.g. 1 hour, 45 minutes')
    performance_rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='good')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-training_date']

    def __str__(self):
        return f"{self.player.name} - {self.get_training_type_display()} ({self.training_date})"

    def rating_color(self):
        return {
            'excellent': 'success',
            'good': 'info',
            'average': 'warning',
            'poor': 'danger',
            'needs_improvement': 'danger',
        }.get(self.performance_rating, 'secondary')
