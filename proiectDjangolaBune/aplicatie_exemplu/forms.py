from django import forms
from .models import Category
from .models import Product
import json
import os
import time
import re
from datetime import datetime, date

class ProductFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Nume produs")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Categorie")
    min_price = forms.DecimalField(required=False, min_value=0, label="Preț minim")
    max_price = forms.DecimalField(required=False, min_value=0, label="Preț maxim")
    min_stock = forms.IntegerField(required=False, min_value=0, label="Stoc minim")
    max_stock = forms.IntegerField(required=False, min_value=0, label="Stoc maxim")
    
#task 2 lab 5

# Funcție comună de validare pentru câmpurile text

def validate_text(value):
    if not value.replace(" ", "").isalpha():
        raise forms.ValidationError("Câmpul poate conține doar litere și spații.")
    if not value[0].isupper():
        raise forms.ValidationError("Textul trebuie să înceapă cu literă mare.")

# Funcție de validare pentru formatul datei (DD/MM/YYYY) și vârsta minimă de 18 ani
def validate_date_format(value):
    try:
        birth_date = datetime.strptime(value, "%d/%m/%Y").date()
        today = date.today()
        age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        age_months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
        age_months = age_months % 12  # Numărul de luni rămase după ani întregi
        if age_years < 18:
            raise forms.ValidationError("Trebuie să ai cel puțin 18 ani pentru a trimite un mesaj.")
    except ValueError:
        raise forms.ValidationError("Data trebuie să fie în formatul DD/MM/YYYY.")

# Funcție de validare pentru mesaj
def validate_message(value):
    words = re.findall(r'\b\w+\b', value)
    if not (5 <= len(words) <= 100):
        raise forms.ValidationError("Mesajul trebuie să conțină între 5 și 100 de cuvinte.")
    
    # Verificare dacă mesajul conține linkuri
    if re.search(r'\bhttps?://\S+', value):
        raise forms.ValidationError("Mesajul nu poate conține linkuri.")
    
    # Verificare dacă ultimul cuvânt este numele utilizatorului
    if words and words[-1] != value.split()[-1]:
        raise forms.ValidationError("Mesajul trebuie să se încheie cu numele expeditorului ca semnătură.")

