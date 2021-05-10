import os

from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

import requests
import random
import statistics
from statistics import mode

from models import db, connect_db, User, RecentlyViewedDrink, RecentlyViewedIngredient, UserDrink, UserIngredient, Original
from forms import UserAddForm, LoginForm, UpdateUserForm, NewOriginalForm, UpdateUserForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable or,
# if not set there, use development local db.

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///cocktails_db'))


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['EXPLAIN_TAMPLATE_LOADING'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


##############################################################################
# User routes


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/users/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup. Create new user and add to DB"""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("/users/signup.html", form=form)

        do_login(user)
        flash(f"Hello, {user.username}. Cheers!", "success")
        return redirect("/")

    else:
        return render_template("/users/signup.html", form=form)


@app.route('/users/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}. Cheers!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/users/login.html', form=form)


@app.route('/users/<int:user_id>')
def show_user_page(user_id):
    """Show user content"""

    if not g.user:
        flash("Please login to view your page", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    recents = most_recent(user_id)
    saved_drinks = get_saved_drinks(user.id)
    saved_ingredients = get_saved_ingredients(user.id)
    recs = generate_recs(recents, saved_drinks, saved_ingredients)
    ogs = (Original.query.filter(Original.user == user_id).all())

    return render_template('/users/show.html',
                           user=user,
                           recents=recents,
                           saved_drinks=saved_drinks,
                           saved_ingredients=saved_ingredients,
                           recs=recs,
                           ogs=ogs)


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def update_user(user_id):
    """Update profile for current user"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash(f"User {user_id} updated", "success")
        return redirect(f'/users/{user.id}')

    else:
        return render_template("/users/edit.html", form=form)


@app.route('/users/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("See you next time!", "success")

    return redirect('/')


@app.route('/users/saved-drinks')
def list_saved_drinks():
    """Show a page for all of the users' saved drinks"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    saved_drinks = get_saved_drinks(g.user.id)

    return render_template('/users/saved-drinks.html',
                           saved_drinks=saved_drinks)


@app.route('/users/saved-ingredients')
def list_saved_ingredients():
    """Show a page for all of the users saved ingredients"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    saved_ingredients = get_saved_ingredients(g.user.id)

    return render_template('/users/saved-ingredients.html',
                           saved_ingredients=saved_ingredients)


@app.route('/users/originals')
def show_originals():
    """Show a page for all of the users original drinks"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    ogs = (Original.query.filter(Original.user == g.user.id).all())

    return render_template('/users/originals.html', ogs=ogs)


@app.route('/users/recent')
def show_recent():
    """Show a page for all of the users' recently viewed drinks"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    recents = most_recent(g.user.id)

    return render_template('/users/recent.html', recents=recents)


@app.route('/users/new-drink', methods=['GET', 'POST'])
def handle_new_drinks():
    """Show form for creating an orignial, create a new instnace of orignial upon submission"""

    if not g.user:
        flash("Please login before creating your recipes", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)

    form = NewOriginalForm()

    if form.validate_on_submit():

        try:
            og = Original(
                user=g.user.id,
                strDrink=form.name.data,
                strVideo=form.video.data,
                strCategory=form.category.data,
                strIBA=form.iba.data,
                strGlass=form.glass.data,
                strInstructions=form.instructions.data,
                strDrinkThumb=form.drinkThumb.data or Original.strDrinkThumb.default.arg,
                strIngredient1=form.ingredient1.data,
                strMeasure1=form.measure1.data,
                strIngredient2=form.ingredient2.data,
                strMeasure2=form.measure2.data,
                strIngredient3=form.ingredient3.data,
                strMeasure3=form.measure3.data,
                strIngredient4=form.ingredient4.data,
                strMeasure4=form.measure4.data,
                strIngredient5=form.ingredient5.data,
                strMeasure5=form.measure5.data,
                strIngredient6=form.ingredient6.data,
                strMeasure6=form.measure6.data,
                strIngredient7=form.ingredient7.data,
                strMeasure7=form.measure7.data,
                strIngredient8=form.ingredient8.data,
                strMeasure8=form.measure8.data,
                strIngredient9=form.ingredient9.data,
                strMeasure9=form.measure9.data,
                strIngredient10=form.ingredient10.data,
                strMeasure10=form.measure10.data
            )

            db.session.add(og)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Recipe name must be unique", 'danger')
            return render_template('/users/new.html', form=form)

        flash("New drink created!", "secccess")
        return redirect("/users/originals")

    return render_template('/users/new-drink.html',
                           user=user,
                           form=form)


@app.route('/users/show-original/<int:og_id>')
def show_original(og_id):
    """Show page for user-made original drinks"""

    drink = Original.query.get_or_404(og_id)

    return render_template('/users/show-original.html', drink=drink,
                           INGREDIENTS=INGREDIENTS)


@app.route('/users/original/delete/<int:og_id>', methods=['POST'])
def delete_original(og_id):
    """Delete an orignal recipe made by a user"""

    og = Original.query.get(og_id)
    db.session.delete(og)
    db.session.commit()
    return jsonify(message="Removed")


#############################################################################
# Drink Routes
@ app.route('/drinks/<int:drink_id>')
def show_drink_page(drink_id):
    """Show drink information"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    handle_recently_viewed_drink(g.user.id, drink_id)
    user = User.query.get_or_404(g.user.id)
    drink = get_drink_by_id(drink_id)

    return render_template('/drinks/show.html',
                           user=user,
                           drink=drink,
                           INGREDIENTS=INGREDIENTS,
                           others=get_drinks_by_ingredient(
                               drink["strIngredient1"]),
                           saved=saved_drk(user.id, drink))


@ app.route('/drinks/save/<int:idDrink>', methods=['POST'])
def handle_saved_drink(idDrink):
    """Create an instane of UserDrink
    Add the saved drink to the database"""

    try:
        saved_drink = UserDrink(user_id=g.user.id, drink_id=idDrink)
        db.session.add(saved_drink)
        db.session.commit()
        return jsonify(message="Saved")

    except IntegrityError:
        db.session.rollback()
        drink = UserDrink.query.filter(
            UserDrink.user_id == g.user.id, UserDrink.drink_id == idDrink).delete()
        db.session.commit()
        return jsonify(message="Removed")


#############################################################################
# Ingredient Routes


@ app.route('/ingredients/<ingredient>')
def show_ingredient_details(ingredient):
    """Show ingredient information"""

    if not g.user:
        flash("Please login to view", "danger")
        return redirect("/")

    ingredient = get_ingredient_by_name(ingredient)
    handle_recenly_viewed_ingredient(g.user.id, ingredient['strIngredient'])
    user = User.query.get_or_404(g.user.id)
    recs = get_drinks_by_ingredient(ingredient['strIngredient'])
    saved = saved_ing(user.id, ingredient['strIngredient'])

    return render_template('ingredients/show.html',
                           ingredient=ingredient,
                           user=user,
                           recs=recs,
                           saved=saved)


@ app.route('/ingredients/save/<ingredient>', methods=['POST'])
def handle_saved_ingredient(ingredient):
    """Create an instane of UserIngredient
    Add the saved ingredient to the database"""

    try:
        saved_ingredient = UserIngredient(
            user_id=g.user.id, ingredient=ingredient)
        db.session.add(saved_ingredient)
        db.session.commit()
        return jsonify(message="Saved")

    except IntegrityError:
        db.session.rollback()
        drink = UserIngredient.query.filter(
            UserIngredient.user_id == g.user.id, UserIngredient.ingredient == ingredient).delete()
        db.session.commit()
        return jsonify(message="Removed")


##############################################################################
# Handle search feature


@app.route('/search')
def search():
    """Handle GET requests for search terms"""

    term = request.args["q"]
    res = get_drink_by_name(term)

    return render_template('/search.html',
                           term=term,
                           res=res)


##############################################################################
# Homepage and error pages


##############################################################################
# Turn off all caching in Flask2


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


###################################################################
# External API Call Helper Functions


API_BASE_URL = "http://www.thecocktaildb.com/api/json/v1/1/"


def get_drink_by_id(idDrink):
    """Look up full cocktail details by id"""

    if idDrink:
        resp = requests.get(f"{API_BASE_URL}lookup.php?i={idDrink}")
        return resp.json()['drinks'][0]

    else:
        return None


def get_all_ingredients():
    """API call to get all ingredients"""

    resp = requests.get(f"{API_BASE_URL}list.php?i=list")

    return [item['strIngredient1'] for item in (resp.json()['drinks'])]


def get_random_drinks():
    """API call to get 4 random drinks"""

    drinks = []
    for i in range(4):
        drinks.append(requests.get(
            f"{API_BASE_URL}random.php").json()['drinks'][0])

    return drinks


def get_drinks_by_ingredient(ingredient):
    """Generate a list of 4 random drinks by ingredient"""

    resp = requests.get(
        f"{API_BASE_URL}filter.php?i={ingredient}"
    )
    if len(resp.json()['drinks']) <= 4:
        rand_samp = resp.json()['drinks']
    else:
        rand_samp = (random.sample(resp.json()['drinks'], 4))

    return [get_drink_by_id(int(i['idDrink'])) for i in rand_samp]


def get_ingredient_by_name(ingredient):
    """API call to search ingredient by name"""
    resp = requests.get(
        f"{API_BASE_URL}search.php?i={ingredient}"
    )

    return resp.json()['ingredients'][0]


INGREDIENTS = get_all_ingredients()


###################################################################
# SQLA Helper Functions


def handle_recently_viewed_drink(usr_id, drk_id):
    """Handle adding drink to user's Recently Viewed if not present + DB Commit"""

    try:
        recently_viewed = RecentlyViewedDrink(
            user_id=usr_id, drink_id=drk_id)
        db.session.add(recently_viewed)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        pass


def handle_recenly_viewed_ingredient(usr_id, ingredient_name):
    """Handle adding ingredient to user's Recently viewed if not already present + DB Commit"""

    try:
        recently_viewed = RecentlyViewedIngredient(
            user_id=usr_id, ingredient=ingredient_name)
        db.session.add(recently_viewed)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        pass


def most_recent(usr_id):
    """Get the 4 most recently viewed drinks by user_id"""

    user = User.query.get_or_404(usr_id)
    recent = RecentlyViewedDrink.query.filter(
        RecentlyViewedDrink.user_id == user.id).all()
    if len(recent) == 0:
        return None
    else:
        lst = []
        for drink in recent:
            resp = get_drink_by_id(drink.drink_id)
            lst.insert(0, resp)

        return lst


def saved_drk(usr_id, drink):
    """Check to see if a user has already saved instance of UserDrink"""

    saved_drinks = (UserDrink
                    .query
                    .filter(UserDrink.user_id == usr_id)
                    .all())

    for d in saved_drinks:
        if str(d.drink_id) == drink['idDrink']:
            return True

    return False


def saved_ing(usr_id, ing):
    """Check to see if a user has already saved instance of UserIngredient"""

    saved = (UserIngredient
             .query
             .filter(UserIngredient.user_id == usr_id)
             .all())

    for i in saved:
        if str(i.ingredient) == ing:
            return True
    else:
        return False


def get_saved_drinks(usr_id):
    """Query and create a list for all saved drinks for a user by ID"""

    saved_drinks = (UserDrink
                    .query
                    .filter(UserDrink.user_id == usr_id)
                    .all())

    lst = []

    for drink in saved_drinks:
        resp = get_drink_by_id(drink.drink_id)
        lst.insert(0, resp)

    return lst


def get_saved_ingredients(usr_id):
    """Query by user ID and return a list of all saved ingredients"""

    saved_ingredients = (UserIngredient
                         .query
                         .filter(UserIngredient.user_id == usr_id)
                         .all())

    lst = []

    for i in saved_ingredients:
        reps = get_ingredient_by_name(i.ingredient)
        lst.insert(0, reps)

    return lst


#######################################################################
# General Helper Functions

def most_frequent(List):
    """Takes a list are returns the most frequent value w/ lowest index as tie breaker"""

    return max(set(List), key=List.count)


def generate_recs(recent, saved_drk, saved_ing):
    """Takes dicts of from user page and finds the most common ingredient"""

    lst = []

    if recent != None:
        for i in recent:
            lst.append(i['strIngredient1'])

    for i in saved_drk:
        lst.append(i['strIngredient1'])

    for i in saved_ing:
        lst.append(i['strIngredient'])

    if len(lst):
        return get_drinks_by_ingredient(most_frequent(lst))

    else:
        return None
