# We import the function from our cook.py file
from cook import make_pizza

print("--- RESTAURANT IS OPEN ---")
print("Customer: I'd like a Mushroom pizza, please.")

# We use the imported function
order = make_pizza("Mushroom")

print(f"Waiter: Here is your {order}, enjoy!")
print("--------------------------")
