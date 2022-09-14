from functools import wraps
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt
# import jwt
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, check_permissions, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resource={r"/*": {"origins": "*"}})

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    try:
        all_drinks = Drink.query.all()
        if len(all_drinks) == 0:
            abort(404)
        drinks = [drink.short() for drink in all_drinks]

        return jsonify({
            "success": True, 
            "status Code": 200,
            "drinks": drinks
        })
    except:
        abort(422)
'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        all_drinks = Drink.query.all()
        if len(all_drinks) == 0:
            abort(404)
        drinks_detail = [drink.long() for drink in all_drinks]

        return({
            "success": True, 
            "status Code": 200,
            "drinks": drinks_detail
        })
    except:
        abort(422)

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get(recipe, None)

        if not title or recipe:
            abort(404)

        add_drink = Drink(title=title, recipe=json.dumps(recipe))
        add_drink.insert()
        drinks = Drink.query.all()
        post_drink = [drink.long() for drink in drinks]

        return({
            "success": True,
            "status Code": 200,
            "drinks": post_drink
        })

    except:
        abort(422)

'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get(recipe, None)
        drink = Drink.query.folter(Drink.id==drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.title =title
        drink.recipe= json.dumps(recipe)
        drink.update()

        drinks = Drink.query.all()
        updated_drinks = [drink.long() for drink in drinks]

        return({
            "success": True,
            "status Code": 200, 
            "drinks": updated_drinks
        })
    except:
        abort(422)

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()

        return({
            "success": True, 
            "status Code": 200,
            "delete": drink_id
        })
    except:
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method Not Allowed"
        }), 405

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code