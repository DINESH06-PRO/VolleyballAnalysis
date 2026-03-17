from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Player, Match, PlayerPerformance, Injury, TrainingRecord


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'jersey_number', 'position', 'height', 'age', 'experience', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Player Full Name'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jersey Number'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm (e.g. 185.5)', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['opponent_name', 'match_date', 'match_type', 'result', 'notes']
        widgets = {
            'opponent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opponent Team Name'}),
            'match_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'match_type': forms.Select(attrs={'class': 'form-select'}),
            'result': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes...'}),
        }


class PlayerPerformanceForm(forms.ModelForm):
    class Meta:
        model = PlayerPerformance
        fields = [
            'player', 'attack_attempts', 'successful_attacks',
            'blocks_attempted', 'successful_blocks',
            'total_serves', 'successful_serves', 'service_errors',
            'reception_success', 'digs',
            'attack_errors', 'reception_errors', 'total_errors',
            'points_scored',
        ]
        widgets = {
            'player': forms.Select(attrs={'class': 'form-select'}),
            'attack_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'successful_attacks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'blocks_attempted': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'successful_blocks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_serves': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'successful_serves': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'service_errors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reception_success': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'digs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'attack_errors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reception_errors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_errors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'points_scored': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ['player', 'injury_type', 'injury_date', 'recovery_period', 'current_status', 'notes']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-select'}),
            'injury_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ankle Sprain, Knee Pain'}),
            'injury_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'recovery_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2 weeks, 1 month'}),
            'current_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional medical notes...'}),
        }


class PlayerComparisonForm(forms.Form):
    player1 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Player 1',
    )
    player2 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Player 2',
    )


class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ['player', 'training_type', 'training_date', 'duration', 'performance_rating', 'notes']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-select'}),
            'training_type': forms.Select(attrs={'class': 'form-select'}),
            'training_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1 hour, 45 minutes'}),
            'performance_rating': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Session notes, observations...'}),
        }
