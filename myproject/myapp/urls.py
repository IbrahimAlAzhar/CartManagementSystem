from django.urls import path
from .views import (list_products, upload_csv, view_transactions, add_to_cart, purchase, product_detail, process_purchase, purchase_success, process_to_checkout, purchase_failure)

# , cart_detail, login_view, register, custom_logout)
# confirm_purchase
urlpatterns = [
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('products/', list_products, name='list_products'),
    path('transactions/', view_transactions, name='view_transactions'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('purchase/<int:product_id>/', purchase, name='purchase'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('process_purchase/<int:product_id>/', process_purchase, name='process_purchase'),
    path('process_to_checkout/<int:product_id>/', process_to_checkout, name='process_to_checkout'),
    path('purchase_success/', purchase_success, name='purchase_success'),
    path('purchase_failure/', purchase_failure, name='purchase_failure'),
    # path('confirm_purchase/<uidb64>/<token>/', confirm_purchase, name='confirm_purchase'),
    # path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    # path('cart/', cart_detail, name='cart_detail'),
    # path('login/', login_view, name='login'),
    # path('register/', register, name='register'),
    # path('logout/', custom_logout, name='logout'),
]
