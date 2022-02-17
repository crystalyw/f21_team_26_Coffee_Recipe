from os import times
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Ingredient(models.Model):
    ingredient_name = models. CharField(max_length= 200)
    def __str__(self):
        return str(self.ingredient_name)


class Recipe(models.Model):
    recipe_name = models.CharField(max_length= 200)
    steps = models.TextField(max_length= 2000)
    time_cost = models.IntegerField(default= 0)
    category = models.CharField(max_length= 200)

    def __str__(self):
        return 'id=' + str(self.id) + ' ,recipe_name="' + str(self.recipe_name) + '"'

class User_Ingredient(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    ingredient = models.ForeignKey(Ingredient, default=None, on_delete=models.PROTECT)

    mg = 'mg'
    g = 'g'
    kg = 'kg'
    oz = 'oz'
    lb = 'lb'
    gt = 'gt'
    qt = 'qt'
    pt = 'pt'
    tsp = 'tsp'
    tbsp = 'tbsp'
    c = 'c'
    no = ''
    shots = 'shots'
    dash = 'dash'
    unit_choice = [(mg,'mg'),(g,'g'),(kg,'kg'),(oz,'oz'),(lb,'lb'),(qt,'qt'),(pt,'pt'),(tsp,'tsp'),(tbsp,'tbsp'),(c,'c'),(no,' '),(shots,'shots'),(dash,'dash')]
    
    ingredient_quantity = models.FloatField(null = True)
    ingredient_unit =  models.CharField(max_length = 5, choices= unit_choice, default= g)

class Recipe_Ingredient(models.Model):
    # The ingredient quantities in Recipe_Ingredient is for one serving
    recipe = models.ForeignKey(Recipe, default=None, on_delete=models.PROTECT)
    ingredient = models.ForeignKey(Ingredient, default=None , on_delete=models.PROTECT)
    
    mg = 'mg'
    g = 'g'
    kg = 'kg'
    oz = 'oz'
    lb = 'lb'
    gt = 'gt'
    qt = 'qt'
    pt = 'pt'
    tsp = 'tsp'
    tbsp = 'tbsp'
    c = 'c'
    no = ''
    shots = 'shots'
    dash = 'dash'
    unit_choice = [(mg,'mg'),(g,'g'),(kg,'kg'),(oz,'oz'),(lb,'lb'),(qt,'qt'),(pt,'pt'),(tsp,'tsp'),(tbsp,'tbsp'),(c,'c'),(no,' '),(shots,'shots'),(dash,'dash')]
    
    ingredient_unit = models.CharField(max_length = 5, choices= unit_choice, default= g)
    ingredient_quantity = models.FloatField( null = True)

    def __str__(self):
        return str(self.ingredient) 


class Profile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    zip_code = models.CharField(blank=True, max_length=20,validators=[RegexValidator(
        regex=r'^[0-9]{5}$',
        message= 'Must be valid zipcode in formats 12345')])
    city = models.CharField(max_length=200, blank=True,validators=[RegexValidator(
        regex=r'^[a-zA-Z]*$',
        message= 'Should not contain number')])
    country = models.CharField(max_length=200, blank=True,validators=[RegexValidator(
        regex=r'^[a-zA-Z]*$',
        message= 'Should not contain number')])
    saved_recipe = models.ManyToManyField(Recipe, default=None, related_name='saved_recipe')
    profile_pic = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return 'id=' + str(self.id) + ',text="' + self.username + '"'















