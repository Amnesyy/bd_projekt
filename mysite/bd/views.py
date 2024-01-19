from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
import re
from django.http import JsonResponse
import psycopg2
from django.contrib.auth import login,logout,authenticate
import urllib.parse as up
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from bd.models import CustomUser
from .forms import AddRankForm
from django.db import IntegrityError
#from .models import Pierwiastek

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.get(username=username)
        print(user)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('index')
        #else:
            #return render(request, 'login.html', {'error_message': 'Login Failed'})
    else:
        return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #print(username)
        users = CustomUser.objects.filter(username=username)
        if len(users) > 0:
            print("xd")
            return render(request, 'register.html', {'error_message': 'Username already exists'})
        else:
            user = CustomUser.objects.create_user(username=username, password=password)
            user.set_password(password)
            user.save()
            print(user)
            return redirect('login')
    else:
        return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('index')

up.uses_netloc.append("postgress")
conn = psycopg2.connect(dbname = "umrtbakq",
                        user = "umrtbakq",
                        password = "ZoGXloLY439j0aXYPWKnFblS7GC3qIMX",
                        host = "flora.db.elephantsql.com"
                        )
cursor = conn.cursor()

def index(request):
    return render(request, "home.html")

def getDB(request):

    cursor.execute("SELECT * FROM pierwiastki.wszystkie_pierwiastki;")
    result = cursor.fetchall()
    items = [r[0] for r in result]
    #return HttpResponse(data)
    return render(request, 'elements.html', {'items': items})

