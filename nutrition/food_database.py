"""
Renal Nutrition Food Database — RenalOne
Nutrient data per 100g unless otherwise noted.
Sources: USDA, Renal Dietitians Association guidelines, KDIGO Nutrition 2020.
"""

FOOD_DB = {
    # ---- Grains & Staples ----
    "white rice (cooked)": {
        "potassium_mg": 29, "sodium_mg": 1, "phosphorus_mg": 43, "protein_g": 2.7, "calories": 130, "fluid_ml": 0,
        "group": "Grains",
    },
    "white bread": {
        "potassium_mg": 100, "sodium_mg": 490, "phosphorus_mg": 96, "protein_g": 8.0, "calories": 265, "fluid_ml": 0,
        "group": "Grains",
    },
    "chapati / roti": {
        "potassium_mg": 135, "sodium_mg": 290, "phosphorus_mg": 110, "protein_g": 7.5, "calories": 300, "fluid_ml": 0,
        "group": "Grains",
    },
    "oats (cooked)": {
        "potassium_mg": 61, "sodium_mg": 49, "phosphorus_mg": 90, "protein_g": 2.5, "calories": 71, "fluid_ml": 0,
        "group": "Grains",
    },
    "pasta (cooked)": {
        "potassium_mg": 44, "sodium_mg": 1, "phosphorus_mg": 58, "protein_g": 5.0, "calories": 158, "fluid_ml": 0,
        "group": "Grains",
    },
    # ---- Vegetables ----
    "cabbage (raw)": {
        "potassium_mg": 170, "sodium_mg": 18, "phosphorus_mg": 26, "protein_g": 1.3, "calories": 25, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "cauliflower (cooked)": {
        "potassium_mg": 152, "sodium_mg": 15, "phosphorus_mg": 32, "protein_g": 1.9, "calories": 23, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "green beans (cooked)": {
        "potassium_mg": 209, "sodium_mg": 1, "phosphorus_mg": 38, "protein_g": 1.8, "calories": 35, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "potato (boiled, no skin)": {
        "potassium_mg": 379, "sodium_mg": 4, "phosphorus_mg": 44, "protein_g": 1.7, "calories": 86, "fluid_ml": 0,
        "group": "Vegetables",
        "note": "Leaching (double-boiling) reduces potassium by ~50%",
    },
    "spinach (cooked)": {
        "potassium_mg": 466, "sodium_mg": 79, "phosphorus_mg": 56, "protein_g": 2.9, "calories": 23, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "tomato": {
        "potassium_mg": 237, "sodium_mg": 5, "phosphorus_mg": 24, "protein_g": 0.9, "calories": 18, "fluid_ml": 94,
        "group": "Vegetables",
    },
    "onion": {
        "potassium_mg": 146, "sodium_mg": 4, "phosphorus_mg": 29, "protein_g": 1.1, "calories": 40, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "carrot (raw)": {
        "potassium_mg": 320, "sodium_mg": 69, "phosphorus_mg": 35, "protein_g": 0.9, "calories": 41, "fluid_ml": 0,
        "group": "Vegetables",
    },
    "capsicum / bell pepper": {
        "potassium_mg": 211, "sodium_mg": 4, "phosphorus_mg": 26, "protein_g": 1.0, "calories": 31, "fluid_ml": 0,
        "group": "Vegetables",
    },
    # ---- Fruits ----
    "apple": {
        "potassium_mg": 107, "sodium_mg": 1, "phosphorus_mg": 11, "protein_g": 0.3, "calories": 52, "fluid_ml": 86,
        "group": "Fruits",
    },
    "grapes": {
        "potassium_mg": 191, "sodium_mg": 2, "phosphorus_mg": 20, "protein_g": 0.7, "calories": 69, "fluid_ml": 81,
        "group": "Fruits",
    },
    "watermelon": {
        "potassium_mg": 112, "sodium_mg": 1, "phosphorus_mg": 11, "protein_g": 0.6, "calories": 30, "fluid_ml": 91,
        "group": "Fruits",
    },
    "banana": {
        "potassium_mg": 358, "sodium_mg": 1, "phosphorus_mg": 22, "protein_g": 1.1, "calories": 89, "fluid_ml": 75,
        "group": "Fruits",
    },
    "orange": {
        "potassium_mg": 181, "sodium_mg": 0, "phosphorus_mg": 14, "protein_g": 0.9, "calories": 47, "fluid_ml": 87,
        "group": "Fruits",
    },
    "mango": {
        "potassium_mg": 168, "sodium_mg": 1, "phosphorus_mg": 14, "protein_g": 0.8, "calories": 60, "fluid_ml": 84,
        "group": "Fruits",
    },
    # ---- Proteins ----
    "egg (whole, boiled)": {
        "potassium_mg": 126, "sodium_mg": 124, "phosphorus_mg": 172, "protein_g": 13.0, "calories": 155, "fluid_ml": 0,
        "group": "Proteins",
    },
    "egg white": {
        "potassium_mg": 163, "sodium_mg": 166, "phosphorus_mg": 15, "protein_g": 10.9, "calories": 52, "fluid_ml": 0,
        "group": "Proteins",
    },
    "chicken breast (cooked)": {
        "potassium_mg": 256, "sodium_mg": 74, "phosphorus_mg": 220, "protein_g": 31.0, "calories": 165, "fluid_ml": 0,
        "group": "Proteins",
    },
    "fish (tilapia, cooked)": {
        "potassium_mg": 302, "sodium_mg": 56, "phosphorus_mg": 204, "protein_g": 26.0, "calories": 128, "fluid_ml": 0,
        "group": "Proteins",
    },
    "tofu (firm)": {
        "potassium_mg": 121, "sodium_mg": 7, "phosphorus_mg": 97, "protein_g": 8.1, "calories": 76, "fluid_ml": 0,
        "group": "Proteins",
    },
    # ---- Dairy ----
    "milk (whole)": {
        "potassium_mg": 132, "sodium_mg": 44, "phosphorus_mg": 84, "protein_g": 3.2, "calories": 61, "fluid_ml": 88,
        "group": "Dairy",
    },
    "curd / yogurt": {
        "potassium_mg": 141, "sodium_mg": 36, "phosphorus_mg": 95, "protein_g": 3.5, "calories": 59, "fluid_ml": 85,
        "group": "Dairy",
    },
    "paneer": {
        "potassium_mg": 98, "sodium_mg": 19, "phosphorus_mg": 138, "protein_g": 11.0, "calories": 265, "fluid_ml": 0,
        "group": "Dairy",
    },
    # ---- Legumes ----
    "lentils (cooked)": {
        "potassium_mg": 369, "sodium_mg": 2, "phosphorus_mg": 180, "protein_g": 9.0, "calories": 116, "fluid_ml": 0,
        "group": "Legumes",
    },
    "chickpeas (cooked)": {
        "potassium_mg": 291, "sodium_mg": 7, "phosphorus_mg": 168, "protein_g": 8.9, "calories": 164, "fluid_ml": 0,
        "group": "Legumes",
    },
    # ---- Snacks / Processed ----
    "biscuits (plain)": {
        "potassium_mg": 90, "sodium_mg": 480, "phosphorus_mg": 110, "protein_g": 5.5, "calories": 420, "fluid_ml": 0,
        "group": "Snacks",
    },
    "potato chips": {
        "potassium_mg": 1642, "sodium_mg": 525, "phosphorus_mg": 139, "protein_g": 6.6, "calories": 536, "fluid_ml": 0,
        "group": "Snacks",
    },
    "chocolate (dark)": {
        "potassium_mg": 559, "sodium_mg": 20, "phosphorus_mg": 308, "protein_g": 7.8, "calories": 546, "fluid_ml": 0,
        "group": "Snacks",
    },
    # ---- Beverages ----
    "coconut water": {
        "potassium_mg": 250, "sodium_mg": 105, "phosphorus_mg": 20, "protein_g": 0.7, "calories": 19, "fluid_ml": 95,
        "group": "Beverages",
    },
    "orange juice": {
        "potassium_mg": 200, "sodium_mg": 1, "phosphorus_mg": 17, "protein_g": 0.7, "calories": 45, "fluid_ml": 89,
        "group": "Beverages",
    },
    "coffee (black)": {
        "potassium_mg": 92, "sodium_mg": 4, "phosphorus_mg": 7, "protein_g": 0.3, "calories": 2, "fluid_ml": 98,
        "group": "Beverages",
    },
    "tea (black, no sugar)": {
        "potassium_mg": 37, "sodium_mg": 3, "phosphorus_mg": 1, "protein_g": 0.0, "calories": 1, "fluid_ml": 99,
        "group": "Beverages",
    },
}


def search_food(query: str) -> list[tuple[str, dict]]:
    """Return list of (name, data) matching the query."""
    q = query.strip().lower()
    results = []
    for name, data in FOOD_DB.items():
        if q in name or any(q in word for word in name.split()):
            results.append((name, data))
    return results


def get_all_food_names() -> list[str]:
    return sorted(FOOD_DB.keys())


def get_food_data(name: str) -> dict | None:
    return FOOD_DB.get(name.lower())
