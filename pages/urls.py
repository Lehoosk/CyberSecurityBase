from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_exercise", views.new_exercise, name="new_exercise"),
    path("exercises", views.exercises, name="exercises"),
    path("edit/<int:exercise_id>", views.edit_exercise, name="edit_exercise"),
    path("remove/<int:exercise_id>", views.remove_exercise, name="remove_exercise"),
    path("edit_exercise_types", views.exercise_types, name="exercise_types"),
    path("search", views.search, name="search"),
    path("comments/<int:exercise_id>", views.comments, name="comments"),
    path("stats", views.stats, name="stats"),
    path("user_page", views.user_page, name="user_page_self"),
    path("user_page/<int:user_id>", views.user_page, name="user_page"),
]
