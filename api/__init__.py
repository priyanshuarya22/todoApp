import os

import stripe
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, g, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import logging
from flask_oidc import OpenIDConnect
import requests
from oauth2client.client import OAuth2Credentials
from keycloak import KeycloakOpenID
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'api/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'sLPERzdnKk0GyMFNLHyAU1U4wlYxgDgt',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'flask-app',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/todo.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
oidc = OpenIDConnect(app)

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="flask",
                                 realm_name="flask-app",
                                 client_secret_key="pww8bSrx1sYC1oLsDkWwj7P2SS6BbpiK")

stripe.api_key = 'sk_test_51MOhzwSIFHw26Et1GBL9pxsAzhAxAPlfyaccwZ9GfHH2I3QB1Su9wq2W61P4cXsoSQiQycIquLf9HMTuyjsYiDvO00Zwycs9Tn'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def auth(user):
    from api.models import UserRole
    user_id = user.get('sub')
    username = user.get('preferred_username')
    role = 'free'
    if user_id in oidc.credentials_store:
        access_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).access_token
    else:
        access_token = None
    check = UserRole.query.filter_by(user_id=username).first()
    if check:
        role = check.role
    else:
        user_role = UserRole(user_id=username, role='free')
        db.session.add(user_role)
        db.session.commit()
    return username, access_token, role


@app.route("/graphql", methods=["POST"])
@oidc.accept_token(require_token=True)
def graphql_server():
    data = request.get_json()

    from main import schema
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.route('/', methods=['GET'])
@oidc.require_login
def index():
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    d = {'username': (auth(user))[0], 'access_token': (auth(user))[1], 'role': (auth(user))[2]}
    if not d['access_token']:
        oidc.logout()
        return redirect(request.url)
    return render_template('index.html', vars=d)


@app.route('/logout')
@oidc.require_login
def logout():
    oidc.logout()
    return redirect('http://localhost:8080/realms/flask-app/protocol/openid-connect/logout')


@app.route('/add')
@oidc.require_login
def addTodo():
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    d = {'username': (auth(user))[0], 'access_token': (auth(user))[1], 'role': (auth(user))[2]}
    if not d['access_token']:
        oidc.logout()
        return redirect(request.url)
    return render_template('add.html', vars=d)


@app.route('/edit/<int:todo_id>')
@oidc.require_login
def edit_todo(todo_id):
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    d = {'username': (auth(user))[0], 'access_token': (auth(user))[1], 'role': (auth(user))[2], 'todo_id': todo_id}
    if not d['access_token']:
        oidc.logout()
        return redirect(request.url)
    return render_template('edit.html', vars=d)


@app.route('/upload', methods=['POST'])
@oidc.require_login
def upload():
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    username, access_token, role = auth(user)
    if role == 'free':
        return "Purchase Premium! <a href='/'>Home</a>"
    if 'file' not in request.files:
        return "No file part <a href='/'>Home</a>"
    else:
        file = request.files['file']
        if file.filename == '':
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], username)):
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], username))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], username, filename))
            return redirect('/')


@app.route("/buy")
@oidc.require_login
def buy():
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    d = {'username': (auth(user))[0], 'access_token': (auth(user))[1], 'role': (auth(user))[2]}
    if not d['access_token']:
        oidc.logout()
        return redirect(request.url)
    return render_template('payment.html', vars=d)


@app.route("/create-checkout-session", methods=['POST'])
@oidc.require_login
def create_checkout_session():
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': 'Premium Plan',
                },
                'unit_amount': 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:5000/success',
        cancel_url='http://localhost:5000/cancel'
    )

    return redirect(session.url, code=303)


@app.route("/success")
@oidc.require_login
def success():
    from api.models import UserRole
    user = oidc.user_getinfo(['preferred_username', 'email', 'sub', 'groups'])
    username, access_token, role = auth(user)
    user_role = UserRole.query.filter_by(user_id=username).first()
    user_role.role = "paid"
    db.session.commit()
    return redirect('/')
