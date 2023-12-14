from django.urls import path
from . import views
urlpatterns = [
               path('<int:user_id>/', views.get_properties, name='properties'),
               path('list_realty/<int:user_id>/', views.show_list_realty, name='realty'),
               path('list_transport/<int:user_id>/', views.show_list_transport, name='transport'),
               path('add_realty/<int:user_id>/', views.add_realty, name='add_realty'),
               path('add_transport/<int:user_id>/', views.add_transport, name='add_transport'),
               path('get_realty/<int:user_id>/<int:property_id>/', views.get_realty, name='get_realty'),
               path('get_transport/<int:user_id>/<int:property_id>/', views.get_transport, name='get_transport'),
               path('change_realty/<int:user_id>/<int:property_id>/', views.change_realty, name='change_realty'),
               path('change_transport/<int:user_id>/<int:property_id>/', views.change_transport, name='change_transport'),               
               path('del_realty/<int:user_id>/<int:property_id>/', views.del_realty, name='del_realty'),
               path('del_transport/<int:user_id>/<int:property_id>/', views.del_transport, name='del_transport'),
               ]