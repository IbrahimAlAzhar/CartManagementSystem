from django.http import HttpResponse
import csv
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product, CustomerInformation, Transaction
from django.contrib.auth.decorators import login_required


def upload_csv(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('File is not CSV type')
        # Set up CSV reader and process rows
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            Product.objects.create(
                number=row['number'],
                description=row['description'],
                price=row['price'],
                weight=row['weight'],
                pictureURL=row['pictureURL']
            )
        return HttpResponse('Successfully uploaded and processed')
    else:
        return render(request, 'upload_csv.html')


def list_products(request):
    products = Product.objects.all()  # Retrieves all products from the database
    return render(request, 'list_products.html', {'products': products})

def view_transactions(request):
    transactions = Transaction.objects.all()  # Fetch all transactions from the database
    return render(request, 'transactions.html', {'transactions': transactions})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Here you'd typically add the product to the user's cart session or database
    return render(request, 'add_to_cart.html', {'product': product})

def purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Here you'd handle the purchase logic, like decrementing stock, processing payment, etc.
    return render(request, 'purchase.html', {'product': product})

# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     return render(request, 'product_detail.html', {'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    handling_fee = 5.00  # Fixed handling charge
    per_unit_weight_shipping_cost = 10.00  # Per unit weight shipping cost

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        shipping_charge = quantity * product.weight * per_unit_weight_shipping_cost
        handling_charge = handling_fee  # As it's fixed per transaction
        total_cost = (product.price * quantity) + shipping_charge + handling_charge

        context = {
            'product': product,
            'quantity': quantity,
            'shipping_charge': shipping_charge,
            'handling_charge': handling_charge,
            'total_cost': total_cost,
        }
        return render(request, 'product_detail.html', context)

    context = {'product': product}
    return render(request, 'product_detail.html', context)


# def process_purchase(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == 'POST':
#         quantity = int(request.POST.get('quantity'))
#         base_price = product.price * quantity
#         shipping_charge = quantity * product.weight * 10  # $10 per unit weight
#         handling_charge = 5  # Fixed handling fee
#         total_price = base_price + shipping_charge + handling_charge
#
#         if product.quantity_on_hand >= quantity:
#             credit_card_info = request.POST.get('creditCard')
#             if Transaction.objects.filter(cc=credit_card_info).exists():
#                 product.quantity_on_hand -= quantity
#                 product.save()
#
#                 CustomerInformation.objects.create(
#                     name=request.POST.get('name'),
#                     email=request.POST.get('email'),
#                     mailing_address=request.POST.get('address'),
#                     credit_card_info=credit_card_info,
#                     quantity=quantity,
#                     shipping_charge=shipping_charge,
#                     handling_charge=handling_charge,
#                     product_description=product.description,
#                     total_price=total_price
#                 )
#
#                 messages.success(request, 'Purchase completed successfully.')
#                 return HttpResponseRedirect(reverse('purchase_success'))
#
#             else:
#                 messages.error(request, 'Credit card authorization failed: Card does not match any records.')
#                 return redirect('purchase_failure')
#
#         else:
#             messages.error(request, 'Insufficient stock available.')
#             return redirect('purchase_failure')
#
#     else:
#         messages.error(request, 'Invalid request method.')
#         return redirect('purchase_failure')

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime


def process_purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            base_price = product.price * quantity
            shipping_charge = quantity * product.weight * 10  # $10 per unit weight
            handling_charge = 5  # Fixed handling fee
            total_cost = base_price + shipping_charge + handling_charge

            # Check if the requested quantity is available
            if product.quantity_on_hand >= quantity:
                credit_card_info = request.POST.get('creditCard')
                exp_date_str = request.POST.get(
                    'credit_card_expiration_date')  # Assuming field is named this in the form

                # Check if the provided credit card info matches any in Transaction model
                if Transaction.objects.filter(cc=credit_card_info, exp=exp_date_str).exists():
                    # Perform the purchase
                    product.quantity_on_hand -= quantity
                    product.save()

                    CustomerInformation.objects.create(
                        name=request.POST.get('name'),
                        email=request.POST.get('email'),
                        mailing_address=request.POST.get('address'),
                        credit_card_info=credit_card_info,
                        quantity=quantity
                    )

                    # Send confirmation email
                    send_mail(
                        'Order Confirmation',
                        f'Thank you for your purchase of {product.description}. Please confirm your order by clicking on this link.',
                        'from@example.com',
                        [request.POST.get('email')],
                        fail_silently=False,
                    )

                    # Redirect with success message
                    messages.success(request,
                                     'Purchase completed successfully. Please check your email to confirm the order.')
                    return HttpResponseRedirect(reverse(
                        'purchase_success') + f'?total_cost={total_cost}&base_price={base_price}&shipping_charge={shipping_charge}&handling_charge={handling_charge}')

                else:
                    # Credit card doesn't match
                    messages.error(request,
                                   'Credit card authorization failed: Card does not match any records or expiration date is incorrect.')
                    return redirect('purchase_failure')

            else:
                # Insufficient stock
                messages.error(request, 'Insufficient stock available.')
                return redirect('purchase_failure')

        except ValueError:
            # Handle invalid quantity input
            messages.error(request, 'Invalid quantity provided.')
            return redirect('purchase_failure')

    else:
        # Invalid request method
        messages.error(request, 'Invalid request method.')
        return redirect('purchase_failure')

# views.py
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import Product, CustomerInformation

# def add_to_cart(request, product_id):
#     # Ensure the user is logged in
#     if not request.user.is_authenticated:
#         messages.error(request, "You need to log in first to add items to the cart.")
#         return redirect('login')
#
#     # Fetch the product using the provided product ID
#     product = get_object_or_404(Product, id=product_id)
#
#     # Check if the item is already in the cart for this user
#     cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
#     if not created:
#         # If the item is already in the cart, increment the quantity
#         cart_item.quantity += 1
#         cart_item.save()
#         messages.info(request, f"{product.description} quantity updated in the cart.")
#     else:
#         # If the item is not in the cart, save it
#         messages.success(request, f"{product.description} was added to the cart.")
#
#     return redirect('cart_detail')

# @login_required(login_url='login')  # Redirect to login page if not authenticated
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#
#     # Check if the item is already in the cart for this user
#     cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
#     if not created:
#         # If the item is already in the cart, increment the quantity
#         cart_item.quantity += 1
#     else:
#         # New item added to the cart
#         cart_item.quantity = 1
#     cart_item.save()
#     messages.success(request, f"{product.description} was added to the cart.")
#     return redirect('cart_detail')
#
# def cart_detail(request):
#     # Ensure the user is logged in
#     if not request.user.is_authenticated:
#         messages.error(request, "You need to log in to view the cart.")
#         return redirect('login')
#
#     # Fetch cart items for the logged-in user
#     cart_items = CartItem.objects.filter(user=request.user)
#     total_price = sum(item.total_price for item in cart_items)
#
#     return render(request, 'cart_detail.html', {
#         'cart_items': cart_items,
#         'total_price': total_price,
#     })
#
#
#
# from django.contrib.auth import authenticate, login, logout
#
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, f"Welcome, {user.username}!")
#             return redirect('part-detail')
#         else:
#             messages.error(request, "Invalid username or password.")
#             return redirect('register')
#     return render(request, 'login.html')
#
# def custom_logout(request):
#     logout(request)
#     messages.success(request, "You have been logged out.")
#     return redirect('login')

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
# from .forms import CustomUserCreationForm

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # or your custom user model
from .models import Transaction

