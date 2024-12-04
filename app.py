from flask import Flask, render_template, request
import csv
import random

app = Flask(__name__)

def load_meal_database(csv_filename):
    """Load meal database from a CSV file."""
    meal_database = []
    try:
        with open(csv_filename, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert diet, allergens, and health_conditions to lowercase lists
                row["diet"] = row["diet"].lower()
                row["allergens"] = row["allergens"].lower().split(",")
                row["health_conditions"] = row["health_conditions"].lower().split(",")
                meal_database.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_filename} not found.")
    except Exception as e:
        print(f"Error loading database: {e}")
    
    return meal_database

def get_random_meal(meal_type, dietary_restrictions, allergies, health_conditions, meal_database):
    """Filter and randomly select a meal based on preferences and conditions."""
    filtered_meals = [
        meal for meal in meal_database
        if meal["meal_type"] == meal_type
        and (not dietary_restrictions or meal["diet"] in dietary_restrictions)
        and all(allergy not in meal["allergens"] for allergy in allergies)
        and all(condition not in meal["health_conditions"] for condition in health_conditions)
    ]
    
    # Handle no valid meal found
    if not filtered_meals:
        return "No suitable meal found"
    
    # Randomly select a meal
    return random.choice(filtered_meals)["name"]

@app.route("/", methods=["GET", "POST"])
def index():
    meal_plan = None
    if request.method == "POST":
        dietary_restrictions = request.form.get("dietary_restrictions", "").lower().strip()
        allergies = request.form.getlist("allergies")
        health_conditions = request.form.getlist("health_conditions")

        # Convert dietary_restrictions to a list for compatibility
        dietary_restrictions = [dietary_restrictions] if dietary_restrictions else []

        # Remove "none" if selected
        allergies = [allergy.lower() for allergy in allergies if allergy.lower() != "none"]
        health_conditions = [condition.lower() for condition in health_conditions if condition.lower() != "none"]

        # Load the meal database
        meal_database = load_meal_database("meal_database.csv")

        # Check if meals are available
        if meal_database:
            # Generate the weekly meal plan
            meal_plan = {
                day: {
                    "breakfast": get_random_meal("breakfast", dietary_restrictions, allergies, health_conditions, meal_database),
                    "lunch": get_random_meal("lunch", dietary_restrictions, allergies, health_conditions, meal_database),
                    "dinner": get_random_meal("dinner", dietary_restrictions, allergies, health_conditions, meal_database),
                    "snack": get_random_meal("snack", dietary_restrictions, allergies, health_conditions, meal_database),
                }
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            }
        else:
            meal_plan = {"error": "Meal database is unavailable or empty."}

    return render_template("index.html", meal_plan=meal_plan)

if __name__ == "__main__":
    app.run(debug=True)
