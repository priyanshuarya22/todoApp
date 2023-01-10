# todoApp

This app uses Keycloak for authentication, GraphQl for Api calls and stripe for payment.

To run the application create the image using Docker file and import the realm from the json file give.

Otherwise

on Linux/MacOS:

export FLASK_APP=main.py
flask run


on Windows:

set FLASK_APP=main.py
flask run


make sure all the requirements mentioned in requirements.txt are installed
