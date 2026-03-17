from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Players
    path('players/', views.player_list, name='player_list'),
    path('players/add/', views.player_create, name='player_create'),
    path('players/<int:pk>/', views.player_profile, name='player_profile'),
    path('players/<int:pk>/edit/', views.player_edit, name='player_edit'),
    path('players/<int:pk>/delete/', views.player_delete, name='player_delete'),

    # Matches
    path('matches/', views.match_list, name='match_list'),
    path('matches/add/', views.match_create, name='match_create'),
    path('matches/<int:pk>/', views.match_detail, name='match_detail'),
    path('matches/<int:pk>/delete/', views.match_delete, name='match_delete'),

    # Performance
    path('matches/<int:match_pk>/performance/add/', views.performance_add, name='performance_add'),
    path('performance/<int:pk>/edit/', views.performance_edit, name='performance_edit'),
    path('performance/<int:pk>/delete/', views.performance_delete, name='performance_delete'),

    # Analysis
    path('analysis/', views.performance_analysis, name='performance_analysis'),

    # Comparison
    path('comparison/', views.player_comparison, name='player_comparison'),

    # Injuries
    path('injuries/', views.injury_list, name='injury_list'),
    path('injuries/add/', views.injury_add, name='injury_add'),
    path('injuries/<int:pk>/edit/', views.injury_edit, name='injury_edit'),
    path('injuries/<int:pk>/delete/', views.injury_delete, name='injury_delete'),

    # Training Planner (auto-generated)
    path('training/', views.training_planner, name='training_planner'),

    # Training Records (manual input)
    path('training/records/', views.training_record_list, name='training_record_list'),
    path('training/records/add/', views.training_record_add, name='training_record_add'),
    path('training/records/<int:pk>/edit/', views.training_record_edit, name='training_record_edit'),
    path('training/records/<int:pk>/delete/', views.training_record_delete, name='training_record_delete'),
]
