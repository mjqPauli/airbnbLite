from flask import Flask, Response, request, jsonify, render_template, make_response, flash 
from flask_pymongo import pymongo
from bson.objectid import ObjectId
from database import DatabaseConnection

app = Flask(__name__)
db = DatabaseConnection()
app.secret_key = "airbnblite"

@app.route('/login', methods = ["GET"])
def loginForm():
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
        return render_template("mode.html")
    else:
        return Response("Username and password mismatch!", status=200, content_type='text/html')
        
@app.route('/home', methods = ["GET"])
def mode():
    return render_template("mode.html")



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
        "price": request.form["price"]
    }
    db.insert("properties", document)
    return Response("Property successfully added", status=200, content_type="text/html")

@app.route('/removeProperty', methods = ['POST'])
def deleteOne():
    document = {
        "id" : request.form["property_id"]
    }
    db.removeRented("properties", {"_id" : ObjectId(document["id"])})
    return Response("Property successfully rented", status=200, content_type="text/html")

@app.route('/properties', methods = ['GET'])
def getProperties():
    properties = db.findMany("properties", {})
    return render_template("properties.html", properties=properties)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
    