# @receiver(post_save, sender=User)
# def create_transaction_for_new_user(sender, instance, created, **kwargs):
#     if created:
#         Transaction.objects.create(
#             _id=instance.username,  # Ensure your Transaction model has an '_id' field
#             name=instance.username
#         )


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
# from .forms import CustomUserCreationForm  # Ensure you have this form defined


# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, f"Registration successful! Welcome, {user.username}!")
#             return redirect('login')  # Redirect to a success page
#         else:
#             messages.error(request, "Registration failed. Please correct the errors below.")
#     else:
#         form = CustomUserCreationForm()
#
#     return render(request, 'register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
# from .forms import CustomUserCreationForm
from .models import CustomerInformation

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()  # This saves the new user
#
#             # Assuming you collect additional info in the form
#             name = form.cleaned_data.get('name')
#             email = form.cleaned_data.get('email')
#             mailing_address = form.cleaned_data.get('mailing_address')
#
#             # Create a CustomerInformation instance
#             CustomerInformation.objects.create(
#                 name=name,
#                 email=email,
#                 mailing_address=mailing_address,
#                 user=user  # Link to the newly created user, assuming a user FK in CustomerInformation
#             )
#
#             messages.success(request, f"Registration successful! Welcome, {user.username}!")
#             return redirect('login')  # Redirect to a success page
#         else:
#             messages.error(request, "Registration failed. Please correct the errors below.")
#     else:
#         form = CustomUserCreationForm()
#
#     return render(request, 'register.html', {'form': form})


# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, "Registration successful! Welcome to the site, {}".format(user.name))
#             return redirect('product_detail')  # Redirect to an appropriate page after registration
#         else:
#             messages.error(request, "Please correct the error below.")
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'register.html', {'form': form})


# def process_purchase(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == 'POST':
#         try:
#             quantity = int(request.POST.get('quantity'))
#             base_price = product.price * quantity
#             shipping_charge = quantity * product.weight * 10  # $10 per unit weight
#             handling_charge = 5  # Fixed handling fee
#             total_cost = base_price + shipping_charge + handling_charge
#
#             # Check if the requested quantity is available
#             if product.quantity_on_hand >= quantity:
#                 credit_card_info = request.POST.get('creditCard')
#                 exp_date_str = request.POST.get('creditCardExpirationDate')
#
#                 try:
#                     exp_month, exp_year = map(int, exp_date_str.split('/'))
#                     exp_date = datetime.date(exp_year, exp_month, 1)
#                 except ValueError:
#                     messages.error(request, 'Invalid expiration date format. Please use MM/YYYY.')
#                     return redirect('purchase_failure')
#
#                 today = datetime.date.today()
#                 if exp_date < today:
#                     messages.error(request, 'Credit card is expired.')
#                     return redirect('purchase_failure')
#
#                 # Check if the provided credit card info matches any in Transaction model and is not expired
#                 if Transaction.objects.filter(cc=credit_card_info,exp =exp_date_str).exists():
#                     # Perform the purchase
#                     product.quantity_on_hand -= quantity
#                     product.save()
#
#                     customer_info = CustomerInformation.objects.create(
#                         name=request.POST.get('name'),
#                         email=request.POST.get('email'),
#                         mailing_address=request.POST.get('address'),
#                         credit_card_info=credit_card_info,
#                         quantity=quantity
#                     )
#
#                     # Send confirmation email
#                     send_mail(
#                         'Order Confirmation',
#                         f'Thank you for your purchase of {product.description}. Please confirm your order by clicking on this link.',
#                         'from@example.com',
#                         [request.POST.get('email')],
#                         fail_silently=False,
#                     )
#
#                     # Redirect with success message
#                     messages.success(request,
#                                      'Purchase completed successfully. Please check your email to confirm the order.')
#                     return HttpResponseRedirect(reverse(
#                         'purchase_success') + f'?total_cost={total_cost}&base_price={base_price}&shipping_charge={shipping_charge}&handling_charge={handling_charge}')
#
#                 else:
#                     # Credit card doesn't match or is expired
#                     messages.error(request,
#                                    'Credit card authorization failed: Card does not match any records or is expired.')
#                     return redirect('purchase_failure')
#
#             else:
#                 # Insufficient stock
#                 messages.error(request, 'Insufficient stock available.')
#                 return redirect('purchase_failure')
#
#         except ValueError:
#             # Handle invalid quantity input
#             messages.error(request, 'Invalid quantity provided.')
#             return redirect('purchase_failure')
#
#     else:
#         # Invalid request method
#         messages.error(request, 'Invalid request method.')
#         return redirect('purchase_failure')