# Formularul pentru pagina de contact
class ContactForm(forms.Form):
    nume = forms.CharField(
        max_length=10,
        required=True,
        label="Nume",
        validators=[validate_text],
        error_messages={'required': "Numele este obligatoriu.", 'max_length': "Numele nu poate avea mai mult de 10 caractere."}
    )
    prenume = forms.CharField(
        required=False,
        label="Prenume",
        validators=[validate_text]
    )
    data_nasterii = forms.CharField(
        required=True,
        label="Data nașterii",
        validators=[validate_date_format],
        error_messages={'required': "Data nașterii este obligatorie și trebuie să fie în formatul DD/MM/YYYY."}
    )
    email = forms.EmailField(
        required=True,
        label="E-mail",
        error_messages={'required': "E-mailul este obligatoriu."}
    )
    confirmare_email = forms.EmailField(
        required=True,
        label="Confirmare e-mail",
        error_messages={'required': "Confirmarea e-mailului este obligatorie."}
    )
    tip_mesaj = forms.ChoiceField(
        choices=[('reclamatie', 'Reclamație'), ('intrebare', 'Întrebare'), ('review', 'Review'), ('cerere', 'Cerere'), ('programare', 'Programare')],
        required=True,
        label="Tip mesaj"
    )
    subiect = forms.CharField(
        required=True,
        label="Subiect",
        validators=[validate_text],
        error_messages={'required': "Subiectul este obligatoriu."}
    )
    minim_zile_asteptare = forms.IntegerField(
        required=True,
        label="Minim zile așteptare",
        min_value=1,
        error_messages={'required': "Trebuie să specifici minimul zilelor de așteptare.", 'min_value': "Numărul trebuie să fie mai mare strict ca zero."}
    )
    mesaj = forms.CharField(
        required=True,
        label="Mesaj",
        widget=forms.Textarea(attrs={'style': 'resize: none; display: block; margin-top: 5px;'}),
        validators=[validate_message],
        error_messages={'required': "Mesajul este obligatoriu."}
    )

    # Validare e-mailuri
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirmare_email = cleaned_data.get("confirmare_email")
        if email and confirmare_email and email != confirmare_email:
            raise forms.ValidationError("E-mailul și confirmarea e-mailului trebuie să coincidă.")

    # Funcție de salvare a mesajului într-un fișier JSON
    def save(self):
        cleaned_data = self.cleaned_data
        birth_date = datetime.strptime(cleaned_data.get("data_nasterii"), "%d/%m/%Y").date()
        today = date.today()
        age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        age_months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
        age_months = age_months % 12  # Numărul de luni rămase după ani întregi
        
        # Procesare mesaj - înlocuim linii noi cu spații și eliminăm spațiile multiple
        mesaj = cleaned_data.get("mesaj").replace("\n", " ")
        mesaj = re.sub(r'\s+', ' ', mesaj).strip()
        
        folder_path = os.path.join(os.getcwd(), "mesaje")
        
        # Creare folder "mesaje" dacă nu există
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Salvare mesaj într-un fișier JSON
        timestamp = int(time.time())
        file_path = os.path.join(folder_path, f"mesaj_{timestamp}.json")
        
        data_to_save = {
            "nume": cleaned_data.get("nume"),
            "prenume": cleaned_data.get("prenume"),
            "email": cleaned_data.get("email"),
            "varsta": f"{age_years} ani și {age_months} luni",
            "tip_mesaj": cleaned_data.get("tip_mesaj"),
            "subiect": cleaned_data.get("subiect"),
            "minim_zile_asteptare": cleaned_data.get("minim_zile_asteptare"),
            "mesaj": mesaj
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        
        return file_path
    

#task 3 lab5
class ProductForm(forms.ModelForm):
    # Adăugăm două câmpuri suplimentare pentru reducere și TVA
    discount_percentage = forms.DecimalField(
        required=True,
        min_value=0,
        max_value=100,
        label="Procent reducere",
        help_text="Introduceți un procent între 0 și 100.",
        error_messages={
            'required': "Procentul de reducere este obligatoriu.",
            'min_value': "Procentul trebuie să fie minim 0.",
            'max_value': "Procentul nu poate depăși 100."
        }
    )
    tax_percentage = forms.DecimalField(
        required=True,
        min_value=0,
        max_value=50,
        label="Procent TVA",
        error_messages={
            'required': "Procentul de TVA este obligatoriu.",
            'min_value': "TVA-ul trebuie să fie minim 0%.",
            'max_value': "TVA-ul nu poate fi mai mare de 50%."
        }
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'stock_quantity', 'price']
        labels = {
            'name': "Nume Produs",
            'description': "Descriere",
            'price': "Preț Final",
            'category': "Categorie",
            'stock_quantity': "Stoc"
        }
        error_messages = {
            'name': {'required': "Numele produsului este obligatoriu."},
            'price': {'required': "Prețul este obligatoriu.", 'min_value': "Prețul trebuie să fie mai mare decât 0."},
            'category': {'required': "Categoria este obligatorie."},
            'stock_quantity': {'required': "Stocul este obligatoriu."}
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Prețul trebuie să fie mai mare decât 0.")
        return price

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError("Reducerea trebuie să fie între 0% și 100%.")
        return discount

    def clean_tax_percentage(self):
        tax = self.cleaned_data.get('tax_percentage')
        if tax is not None and (tax < 0 or tax > 50):
            raise forms.ValidationError("TVA-ul trebuie să fie între 0% și 50%.")
        return tax

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount = cleaned_data.get('discount_percentage')
        tax = cleaned_data.get('tax_percentage')

        if price is not None and discount is not None and tax is not None:
            # Aplicăm reducerea și TVA-ul
            discounted_price = price - (price * (discount / 100))
            final_price = discounted_price * (1 + tax / 100)

            if final_price < 1:
                raise forms.ValidationError("Prețul final după reducere și TVA nu poate fi mai mic de 1 unitate monetară.")

            # **Actualizăm prețul în instanța modelului pentru a fi salvat**
            self.instance.price = round(final_price, 2)

        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)  # Obținem instanța produsului
        product.price = self.instance.price  # **Setăm prețul final calculat**

        if commit:
            product.save()  # Salvăm produsul în baza de date
        return product