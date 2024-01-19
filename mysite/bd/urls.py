from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("getDB", views.getDB, name="getDB"),
    #re_path(r'(?P<element_name>\w)', views.getElement, name="getElement"),
    path("addInfo", views.get_additional_info, name="addInfo"),
    path("adder", views.adder, name="adder"),
    path("all_compounds", views.all_compounds, name="compunds_list"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("view_all_users", views.view_all_users, name="view_all_users"),
    path("add_rank", views.add_rank, name='add_rank'),
    path('rate_compound/<int:compound_id>/', views.rate_compound, name='rate_compound'),
    path('submit_rating/<int:compound_id>/', views.submit_rating, name='submit_rating'),
]