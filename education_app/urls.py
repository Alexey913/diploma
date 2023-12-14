from django.urls import path
from . import views
urlpatterns = [
               path('<int:user_id>/', views.education, name='education'),
               path('get_diploma/<int:user_id>/<int:diploma_id>/', views.get_diploma, name='get_diploma'),
               path('add_diploma/<int:user_id>/', views.add_diploma, name='add_diploma'),
               path('show_diplomas/<int:user_id>/', views.show_diplomas_for_change, name='show_diplomas'),
               path('change_diploma/<int:user_id>/<int:diploma_id>/', views.change_diploma, name='change_diploma'),
               path('del_diploma/<int:user_id>/<int:diploma_id>/', views.del_diploma, name='del_diploma'),

               ]