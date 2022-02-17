from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from configparser import ConfigParser

# user and authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404

# models
from django.urls import reverse
from web_project.forms import ProfileForm, RegisterForm, LoginForm, SearchForm
from web_project.models import Profile, Recipe, Ingredient, Recipe_Ingredient, User_Ingredient
from itertools import chain
import json
from django.db.models import Q
import os
from pathlib import Path
from configparser import ConfigParser

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")

def register_action(request):
    context = {}

    # display new registration form for GET request
    if request.method == 'GET':
        context['form'] = RegisterForm()
        print("context get:", context)
        return render(request, 'web_project/register.html', context)

    # create a bound from from POST request
    # store in context
    form = RegisterForm(request.POST)
    context['form'] = form

    # validate the form
    if not form.is_valid():
        return render(request, 'web_project/register.html', context)
    print("if valid", form.is_valid())
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password'])
    print("new_user_for_save", new_user)
    new_user.save()

    new_profile = Profile.objects.create(user=new_user)
    new_profile.save()

    # register automatically to login
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    print("new_user_for_login", new_user)
    login(request, new_user)
    return redirect(reverse('home'))
    # return render(request, 'web_project/recipe.html', {})


def login_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'web_project/login.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    # validates the form, return if fail
    if not form.is_valid():
        return render(request, 'web_project/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('home'))


# log out, back to log in
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def get_recipe(request, id):

    recipe = get_object_or_404(Recipe, id = id)
    ingredients = Recipe_Ingredient.objects.filter(recipe = Recipe.objects.get(id = id))

    steps =recipe.steps.split('STEP ')[1:]
    if recipe in Profile.objects.get(user=request.user).saved_recipe.all():
        saved = True
    else:
        saved = False
    print('saved', saved)
    context = {
        'recipe': recipe,
        'steps': steps,
        'ingredients': ingredients,
        'saved': saved
    }
    return render(request, 'web_project/recipe.html', context)


@login_required
def get_available_ingredient_recipe(request):

    # get user ingredient list
    user_ingredients = User_Ingredient.objects.filter(user=request.user).all()
    u_i_dict = {}
    for i in user_ingredients:
        u_i_dict[i.ingredient.id] = i.ingredient_quantity

    # loop through recipies and get their recipe_ingredients
    available_recipe = []
    for recipe in Recipe.objects.all():
        print("recipe name: ", recipe.recipe_name)
        # the ingredients needed for a specific recipe
        ingredients = recipe.recipe_ingredient_set.all()
        miss_i_ls = ''

        # loop through ingredients to check if all ingredients are satisfied
        # ingredients are only satisfied when the amount is at least enough for one serving
        missing_count = 0
        for ingredient in ingredients:
            i_id = ingredient.ingredient.id
            print("ingredient name", ingredient.ingredient.ingredient_name)
            # if the required ingredient is not in the user's ingredient dict
            # or if the quantity left is smaller than the number needed for 1 sample
            print(ingredient.ingredient_quantity)
            if not i_id in u_i_dict.keys(): 
                # or (i_id in u_i_dict.keys() and u_i_dict[i_id] < ingredient.ingredient_quantity):
                # add one missing
                print("missing", i_id)
                missing_count += 1
                miss_i_ls =ingredient.ingredient.ingredient_name

            # if more than 1 missing, don't go through more ingredients
            if missing_count > 1:
                print("missing more than 1!")
                break

        # for invalid recipes, don't add to return list
        if missing_count > 1:
            continue
        # once all ingredients are verified for this recipe, put recipe and count in the available list
        if missing_count == 0:
            print("sufficient!")
            available_recipe.append({
                'recipe': recipe,
                'miss_count': 0,
                'missing_ls': None
            })
        elif missing_count == 1:
            print("miss one!")
            available_recipe.append({
                'recipe': recipe,
                'miss_count': 1,
                'missing_ls': miss_i_ls
            })
        else:
            print("Something is wrong, should only have 1 or 0 missing")

    filter = []
    filter.append(1)
    filter.append(0)
    # Store the list in availble recipes and return to client
    context = {'available_recipe': available_recipe, 'filter': filter}
    print(context)
    return render(request, 'web_project/recipe_result.html', context)


# method used in single recipe display page to save recipe
@login_required
def save_recipe(request, id):

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    recipe_to_add = get_object_or_404(Recipe, id=id)

    # add recipe to saved_recipe in the user's profile
    Profile.objects.get(user=request.user).saved_recipe.add(recipe_to_add)

    return redirect('/web_project/recipe/'+ str(id))

@login_required
def unsave_recipe(request, id):

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    recipe_to_remove = get_object_or_404(Recipe, id=id)

    # add recipe to saved_recipe in the user's profile
    Profile.objects.get(user=request.user).saved_recipe.remove(recipe_to_remove)
    return redirect('/web_project/recipe/'+ str(id))


@login_required
def my_profile(request):
    context = {}
    if len(Profile.objects.filter(user=request.user).all()) == 0:
        new_profile = Profile.objects.create(user=request.user)
        new_profile.save()

    profile = Profile.objects.get(user=request.user)
    saved_recipe = profile.saved_recipe.all()

    if request.method == 'GET':
        context['profile'] = profile
        context['form'] = ProfileForm(initial={
            'zip_code': profile.zip_code,
            'city': profile.city,
            'country': profile.country
        })
        context['saved_recipe'] = saved_recipe
        return render(request, 'web_project/my_profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context['profile'] = profile
        context['form'] = form
        context['saved_recipe'] = saved_recipe
        return render(request, 'web_project/my_profile.html', context)
    
    if form.cleaned_data['profile_pic'] != None:
        pic = form.cleaned_data['profile_pic']
        print('Uploaded picture: {} (type={})'.format(pic, type(pic)))
        profile.profile_pic = pic
        profile.content_type = pic.content_type
    
    profile.zip_code = form.cleaned_data['zip_code']
    profile.city = form.cleaned_data['city']
    profile.country = form.cleaned_data['country']
    profile.save()

    context['profile'] = profile
    context['form'] = ProfileForm(initial={
        'zip_code': profile.zip_code,
        'city': profile.city,
        'country': profile.country
    })
    context['saved_recipe'] = saved_recipe

    return redirect(reverse('my-profile'))

@login_required
def get_photo(request, id):
    p = get_object_or_404(Profile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, p.profile_pic, type(p.profile_pic)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not p.profile_pic:
        raise Http404

    return HttpResponse(p.profile_pic, content_type=p.content_type)

@login_required
def add_ingredient_list(request):
    # check if ingredient exists
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("You must use a CSRF token", status=400)

    ingredient = get_object_or_404(Ingredient, id=request.POST['ingredient_id'])

    # check if unit is correct
    units_list = [u[1] for u in User_Ingredient.unit_choice]
    if request.POST['unit'] not in units_list:
        return _my_json_error_response("This unit does not exist.", status=400)

    # check if ingredient is already added by user
    user_i_exist = User_Ingredient.objects.filter(user=request.user).filter(ingredient=ingredient).all()
    if len(user_i_exist) > 0 :
        return _my_json_error_response("Ingredient already in your list.", status=400)
    
    if not request.POST['quantity'] or not is_float(request.POST['quantity']) or not float(request.POST['quantity']) > 0:
        return _my_json_error_response("Invalid quantity", status=400)

    # add new ingredient to user ingredient
    new_ingredient = User_Ingredient(user=request.user, ingredient=ingredient, ingredient_unit=request.POST['unit'], ingredient_quantity=float(request.POST['quantity']))
    new_ingredient.save()

    return get_ingredient_list_json_dumps_serializer(request)

def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def edit_ingredient_list(request):
    # check if user ingredient exists
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("You must use a CSRF token", status=400)

    user_ingredient = get_object_or_404(User_Ingredient, id=request.POST['user_ingredient_id'])

    # check if unit is correct
    units_list = [u[1] for u in User_Ingredient.unit_choice]
    if request.POST['unit'] not in units_list:
        return _my_json_error_response("This unit does not exist.", status=400)

    # check if quantity value valid
    if not request.POST['quantity'] or not is_float(request.POST['quantity']) or not float(request.POST['quantity']) > 0:
        return _my_json_error_response("Invalid quantity", status=400)

    # add new ingredient to user ingredient
    user_ingredient.ingredient_quantity=float(request.POST['quantity'])
    user_ingredient.ingredient_unit=request.POST['unit']
    user_ingredient.save()
    return update_ingredient_list_json_dumps_serializer(request)

def update_ingredient_list_json_dumps_serializer(request):
    # ingredients user have
    
    updated_ingredient = User_Ingredient.objects.get(id=request.POST['user_ingredient_id'])
    response_data = {
        'id': updated_ingredient.id,
        'ingredient': {
            'id': updated_ingredient.ingredient.id,
            'ingredient_name': updated_ingredient.ingredient.ingredient_name,
        },
        'ingredient_quantity': updated_ingredient.ingredient_quantity,
        'ingredient_unit': updated_ingredient.ingredient_unit,
    }

    response_json = json.dumps(response_data)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def delete_ingredient_list(request):

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("You must use a CSRF token", status=400)

    # check if user ingredient exists
    user_ingredient = get_object_or_404(User_Ingredient, id=request.POST['user_ingredient_id'])
    user_ingredient.delete()
    return get_ingredient_list_json_dumps_serializer(request)

@login_required
def get_ingredient_list_page(request):
    # ingredients catalog
    ingredients = Ingredient.objects.all().order_by('ingredient_name')
    # get the units
    units = [u[1] for u in User_Ingredient.unit_choice]

    context = {
        'ingredients': ingredients,
        'units':units,
    }
    return render(request, 'web_project/user_ingredient.html', context)

@login_required
def get_ingredient_list_json_dumps_serializer(request):
    response_data = []
    # ingredients user have
    user_ingredients = User_Ingredient.objects.filter(user=request.user)
    
    for u_i in user_ingredients:
        my_ingredient = {
            'id': u_i.id,
            'ingredient': {
                'id': u_i.ingredient.id,
                'ingredient_name': u_i.ingredient.ingredient_name,
            },
            'ingredient_quantity': u_i.ingredient_quantity,
            'ingredient_unit': u_i.ingredient_unit,
        }
        response_data.append(my_ingredient)

    response_json = json.dumps(response_data)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

    
def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

@login_required
def search(request):

    # receive search form data from user
    search = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            
            form_clean = form.cleaned_data['search']
            results = Recipe.objects.filter(Q(recipe_name__icontains = form_clean)|Q(steps__icontains= form_clean))
            context = {'available_recipe': results}
            # return search result to search result page
            return render(request,'web_project/search_result.html', context)
    
    # show search page
    return render(request, 'web_project/search.html', {"search": search})


@login_required
def display_map(request):
    context = {"GoogleAPIKey": CONFIG.get("GoogleAPI", "key")}
    return render(request, 'web_project/map.html', context)

