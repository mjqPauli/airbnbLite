from flask import Flask, Response, request, jsonify, render_template, make_response, flash, session, redirect, url_for 
from flask_pymongo import pymongo
from bson.objectid import ObjectId
from database import DatabaseConnection

import datetime

app = Flask(__name__)
db = DatabaseConnection()
app.secret_key = "airbnblite"


def greeting():
    name = request.cookies.get("signed_in")
    hourTime = datetime.datetime.now().time().hour
    greeting = ""
    if not name:
        return Response(status=404)
    if hourTime < 12:
        greeting = "Good Morning"
    elif hourTime >= 12 and hourTime < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    response = greeting + ", " + name
    return response

@app.route('/login', methods = ["GET"])
def loginForm():
    if request.cookies.get("signed_in"):
        return render_template("mode.html", GreetingMessage=greeting())
    return render_template('login.html')

@app.route('/login', methods = ["POST"])
def login():
    document = {
        "username": request.form["username"],
        "password": request.form["password"]
    }
    user = db.findOne("users", {"username" : document["username"]})
    if user == None:
        return Response("User doesn't exist!", status=200, content_type='text/html')
    if user["password"] == document["password"]:
        resp = make_response(redirect("/home"))
        resp.set_cookie("signed_in", request.form["username"])
        return resp
    else:
        return Response("Username and password mismatch!", status=200, content_type='text/html')
        
@app.route('/home', methods = ["GET"])
def mode():
    
    return render_template("mode.html", GreetingMessage=greeting())

@app.route('/signup', methods = ["GET"])
def signupForm():
    return render_template('signup.html')

@app.route('/signup', methods = ["POST"])
def signup():
    document = {
        "username": request.form["username"],
        "password": request.form["password"]
    }
    user = db.findOne("users", {"username" : document["username"]})
    if user == None:
        db.insert('users', document)
        return Response("Signed up successfully!", status=200, content_type='text/html')
    if document["username"] == user["username"]:
        return Response("Username already exists!", status=200, content_type='text/html')
   

@app.route('/addNewProperty', methods = ['GET'])
def getPropertyForm():
    return render_template('getPropertyForm.html')

@app.route('/addNewProperty', methods = ['POST'])
def addProperty():
    document = {
        "name": request.form["name"],
        "propertyType": request.form["type"],
        "price": request.form["price"],
        "rentor": "",
        "host": request.cookies.get("signed_in")
    }
    db.insert("properties", document)
    return Response("Property successfully added", status=200, content_type="text/html")

@app.route('/rentProperty', methods = ['POST'])
def rent():
    document = {
        "id" : request.form["property_id"]
    }
    property_rent = db.findOne("properties", {"_id" : ObjectId(document["id"])})
    db.removeRented("properties", {"_id" : ObjectId(document["id"])})
    property_rent["rentor"] = request.cookies.get("signed_in")
    db.insert("properties", property_rent)
    return Response("Property successfully rented", status=200, content_type="text/html")

@app.route('/checkout', methods = ['POST'])
def checkOut():
    document = {
        "id" : request.form["property_id"]
    }
    property_rent = db.findOne("properties", {"_id" : ObjectId(document["id"])})
    db.removeRented("properties", {"_id" : ObjectId(document["id"])})
    property_rent["rentor"] = ''
    db.insert("properties", property_rent)
    return Response('You have checked out!', status=200, content_type="text/html")

@app.route('/removeProperty', methods = ['POST'])
def deleteOne():
    document = {
        "id" : request.form["property_id"]
    }
    db.removeRented("properties", {"_id" : ObjectId(document["id"])})
    return Response("Property successfully removed", status=200, content_type="text/html")

@app.route('/properties', methods = ['GET'])
def getProperties():
    properties = db.findMany("properties", {"rentor": ""})
    return render_template("properties.html", properties=properties)

@app.route('/account', methods = ['GET'])
def getAccount():
    properties_host = db.findMany("properties", {"host": request.cookies.get("signed_in")})
    properties_rent = db.findMany("properties", {"rentor": request.cookies.get("signed_in")})
    name = request.cookies.get("signed_in")
    return render_template("account.html", name=name, properties_host=properties_host, properties_rent=properties_rent)

@app.route('/logout', methods = ['GET'])
def logout():
    resp = make_response(render_template("login.html"))
    resp.set_cookie("signed_in", request.cookies.get("signed_in"), max_age=0)
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
    