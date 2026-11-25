from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Contact
from django.views.generic import ListView
import re

# Phone number formatting
def format_phone(phone):
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits.startswith("7"):
        pass
    else:
        raise ValueError("Телефон нөмірі дұрыс емес!")

    return "+" + digits


# Email formatting
def format_email(email):
    email = email.strip().lower()

    if not email:
        return ""

    if "@" not in email:
        email += "@gmail.com"

    if not re.fullmatch(r"[a-z0-9._%+-]+@gmail\.com", email):
        raise ValueError("Email тек @gmail.com доменімен болуы керек!")

    return email
# Contact list

class ContactList(ListView):
    context_object_name = "contacts"
    paginate_by = 4  # add this

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Contact.objects.filter(created_by=self.request.user)
        return Contact.objects.filter(created_by=None)


# detail contact


@login_required(login_url="/login/")
def contact_details(request, id):
    contact = get_object_or_404(Contact, id=id)
    context = {"contact": contact}
    return render(request, "contact/contact_details.html", context)

# Add new contact


@login_required(login_url="/login/")
def new_contact(request):
    if request.method == "POST":
        try:
            created_by = request.user
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']

            phone = format_phone(request.POST.get("phone", ""))
            email = format_email(request.POST.get("email", ""))

            Contact.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                created_by=created_by
            )

            return redirect("/contacts/")

        except ValueError as error:
            return render(
                request,
                "contact/new_contact.html",
                {"error": str(error)}
            )

    return render(request, "contact/new_contact.html")

# Update a contact
@login_required(login_url="/login/")
def update_contact(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == "POST":
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']

            phone = format_phone(request.POST.get("phone", ""))
            email = format_email(request.POST.get("email", ""))

            Contact.objects.filter(pk=contact.id).update(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email
            )

            return redirect("/contacts/")

        except ValueError as error:
            context = {
                "contact": contact,
                "error": str(error)
            }
            return render(
                request,
                "contact/update_contact.html",
                context
            )

    context = {"contact": contact}
    return render(request, "contact/update_contact.html", context)

# Remove a contact
@login_required(login_url="/login/")
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    if request.method == "POST":
        contact.delete()
        return redirect("/contacts/")
    context = {"contact": contact}
    return render(request, "contact/delete_contact.html", context)
