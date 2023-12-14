from django.urls import path
from . import views


urlpatterns = [path('registration/', views.registration, name='registration'),
               path('authorization/', views.authorization, name='authorization'),
               path('logout/',views.logout, name='logout'),
               path('data/<int:user_id>/', views.show_data, name='data'),
               path('change_data/<int:user_id>', views.change_data, name='change_data'),
               path('', views.main, name='main')
               ]