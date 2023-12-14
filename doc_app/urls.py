from django.urls import path
from . import views


urlpatterns = [
               path('<int:user_id>/', views.docs, name='docs'),

               path('passport/<int:user_id>/', views.get_passport, name='passport'),
               path('change_passport/<int:user_id>/', views.change_passport, name='change_passport'),

               path('edit_spouce/<int:user_id>/', views.edit_spouce, name='edit_spouce'),
               path('del_spouce/<int:user_id>/', views.del_spouce, name='del_spouce'),

               path('edit_children/<int:user_id>/', views.edit_children, name='edit_children'),
               path('add_children/<int:user_id>/', views.add_children, name='add_children'),
               path('show_children/<int:user_id>/', views.show_childrens_for_change, name='show_children'),
               path('change_children/<int:user_id>/<int:children_id>/', views.change_children, name='change_children'),
               path('del_children/<int:user_id>/<int:children_id>/', views.del_children, name='del_children'),

               path('inn/<int:user_id>/', views.get_inn, name='inn'),
               path('change_inn/<int:user_id>/', views.change_inn, name='change_inn'),

               path('snils/<int:user_id>/', views.get_snils, name='snils'),
               path('change_snils/<int:user_id>/', views.change_snils, name='change_snils'),
               
               path('driver_license/<int:user_id>/', views.get_driver_license, name='driver_license'),
               path('change_driver_license/<int:user_id>/', views.change_driver_license, name='change_driver_license'),

               path('edit_driver_categories/<int:user_id>/', views.edit_driver_categories, name='edit_driver_categories'),
               path('add_driver_category/<int:user_id>/', views.add_driver_category, name='add_driver_category'),
               path('change_driver_category/<int:user_id>/<int:category_id>/', views.change_driver_category, name='change_driver_category'),
               path('show_driver_categories/<int:user_id>/', views.show_categories_for_change, name='show_driver_categories'),
               path('del_driver_category/<int:user_id>/<int:category_id>/', views.del_driver_category, name='del_driver_category'),
              
               path('foreign_passport/<int:user_id>/', views.get_foreign_passport, name='foreign_passport'),
               path('change_foreign_passport/<int:user_id>/', views.change_foreign_passport, name='change_foreign_passport'),
               
               path('military_ticket/<int:user_id>/', views.get_military_ticket, name='military_ticket'),
               path('change_military_ticket/<int:user_id>/', views.change_military_ticket, name='change_military_ticket'),
               ]