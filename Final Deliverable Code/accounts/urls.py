from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),

    path('forgotpassword/', views.forgotpassword, name = 'forgotpassword'),
    path('password_reset_validate/<uidb64>/<token>/', views.password_reset_validate, name='password_reset_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

]
