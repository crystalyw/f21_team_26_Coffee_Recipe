from django.urls import path
from web_project import views

urlpatterns = [
    path('', views.get_ingredient_list_page, name='home'),  # edit_ingredient_list TODO
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('logout', views.logout_action, name='logout'),
    path('result', views.get_available_ingredient_recipe, name='result'),
    path('save-recipe/<int:id>', views.save_recipe, name='save-recipe'),
    path('unsave-recipe/<int:id>', views.unsave_recipe, name='unsave-recipe'),
    path('recipe/<int:id>', views.get_recipe, name='recipe'),
    path('my-ingredient', views.get_ingredient_list_page, name='my-ingredient'),
    path('search', views.search, name='search'),
    path('map', views.display_map, name='map'),
    path('my-profile', views.my_profile, name='my-profile'),
    path('get-ingredient-list', views.get_ingredient_list_json_dumps_serializer, name='get-i-list'),
    path('add-ingredient', views.add_ingredient_list, name='add-ingredient'),
    path('update-ingredient', views.edit_ingredient_list, name='edit-ingredient'),
    path('delete-ingredient', views.delete_ingredient_list, name='delete-ingredient'),
    path('search-result', views.search, name='search-result'),
    path('photo/<int:id>', views.get_photo, name='photo')

]
