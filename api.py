#!/usr/bin/python
import sqlite3, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''DROP TABLE recipes''')
        conn.execute('''
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                title VARCHAR(100) NOT NULL,
                making_time VARCHAR(100) NOT NULL,
                serves VARCHAR(100) NOT NULL,
                ingredients VARCHAR(300) NOT NULL,
                cost INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime'))
            );
        ''')

        conn.commit()
        print("Recipes table created successfully")
    except:
        print("Recipes table creation failed - Maybe table")
    finally:
        conn.close()


def insert_recipe(recipe):
    inserted_recipe = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        if recipe['created_at'] and recipe['updated_at']:
            cur.execute("INSERT INTO recipes (title, making_time, serves, ingredients, cost, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (recipe['title'], recipe['making_time'], recipe['serves'], recipe['ingredients'], recipe['cost'], recipe['created_at'], recipe['updated_at']))
        else:
            cur.execute("INSERT INTO recipes (title, making_time, serves, ingredients, cost) VALUES (?, ?, ?, ?, ?)", (recipe['title'], recipe['making_time'], recipe['serves'], recipe['ingredients'], recipe['cost']))
            
        conn.commit()
        inserted_recipe = get_recipe_by_id(cur.lastrowid)
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_recipe


def get_recipes():
    recipes = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM recipes;")
        rows = cur.fetchall()
        print(rows)
        # convert row objects to dictionary
        for i in rows:
            recipe = {}
            recipe["id"] = i["id"]
            recipe["title"] = i["title"]
            recipe["making_time"] = i["making_time"]
            recipe["serves"] = i["serves"]
            recipe["ingredients"] = i["ingredients"]
            recipe["cost"] = i["cost"]
            recipe["created_at"] = i["created_at"]
            recipe["updated_at"] = i["updated_at"]
            
            recipes.append(recipe)

    except:
        recipes = []

    return recipes


def get_recipe_by_id(id):
    recipe = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM recipes WHERE id = ?", (id,))
        row = cur.fetchone()

        # convert row object to dictionary
        recipe["id"] = row["id"]
        recipe["title"] = row["title"]
        recipe["making_time"] = row["making_time"]
        recipe["serves"] = row["serves"]
        recipe["ingredients"] = row["ingredients"]
        recipe["cost"] = row["cost"]
    except:
        recipe = {}

    return recipe


def update_recipe(recipe):
    updated_recipe = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE recipes SET title = ?, making_time = ?, serves = ?, ingredients = ?, cost = ?, updated_at = " + datetime.now + " WHERE id =?", (recipe["title"], recipe["making_time"], recipe["serves"], recipe["ingredients"], recipe["cost"], recipe["id"],))
        conn.commit()
        #return the recipe
        updated_recipe = get_recipe_by_id(recipe["id"])

    except:
        conn.rollback()
        updated_recipe = {}
    finally:
        conn.close()

    return updated_recipe


def delete_recipe(id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from recipes WHERE id = ?", (id,))
        conn.commit()
        message["status"] = "recipe deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete recipe"
    finally:
        conn.close()

    return message


recipes = []

recipe1 = {
    "title": "Chicken Curry",
    "making_time": "45 minutes",
    "serves": "4 people",
    "ingredients": "onion, chicken, seasoning",
    "cost": "1000",
    "created_at": "2016-01-10 12:10:12",
    "updated_at": "2016-01-10 12:10:12"
}

recipe2 = {
    "title": "Rice Omelette",
    "making_time": "20 min",
    "serves": "2 people",
    "ingredients": "onion, egg, seasoning, soy sauce",
    "cost": "700",
    "created_at": "2016-01-11 13:10:12",
    "updated_at": "2016-01-11 13:10:12"
}


recipes.append(recipe1)
recipes.append(recipe2)

create_db_table()

for i in recipes:
    print(insert_recipe(i))



@app.route('/recipes', methods=['GET'])
def api_get_recipes():
    recipes = get_recipes()
    print(recipes)
    return jsonify(recipes)

@app.route('/recipes/<id>', methods=['GET'])
def api_get_recipe(id):
    return jsonify(get_recipe_by_id(id))

@app.route('/recipes',  methods = ['POST'])
def api_add_recipe():
    recipe = request.get_json()
    return jsonify(insert_recipe(recipe))

@app.route('/recipes',  methods = ['PUT'])
def api_update_recipe():
    recipe = request.get_json()
    return jsonify(update_recipe(recipe))

@app.route('/recipes/<id>',  methods = ['DELETE'])
def api_delete_recipe(id):
    return jsonify(delete_recipe(id))


if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    app.run()