# def process_purchase(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == 'POST':
#         try:
#             quantity = int(request.POST.get('quantity'))
#             base_price = product.price * quantity
#             shipping_charge = quantity * product.weight * 10  # $10 per unit weight
#             handling_charge = 5  # Fixed handling fee
#             total_cost = base_price + shipping_charge + handling_charge
#
#             # Check if the requested quantity is available
#             if product.quantity_on_hand >= quantity:
#                 credit_card_info = request.POST.get('creditCard')
#
#                 # Check if the provided credit card info matches any in Transaction model
#                 if Transaction.objects.filter(cc=credit_card_info).exists():
#                     # Perform the purchase
#                     product.quantity_on_hand -= quantity
#                     product.save()
#
#                     customer_info = CustomerInformation.objects.create(
#                         name=request.POST.get('name'),
#                         email=request.POST.get('email'),
#                         mailing_address=request.POST.get('address'),
#                         credit_card_info=credit_card_info,
#                         quantity=quantity
#                     )
#
#                     # Send confirmation email
#                     send_mail(
#                         'Order Confirmation',
#                         f'Thank you for your purchase of {product.description}. Please confirm your order by clicking on this link.',
#                         'from@example.com',
#                         [request.POST.get('email')],
#                         fail_silently=False,
#                     )
#
#                     # Redirect with success message
#                     messages.success(request, 'Purchase completed successfully. Please check your email to confirm the order.')
#                     return HttpResponseRedirect(reverse('purchase_success') + f'?total_cost={total_cost}&base_price={base_price}&shipping_charge={shipping_charge}&handling_charge={handling_charge}')
#
#                 else:
#                     # Credit card doesn't match
#                     messages.error(request, 'Credit card authorization failed: Card does not match any records.')
#                     return redirect('purchase_failure')
#
#             else:
#                 # Insufficient stock
#                 messages.error(request, 'Insufficient stock available.')
#                 return redirect('purchase_failure')
#
#         except ValueError:
#             # Handle invalid quantity input
#             messages.error(request, 'Invalid quantity provided.')
#             return redirect('purchase_failure')
#
#     else:
#         # Invalid request method
#         messages.error(request, 'Invalid request method.')
#         return redirect('purchase_failure')



# def process_purchase(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     print("process purchase called")
#     if request.method == 'POST':
#         try:
#             quantity = int(request.POST.get('quantity'))
#             print("Quantity 1:", quantity)
#             base_price = product.price * quantity
#             shipping_charge = quantity * product.weight * 10  # $10 per unit weight
#             handling_charge = 5  # Fixed handling fee
#             total_cost = base_price + shipping_charge + handling_charge
#
#             # Check if the requested quantity is available
#             if product.quantity_on_hand >= quantity:
#                 credit_card_info = request.POST.get('creditCard')
#
#                 # Check if the provided credit card info matches any in Transaction model
#                 if Transaction.objects.filter(cc=credit_card_info).exists():
#                     # Perform the purchase
#                     product.quantity_on_hand -= quantity
#                     product.save()
#
#                     CustomerInformation.objects.create(
#                         name=request.POST.get('name'),
#                         email=request.POST.get('email'),
#                         mailing_address=request.POST.get('address'),
#                         credit_card_info=credit_card_info,
#                         quantity=quantity
#                     )
#
#                     # Redirect with success message
#                     messages.success(request, 'Purchase completed successfully.')
#                     return HttpResponseRedirect(reverse('purchase_success') + f'?total_cost={total_cost}&base_price={base_price}&shipping_charge={shipping_charge}&handling_charge={handling_charge}')
#
#                 else:
#                     # Credit card doesn't match
#                     messages.error(request, 'Credit card authorization failed: Card does not match any records.')
#                     #return redirect('product_detail', product_id=product_id)
#                     return redirect('purchase_failure')
#
#             else:
#                 # Insufficient stock
#                 messages.error(request, 'Insufficient stock available.')
#                 return redirect('purchase_failure')
#
#         except ValueError:
#             # Handle invalid quantity input
#             messages.error(request, 'Invalid quantity provided.')
#             return redirect('purchase_failure')
#
#     else:
#         # Invalid request method
#         messages.error(request, 'Invalid request method.')
#         return redirect('purchase_failure')


