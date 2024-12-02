# # utils.py in your Django app directory
#
# from django.core.mail import send_mail
# from django.urls import reverse
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text
# from django.contrib.auth.tokens import default_token_generator
# from .models import CustomerInformation
#
# def send_confirmation_email(user, request):
#     token = default_token_generator.make_token(user)
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     link = request.build_absolute_uri(
#         reverse('confirm_purchase', kwargs={'uidb64': uid, 'token': token})
#     )
#     subject = 'Confirm Your Purchase'
#     message = f'Hi {user.name}, please confirm your purchase by clicking on this link: {link}'
#     send_mail(subject, message, 'from@example.com', [user.email], fail_silently=False)
