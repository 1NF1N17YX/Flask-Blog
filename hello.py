from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")

def index():
    first_name = "John"
    stuff = "This is      Bold Text"

    favorite_pizza = ["Pepparoni", "Cheese", "Mashrooms", 41]
    return render_template("index.html", first_name=first_name, stuff=stuff, 
                           favorite_pizza=favorite_pizza)



# localhost:5000/user/nameoftheuser
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", name=name)

# Create Custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400
 
# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


'''
#filters
safe
capitalize
lower
upper
title
trim
striptags
'''