# def process_purchase(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == 'POST':
#         quantity = int(request.POST.get('quantity'))
#         print("quantity",quantity)
#         base_price = product.price * quantity
#         shipping_charge = quantity * product.weight * 10  # $10 per unit weight
#         handling_charge = 5  # Fixed handling fee
#         total_cost = base_price + shipping_charge + handling_charge
#
#         # Check if the requested quantity is available
#         if product.quantity_on_hand >= quantity:
#             credit_card_info = request.POST.get('creditCard')
#
#             # Check if the provided credit card info matches any in Transaction model
#             if Transaction.objects.filter(cc=credit_card_info).exists():
#                 product.quantity_on_hand -= quantity
#                 product.save()
#
#                 customer_info = CustomerInformation(
#                     name=request.POST.get('name'),
#                     email=request.POST.get('email'),
#                     mailing_address=request.POST.get('address'),
#                     credit_card_info=credit_card_info,  # Be cautious with storing sensitive info
#                     quantity=quantity
#                 )
#                 customer_info.save()
#
#                 messages.success(request, 'Purchase completed successfully.')
#                 return HttpResponseRedirect(reverse(
#                     'purchase_success') + f'?total_cost={total_cost}&base_price={base_price}&shipping_charge={shipping_charge}&handling_charge={handling_charge}')
#
#             else:
#                 messages.error(request, 'Purchase can\'t be done due to authorization of credit card.')
#                 return redirect('product_detail', product_id=product_id)
#         else:
#             messages.error(request, 'Insufficient stock available.')
#             return redirect('product_detail', product_id=product_id)
#     else:
#         messages.error(request, 'Invalid request')
#         return redirect('product_detail', product_id=product_id)



def purchase_success(request):
    return render(request, 'purchase_success.html')

def purchase_failure(request):
    return render(request, 'purchase_failure.html')

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

# def process_to_checkout(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     if request.method == 'POST':
#         quantity = int(request.POST.get('quantity'))
#         base_price = product.price * quantity
#         shipping_charge = quantity * product.weight * 10
#         handling_charge = 5
#         total_cost = base_price + shipping_charge + handling_charge
#
#         user = request.user  # Assuming user is logged in and is an instance of your user model
#
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)
#         print("yes")
#         print("token",token)
#         context = {
#             'product': product,
#             'quantity': quantity,
#             'total_cost': total_cost,
#             'shipping_charge': shipping_charge,
#             'handling_charge': handling_charge,
#             'uid': uid,
#             'token': token,
#         }
#         return render(request, 'process_to_checkout.html', context)
#     return redirect('product_detail', product_id=product_id)


def process_to_checkout(request, product_id):
    # this function called in the button 'Proceed to checkout'
    print("process_to_checkout called")
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        print("quantity 2",quantity)
        base_price = product.price * quantity
        shipping_charge = quantity * product.weight * 10  # $10 per unit weight
        handling_charge = 5  # Fixed handling fee
        total_cost = base_price + shipping_charge + handling_charge

        context = {
            'product': product,
            'quantity': quantity,
            'total_cost': total_cost,
            'shipping_charge': shipping_charge,
            'handling_charge': handling_charge,
        }
        return render(request, 'process_to_checkout.html', context)
    return redirect('product_detail', product_id=product_id)



# def confirm_purchase(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = CustomerInformation.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, CustomerInformation.DoesNotExist):
#         user = None
#
#     if user is not None and default_token_generator.check_token(user, token):
#         # Proceed with the purchase
#         # Update the database or perform tasks as necessary
#         messages.success(request, 'Thank you for confirming your purchase.')
#         return redirect('purchase_success')
#     else:
#         messages.error(request, 'The confirmation link was invalid, possibly because it has already been used.')
#         return redirect('home')  # Or wherever you'd like to redirect in case of failure
