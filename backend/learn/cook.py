def make_pizza(topping):
    print(f"Cooking a delicious {topping} pizza!")
    return f"{topping} pizza"

# --- Standalone Test ---
# This block ONLY runs if you execute THIS file directly.
# It does NOT run if someone imports this file.
if __name__ == "__main__":
    print("--- COOK IS TESTING IN THE KITCHEN ---")
    my_pizza = make_pizza("Pepperoni")
    print(f"Taste test result: {my_pizza} is perfect!")
    print("--------------------------------------")
