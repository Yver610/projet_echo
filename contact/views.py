from django.shortcuts import render, redirect
from .models import MessageContact
from django.contrib import messages
from django.core.mail import send_mail

def contact_view(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if nom and email and message:
            MessageContact.objects.create(nom=nom, email=email, message=message)

            # Envoi d'un e-mail de confirmation
            send_mail(
                subject="Nouveau message de contact",
                message=f"Nom : {nom}\nEmail : {email}\n\nMessage :\n{message}",
                from_email=None,  # utilisera DEFAULT_FROM_EMAIL
                recipient_list=['echo-du-bosquet@example.com'],  # à remplacer plus tard
                fail_silently=False,
            )


            messages.success(request, "Votre message a bien été envoyé.")
            return redirect('contact')
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return render(request, 'contact/contact.html')
