# Recipe Website
This website aims to organize recipes for multiple users.
See [my website](https://rezepte.juliaschmid.com/) for a demo

## Features
* creating/updating/deleting recipes
* adding multiple images to a recipe
* multi-user support: 
  * recipes can be either private or public
  * passwort reset/change
* converting ingredients according to a new number of servings
* sorting by categories
* advanced search with:
  * search by name (searches in recipe.title, recipe.introduction, recipe.instructions, recipe.notes)
  * which categories to search in
  * which foods the recipe should include ('OR' and 'AND' possible)
  * which foods the recipe should NOT contain
  
  ### Coming Soon
  * Markdown Editor for introduction, instructions and notes
  * more complex multi-user permissions: select who can view your recipes instead of only public/private 
  * Share Links for recipes
  * Print Recipe
  * Language support (select interface language in profile, currently it's all in German)

## Requirements
To install the requirements use
```pip3 install -r requirements.txt```
