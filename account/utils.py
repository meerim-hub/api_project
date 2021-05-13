from django.core.mail import send_mail


def send_activation_code(email, activation_code):
    message = f"""Thank you for registering. Activate your account using the link:
            http://127.0.0.1:8000/api/v1/account/activate/{activation_code}/"""
    send_mail(
        'Активация аккаунта',
        message,
        'test@test.com',
        [email, ],
        fail_silently=False
    )


