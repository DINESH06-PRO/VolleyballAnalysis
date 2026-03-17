from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum, Count
from .models import Player, Match, PlayerPerformance, Injury, TrainingRecord
from .forms import (LoginForm, PlayerForm, MatchForm,
                    PlayerPerformanceForm, InjuryForm, PlayerComparisonForm,
                    TrainingRecordForm)
import json


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    players = Player.objects.all()
    matches = Match.objects.all()
    performances = PlayerPerformance.objects.all()
    injuries = Injury.objects.filter(current_status='active')

    total_wins = matches.filter(result='win').count()
    total_losses = matches.filter(result='loss').count()

    # Chart data: attack success by player (top 8)
    player_chart_data = []
    for p in players[:8]:
        perfs = p.performances.all()
        if perfs:
            avg_attack = sum(x.attack_success_rate for x in perfs) / len(perfs)
            avg_serve = sum(x.serve_accuracy for x in perfs) / len(perfs)
            avg_block = sum(x.block_efficiency for x in perfs) / len(perfs)
            avg_score = p.get_avg_performance_score()
            player_chart_data.append({
                'name': p.name,
                'attack': round(avg_attack, 1),
                'serve': round(avg_serve, 1),
                'block': round(avg_block, 1),
                'score': avg_score,
            })

    # Match trend (last 10 matches)
    recent_matches = matches[:10]
    trend_labels = [str(m.match_date) for m in reversed(list(recent_matches))]
    trend_wins = []
    running_win = 0
    for m in reversed(list(recent_matches)):
        if m.result == 'win':
            running_win += 1
        trend_wins.append(running_win)

    # Top performers
    top_players = sorted(players, key=lambda p: p.get_avg_performance_score(), reverse=True)[:5]

    context = {
        'total_players': players.count(),
        'total_matches': matches.count(),
        'total_wins': total_wins,
        'total_losses': total_losses,
        'active_injuries': injuries.count(),
        'win_rate': round((total_wins / max(matches.count(), 1)) * 100, 1),
        'player_chart_data': json.dumps(player_chart_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_wins': json.dumps(trend_wins),
        'top_players': top_players,
        'recent_matches': matches[:5],
        'active_injury_list': injuries[:5],
    }
    return render(request, 'dashboard.html', context)


# ─── PLAYERS ──────────────────────────────────────────────────────────────────

@login_required
def player_list(request):
    players = Player.objects.all()
    return render(request, 'players/list.html', {'players': players})


@login_required
def player_create(request):
    form = PlayerForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Player added successfully!')
        return redirect('player_list')
    return render(request, 'players/form.html', {'form': form, 'title': 'Add Player'})


@login_required
def player_edit(request, pk):
    player = get_object_or_404(Player, pk=pk)
    form = PlayerForm(request.POST or None, request.FILES or None, instance=player)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Player updated successfully!')
        return redirect('player_profile', pk=player.pk)
    return render(request, 'players/form.html', {'form': form, 'title': 'Edit Player', 'player': player})


@login_required
def player_delete(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == 'POST':
        player.delete()
        messages.success(request, 'Player deleted.')
        return redirect('player_list')
    return render(request, 'players/confirm_delete.html', {'player': player})


@login_required
def player_profile(request, pk):
    player = get_object_or_404(Player, pk=pk)
    performances = player.performances.select_related('match').all()
    injuries = player.injuries.all()
    strengths, weaknesses = player.get_strengths_weaknesses()
    recommendations = player.get_training_recommendations()
    avg_score = player.get_avg_performance_score()

    # Chart data for radar
    if performances:
        n = len(performances)
        radar_data = {
            'attack': round(sum(p.attack_success_rate for p in performances) / n, 1),
            'serve': round(sum(p.serve_accuracy for p in performances) / n, 1),
            'block': round(sum(p.block_efficiency for p in performances) / n, 1),
            'points': round(sum(p.points_scored for p in performances) / n, 1),
            'digs': round(sum(p.digs for p in performances) / n, 1),
        }
    else:
        radar_data = {'attack': 0, 'serve': 0, 'block': 0, 'points': 0, 'digs': 0}

    context = {
        'player': player,
        'performances': performances,
        'injuries': injuries,
        'training_records': player.training_records.all()[:10],
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'avg_score': avg_score,
        'total_attack_errors': sum(p.attack_errors for p in performances),
        'total_reception_errors': sum(p.reception_errors for p in performances),
        'total_career_errors': sum(p.total_errors for p in performances),
        'radar_data': json.dumps(radar_data),
    }
    return render(request, 'players/profile.html', context)


# ─── MATCHES ──────────────────────────────────────────────────────────────────

@login_required
def match_list(request):
    matches = Match.objects.all()
    return render(request, 'matches/list.html', {'matches': matches})


@login_required
def match_create(request):
    form = MatchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        match = form.save()
        messages.success(request, 'Match recorded successfully!')
        return redirect('match_detail', pk=match.pk)
    return render(request, 'matches/form.html', {'form': form, 'title': 'Record New Match'})


@login_required
def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Match deleted.')
        return redirect('match_list')
    return render(request, 'matches/confirm_delete.html', {'match': match})


@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    performances = match.performances.select_related('player').all()
    return render(request, 'matches/detail.html', {'match': match, 'performances': performances})


# ─── PERFORMANCE ──────────────────────────────────────────────────────────────

@login_required
def performance_add(request, match_pk):
    match = get_object_or_404(Match, pk=match_pk)
    # Exclude players already entered for this match
    existing_player_ids = match.performances.values_list('player_id', flat=True)
    form = PlayerPerformanceForm(request.POST or None)
    form.fields['player'].queryset = Player.objects.exclude(id__in=existing_player_ids)

    if request.method == 'POST' and form.is_valid():
        perf = form.save(commit=False)
        perf.match = match
        perf.save()
        messages.success(request, f'Stats for {perf.player.name} saved!')
        return redirect('match_detail', pk=match.pk)
    return render(request, 'performance/form.html', {'form': form, 'match': match})


@login_required
def performance_edit(request, pk):
    perf = get_object_or_404(PlayerPerformance, pk=pk)
    form = PlayerPerformanceForm(request.POST or None, instance=perf)
    form.fields['player'].queryset = Player.objects.all()
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Performance stats updated!')
        return redirect('match_detail', pk=perf.match.pk)
    return render(request, 'performance/form.html', {'form': form, 'match': perf.match, 'edit': True})


@login_required
def performance_delete(request, pk):
    perf = get_object_or_404(PlayerPerformance, pk=pk)
    match_pk = perf.match.pk
    if request.method == 'POST':
        perf.delete()
        messages.success(request, 'Performance entry deleted.')
    return redirect('match_detail', pk=match_pk)


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

@login_required
def performance_analysis(request):
    players = Player.objects.all()
    analysis_data = []
    for p in players:
        perfs = p.performances.all()
        if perfs:
            n = len(perfs)
            strengths, weaknesses = p.get_strengths_weaknesses()
            analysis_data.append({
                'player': p,
                'avg_attack': round(sum(x.attack_success_rate for x in perfs) / n, 1),
                'avg_serve': round(sum(x.serve_accuracy for x in perfs) / n, 1),
                'avg_block': round(sum(x.block_efficiency for x in perfs) / n, 1),
                'avg_score': p.get_avg_performance_score(),
                'total_points': sum(x.points_scored for x in perfs),
                'total_errors': sum(x.total_errors for x in perfs),
                'attack_errors': sum(x.attack_errors for x in perfs),
                'reception_errors': sum(x.reception_errors for x in perfs),
                'strengths': strengths,
                'weaknesses': weaknesses,
            })

    # Sort by avg_score
    analysis_data.sort(key=lambda x: x['avg_score'], reverse=True)

    # Chart data for team overview
    chart_players = [d['player'].name for d in analysis_data]
    chart_attack = [d['avg_attack'] for d in analysis_data]
    chart_serve = [d['avg_serve'] for d in analysis_data]
    chart_block = [d['avg_block'] for d in analysis_data]
    chart_scores = [d['avg_score'] for d in analysis_data]
    chart_errors = [d['total_errors'] for d in analysis_data]

    context = {
        'analysis_data': analysis_data,
        'chart_players': json.dumps(chart_players),
        'chart_attack': json.dumps(chart_attack),
        'chart_serve': json.dumps(chart_serve),
        'chart_block': json.dumps(chart_block),
        'chart_scores': json.dumps(chart_scores),
        'chart_errors': json.dumps(chart_errors),
    }
    return render(request, 'analysis/performance.html', context)


# ─── PLAYER COMPARISON ────────────────────────────────────────────────────────

@login_required
def player_comparison(request):
    form = PlayerComparisonForm(request.GET or None)
    player1 = player2 = None
    p1_data = p2_data = None

    if form.is_valid():
        player1 = form.cleaned_data['player1']
        player2 = form.cleaned_data['player2']

        def get_stats(player):
            perfs = player.performances.all()
            if not perfs:
                return {'attack': 0, 'serve': 0, 'block': 0, 'score': 0, 'errors': 0, 'points': 0}
            n = len(perfs)
            return {
                'attack': round(sum(p.attack_success_rate for p in perfs) / n, 1),
                'serve': round(sum(p.serve_accuracy for p in perfs) / n, 1),
                'block': round(sum(p.block_efficiency for p in perfs) / n, 1),
                'score': player.get_avg_performance_score(),
                'errors': sum(p.total_errors for p in perfs),
                'points': sum(p.points_scored for p in perfs),
            }

        p1_data = get_stats(player1)
        p2_data = get_stats(player2)

    comparison_rows = []
    if p1_data and p2_data:
        comparison_rows = [
            ('Attack Success Rate', p1_data['attack'], p2_data['attack'], '%'),
            ('Serve Accuracy', p1_data['serve'], p2_data['serve'], '%'),
            ('Block Efficiency', p1_data['block'], p2_data['block'], '%'),
            ('Performance Score', p1_data['score'], p2_data['score'], ''),
            ('Total Points', p1_data['points'], p2_data['points'], ''),
            ('Total Errors', p1_data['errors'], p2_data['errors'], ''),
        ]

    context = {
        'form': form,
        'player1': player1,
        'player2': player2,
        'p1_data': json.dumps(p1_data) if p1_data else None,
        'p2_data': json.dumps(p2_data) if p2_data else None,
        'p1_raw': p1_data,
        'p2_raw': p2_data,
        'comparison_rows': comparison_rows,
    }
    return render(request, 'comparison/compare.html', context)


# ─── INJURIES ─────────────────────────────────────────────────────────────────

@login_required
def injury_list(request):
    injuries = Injury.objects.select_related('player').all()
    return render(request, 'injuries/list.html', {'injuries': injuries})


@login_required
def injury_add(request):
    form = InjuryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Injury recorded.')
        return redirect('injury_list')
    return render(request, 'injuries/form.html', {'form': form, 'title': 'Record Injury'})


@login_required
def injury_edit(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    form = InjuryForm(request.POST or None, instance=injury)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Injury updated.')
        return redirect('injury_list')
    return render(request, 'injuries/form.html', {'form': form, 'title': 'Edit Injury', 'injury': injury})


@login_required
def injury_delete(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    if request.method == 'POST':
        injury.delete()
        messages.success(request, 'Injury record deleted.')
        return redirect('injury_list')
    return render(request, 'injuries/confirm_delete.html', {'injury': injury})


# ─── TRAINING PLANNER ─────────────────────────────────────────────────────────

@login_required
def training_planner(request):
    players = Player.objects.all()
    team_plan = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_idx = 0

    for p in players:
        recs = p.get_training_recommendations()
        for rec in recs:
            team_plan.append({
                'player': p,
                'day': days[day_idx % len(days)],
                **rec,
            })
            day_idx += 1

    # Group by day
    schedule = {}
    for item in team_plan:
        day = item['day']
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(item)

    context = {
        'schedule': schedule,
        'players': players,
        'days': days,
    }
    return render(request, 'training/planner.html', context)


# ─── TRAINING RECORDS ─────────────────────────────────────────────────────────

@login_required
def training_record_list(request):
    player_filter = request.GET.get('player')
    records = TrainingRecord.objects.select_related('player').all()
    if player_filter:
        records = records.filter(player_id=player_filter)
    players = Player.objects.all()
    return render(request, 'training/records.html', {
        'records': records,
        'players': players,
        'selected_player': player_filter,
    })


@login_required
def training_record_add(request):
    player_pk = request.GET.get('player')
    initial = {}
    if player_pk:
        from datetime import date
        initial = {'player': player_pk, 'training_date': date.today()}
    form = TrainingRecordForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Training session recorded!')
        return redirect('training_record_list')
    return render(request, 'training/record_form.html', {'form': form, 'title': 'Log Training Session'})


@login_required
def training_record_edit(request, pk):
    record = get_object_or_404(TrainingRecord, pk=pk)
    form = TrainingRecordForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Training record updated!')
        return redirect('training_record_list')
    return render(request, 'training/record_form.html', {'form': form, 'title': 'Edit Training Record', 'record': record})


@login_required
def training_record_delete(request, pk):
    record = get_object_or_404(TrainingRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Training record deleted.')
    return redirect('training_record_list')