def get_additional_info(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items[]')

        # Fetch additional information (related tables) based on selected items
        additional_info = []
        if selected_items:
            for item in selected_items:
                # Assuming you have a table named 'related_table' with a foreign key to 'pierwiastki.pierwiastek'
                cursor.execute(f"SELECT pierwiastki.zwiazek.nazwa_zwiazek FROM pierwiastki.pierwiastek, pierwiastki.zwiazek, pierwiastki.pierwiastek_zwiazek WHERE pierwiastki.pierwiastek.nazwa_pierwiastek  = '{item}' and pierwiastki.pierwiastek.id_pierwiastek = pierwiastki.pierwiastek_zwiazek.id_p and pierwiastki.zwiazek.id_zwiazek = pierwiastki.pierwiastek_zwiazek.id_z;")
                related_data = cursor.fetchall()
                additional_info.append({'item': item, 'related_data': related_data})

        return JsonResponse({'additional_info': additional_info})

    return JsonResponse({'error': 'Invalid request method'})


def adder(request):
    print(request.user)
    if not request.user.is_authenticated:
        return render(request, 'error_message.html', {'error_message': 'We sie zaloguj'})
    if request.method == 'POST':
        name = request.POST.get('name')
        formula = request.POST.get('formula')
        category = request.POST.get('category')
        
        ranga_kategoria = [("CertyfikowanyNarkoman", 1), ("CertyfikowanyAptekarz", 2), ("CertyfikowanyDomownik", 3), ("CertyfikowanyWielkiChlop", 4)]
        user_rank_id = None
        for rk in ranga_kategoria:
            if(rk[0] == request.user.rank):
                user_rank_id = rk[1]
        
        try:
            cursor.execute("SELECT MAX(id_zwiazek) FROM pierwiastki.zwiazek;")
            max_id = cursor.fetchall()
            
            cursor.execute(f"SELECT id_kategorii FROM pierwiastki.kategoria WHERE nazwa_kategorii = '{category}';")
            id_kategorii = cursor.fetchall()
            id_kategorii_int = [i[0] for i in id_kategorii][0]
            
            max_id_int = [i[0] for i in max_id][0]
            max_id_int = max_id_int + 1
            if(user_rank_id != id_kategorii_int and not request.user.is_superuser):
                return render(request, 'adder.html', {'message': 'Brak uprawnień'})
            query = "INSERT INTO pierwiastki.zwiazek VALUES (%s, %s, %s, %s);"
            cursor.execute(query, (max_id_int, name, formula, id_kategorii_int))
            conn.commit()
        except IntegrityError as e:
            # Handle the exception
            error_message = str(e)
            return render(request, 'error_message.html', {'error_message': error_message})
    
    return render(request, 'adder.html', {'message': 'Dodano pomyślnie'})

def rate_compound(request, compound_id):
    if request.method == 'POST':
        user_rating = request.POST.get('user_rating')

        if user_rating and request.user.is_authenticated:
            cursor.execute("INSERT INTO pierwiastki.ocena (zwiazek_id, ocena) VALUES (%s, %s);",
                           [compound_id, user_rating])
            
            return redirect('compounds_list')  # Redirect after submitting the rating

    cursor.execute("SELECT * FROM pierwiastki.zwiazek WHERE id_zwiazek = %s;", [compound_id])
    result = cursor.fetchone()

    compound_details = {
        'compound_id': result[0],
        'compound_name': result[1],
        'compound_formula': result[2],
        'compound_category': result[3],
        # You may add more details if needed
    }

    return render(request, "rate_compound.html", {'compound_details': compound_details})

def submit_rating(request, compound_id):
    if request.method == 'POST':
        user_rating = request.POST.get('user_rating')

        if user_rating and request.user.is_authenticated:
            cursor.execute("INSERT INTO pierwiastki.ocena (id_zwiazek, ocena) VALUES (%s, %s);",
                           [compound_id, user_rating])
            conn.commit()
    return redirect('compunds_list')

def all_compounds(request):
    cursor.execute("SELECT * FROM pierwiastki.wszystkie_zwiazki;")
    result = cursor.fetchall()
    #items = [r for r in result]
    items_id = [r[0] for r in result]
    items_name = [r[1] for r in result]
    items_formula = [r[2] for r in result]
    
    cursor.execute("SELECT * FROM pierwiastki.kategoria_dla_zwiazku;")
    result = cursor.fetchall()
    
    average_ratings = []
    counts = []
    for compound_id in items_id:
        cursor.execute("SELECT AVG(ocena), COUNT(id_zwiazek) FROM pierwiastki.ocena WHERE id_zwiazek = %s;", [compound_id])
        res = cursor.fetchone()
        average_rating = res[0]
        count = res[1]
        average_ratings.append(round(average_rating, 1) if average_rating else None)
        counts.append(count)
    
    # Fetch user's ratings for each compound (assuming user authentication)
    #user_ratings = []
    #if request.user.is_authenticated:
    #    for compound_id in items_id:
    #        cursor.execute("SELECT ocena FROM pierwiastki.ocena WHERE id_zwiazek = %s;", [compound_id])
    #        user_rating = cursor.fetchone()
    #        user_ratings.append(user_rating[0] if user_rating else None)
    #else:
    #    user_ratings = [None] * len(items_id)
    
    items_category = [r[0] for r in result]
    items = zip(items_id, items_name, items_formula, items_category, average_ratings, counts)
    items = sorted(items, key=lambda x :x[0])
    
    return render(request, "all_compounds.html", {"compounds" : items})
    
def view_all_users(request):
    # Check if the user is authenticated and is a superuser
    if not (request.user.is_authenticated and request.user.is_superuser):
        return render (request, 'error_message.html', {'error_message': "Tylko dla admina tu wejść wolno"})

    # Get all users from the database along with their ranks
    all_users = CustomUser.objects.all()

    # Get the unique rank choices
    rank_choices = CustomUser.RANK_CHOICES

    # Render the template with the list of users and rank choices
    return render(request, 'all_users.html', {'all_users': all_users, 'rank_choices': rank_choices})

def add_rank(request):
    # Check if the user is authenticated and is a superuser
    if not (request.user.is_authenticated and request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to add ranks.")

    if request.method == 'POST':
        form = AddRankForm(request.POST)
        if form.is_valid():
            # Process the form data and add or delete the rank
            user = form.cleaned_data['user']
            rank = form.cleaned_data['rank']

            # Update the user's rank
            user_instance = CustomUser.objects.get(id=user.id)
            user_instance.rank = rank
            user_instance.save()

    else:
        form = AddRankForm()

    return redirect('view_all_users')