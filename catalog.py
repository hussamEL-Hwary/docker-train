# Library imports.
from flask import Flask, render_template, request, redirect, jsonify, url_for,\
    session as login_session, make_response, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from catalog_datamodel import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)


# Constants.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "KickButt Catalog"

NUM_RECENT_ITEMS = 8  # Max number of items to include in recent items list.


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show latest items regardless of category. This is the home page for the app.
@app.route('/')
@app.route('/catalog/')
def showLatestItems():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id)) \
        .limit(NUM_RECENT_ITEMS)
    if 'username' not in login_session:
        return render_template('catalog.html',
                               categories=categories,
                               items=items,
                               user_id=None)
    else:
        return render_template('catalog.html',
                               categories=categories,
                               items=items,
                               user_id=login_session['user_id'])


# Show all items in a specific category.
@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(asc(CategoryItem.name)) \
        .filter_by(category_id=category_id)
    categoryName = items[0].category.name
    if 'username' not in login_session:
        return render_template('category.html',
                               categories=categories,
                               categoryName=categoryName,
                               items=items,
                               user_id=None)
    else:
        return render_template('category.html',
                               categories=categories,
                               categoryName=categoryName,
                               items=items,
                               user_id=login_session['user_id'])


# Add a new item.
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id)) \
        .limit(NUM_RECENT_ITEMS)

    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategoryItem(
            name=request.form['name'],
            user_id=login_session['user_id'],
            category_id=request.form['category_id'],
            description=request.form['description'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showLatestItems'))
    else:
        return render_template('newItem.html',
                               categories=categories,
                               user_id=login_session['user_id'])


# Show description of an individual item.
@app.route('/categoryitem/<int:item_id>/')
def showItem(item_id):
    item = session.query(CategoryItem). \
        filter_by(id=item_id).one()
    if 'username' not in login_session:
        return render_template('showItem.html',
                               item=item,
                               user_id=None)
    else:
        return render_template('showItem.html',
                               item=item,
                               user_id=login_session['user_id'])


# Edit an individual item.
@app.route('/edititem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(item_id):
    categories = session.query(Category).order_by(asc(Category.name))
    editItem = session.query(CategoryItem). \
        filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['category_id']:
            editItem.category_id = request.form['category_id']
        if request.form['description']:
            editItem.description = request.form['description']
        session.add(editItem)
        session.commit()
        return redirect(url_for('showLatestItems'))
    else:
        return render_template('editItem.html',
                               categories=categories,
                               item=editItem,
                               user_id=login_session['user_id'])


# Delete an individual item.
@app.route('/deleteitem/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(CategoryItem). \
        filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showLatestItems'))
    else:
        return render_template('deleteItem.html',
                               item=item,
                               user_id=login_session['user_id'])


# JSON end point for all items in all categories.
@app.route('/catalog/JSON')
def catalogJSON():
    items = session.query(CategoryItem).all()
    return jsonify(CategoryItem=[i.serialize for i in items])


# JSON end point for all categories.
@app.route('/category/JSON')
def categoryJSON():
    items = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in items])


# JSON end point for all items in a specific category.
@app.route('/category/<int:category_id>/JSON')
def catalogItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem). \
        filter_by(category_id=category_id).all()
    return jsonify(CategoryItem=[i.serialize for i in items])


# JSON end point for a specific item.
@app.route('/item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    items = session.query(CategoryItem). \
        filter_by(id=item_id).all()
    return jsonify(CategoryItem=[i.serialize for i in items])


# Disconnect from google
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLatestItems'))
    else:
        return redirect(url_for('showLatestItems'))


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Google api connection.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = 'Welcome ' + login_session['username']
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Applicaiion start up.
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
