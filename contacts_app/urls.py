from django.urls import path
from . import views
urlpatterns = [    
               path('<int:user_id>/', views.get_contacts, name='contacts'),
               path('add_contact/<int:user_id>/', views.add_contact, name='add_contact'),
               path('show_contact/<int:user_id>/<int:contact_id>/', views.show_contact, name='show_contact'),
               path('change_contact/<int:user_id>/<int:contact_id>/', views.change_contact, name='change_contact'),
               path('del_contact/<int:user_id>/<int:contact_id>/', views.del_contact, name='del_contact'),
               path('add_phone/<int:user_id>/<int:contact_id>/', views.add_phone, name='add_phone'),
               path('add_email/<int:user_id>/<int:contact_id>/', views.add_email, name='add_email'),
               path('change_phone/<int:user_id>/<int:contact_id>/<int:phone_id>/', views.change_phone, name='change_phone'),
               path('change_email/<int:user_id>/<int:contact_id>/<int:email_id>/', views.change_email, name='change_email'),               
               path('del_phone/<int:user_id>/<int:contact_id>/<int:phone_id>/', views.del_phone, name='del_phone'),
               path('del_email/<int:user_id>/<int:contact_id>/<int:email_id>/', views.del_email, name='del_email'),
               path('search/<int:user_id>/', views.search, name='search'),

               ]