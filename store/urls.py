from django.urls import path
from . import views

urlpatterns = [
     path('', views.home, name='home'),
    path('category/<int:id>/', views.category_filter, name='category'),
    path('search/', views.search, name='search'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('signup/', views.signup_user, name='signup_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path("products/", views.product_list, name="product_list"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("create_order/", views.create_order, name="create_order"),
    path('payment_success/', views.payment_success, name='payment_success'),
    path("clear-cart/", views.clear_cart, name="clear_cart"),

   
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


