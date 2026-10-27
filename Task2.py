
# Integrated E-Commerce Order Processing and Reconciliation

# Product: [Product ID, Name, Price, Stock]
inventory = [
    [101, "Laptop", 50000.0, 10],
    [102, "Mobile", 20000.0, 20],
    [103, "Headphones", 2000.0, 30],
    [104, "Keyboard", 1500.0, 25]
]

# Order: [Order ID, Product ID, Quantity, Discount, Status]
orders = []

# Dispatch: [Order ID, Quantity Dispatched]
dispatches = []

# Return: [Order ID, Quantity Returned]
returns = []

order_counter = 1001


def find_product(product_id):
    for product in inventory:
        if product[0] == product_id:
            return product
    return None


def find_order(order_id):
    for order in orders:
        if order[0] == order_id:
            return order
    return None


def display_inventory():
    print("\n========== INVENTORY ==========")
    print("ID\tProduct\t\tPrice\tStock")

    for product_id, name, price, stock in inventory:
        print(f"{product_id}\t{name:<15}\t{price:.2f}\t{stock}")

    print("================================")


def place_order():
    global order_counter

    display_inventory()

    try:
        product_id = int(input("Enter product ID: "))
        quantity = int(input("Enter order quantity: "))
    except ValueError:
        print("Invalid numeric input!")
        return

    product = find_product(product_id)

    if product is None:
        print("Product not found!")
        return

    if quantity <= 0:
        print("Quantity must be positive!")
        return

    if quantity > product[3]:
        print("Insufficient stock!")
        return

    price = product[2]
    subtotal = price * quantity

    if subtotal >= 50000:
        discount_rate = 0.10
    elif subtotal >= 20000:
        discount_rate = 0.05
    else:
        discount_rate = 0.0

    discount = subtotal * discount_rate
    net_amount = subtotal - discount

    # Reserve stock when the order is placed.
    product[3] -= quantity

    orders.append([
        order_counter, product_id, quantity,
        discount, "PLACED"
    ])

    print("\nOrder placed successfully!")
    print("Order ID:", order_counter)
    print("Subtotal: Rs.", round(subtotal, 2))
    print("Discount: Rs.", round(discount, 2))
    print("Net amount: Rs.", round(net_amount, 2))

    order_counter += 1


def dispatch_order():
    try:
        order_id = int(input("Enter order ID to dispatch: "))
    except ValueError:
        print("Invalid order ID!")
        return

    order = find_order(order_id)

    if order is None:
        print("Order not found!")
        return

    if order[4] != "PLACED":
        print("Only placed orders can be dispatched!")
        return

    order[4] = "DISPATCHED"
    dispatches.append([order_id, order[2]])

    print("Order", order_id, "dispatched successfully.")


def return_order():
    try:
        order_id = int(input("Enter order ID for return: "))
        quantity = int(input("Enter quantity to return: "))
    except ValueError:
        print("Invalid numeric input!")
        return

    order = find_order(order_id)

    if order is None:
        print("Order not found!")
        return

    if order[4] not in ("DISPATCHED", "PARTIALLY RETURNED"):
        print("Only dispatched orders can be returned!")
        return

    already_returned = 0

    for return_id, returned_quantity in returns:
        if return_id == order_id:
            already_returned += returned_quantity

    remaining = order[2] - already_returned

    if quantity <= 0 or quantity > remaining:
        print("Invalid return quantity!")
        return

    returns.append([order_id, quantity])

    # Restore returned units to inventory.
    product = find_product(order[1])
    product[3] += quantity

    if quantity + already_returned == order[2]:
        order[4] = "RETURNED"
    else:
        order[4] = "PARTIALLY RETURNED"

    print("Return recorded successfully.")
    print("Stock updated:", product[3])


def calculate_order_amount(order):
    order_id, product_id, quantity, discount, status = order
    product = find_product(product_id)

    # Calculate total amount after discount.
    subtotal = product[2] * quantity
    net_amount = subtotal - discount
    return net_amount


def revenue_report():
    gross_sales = 0.0
    total_discounts = 0.0
    refunds = 0.0
    total_returns = 0

    for order_id, product_id, quantity, discount, status in orders:
        product = find_product(product_id)
        gross_sales += product[2] * quantity
        total_discounts += discount

    for order_id, returned_quantity in returns:
        order = find_order(order_id)
        product = find_product(order[1])

        # Refund is proportional to returned units.
        original_quantity = order[2]
        unit_net_price = (
            product[2] -
            (order[3] / original_quantity)
        )

        refunds += unit_net_price * returned_quantity
        total_returns += returned_quantity

    net_revenue = gross_sales - total_discounts - refunds

    print("\n========== REVENUE REPORT ==========")
    print("Gross sales: Rs.", round(gross_sales, 2))
    print("Discounts: Rs.", round(total_discounts, 2))
    print("Refunds: Rs.", round(refunds, 2))
    print("Units returned:", total_returns)
    print("Net revenue: Rs.", round(net_revenue, 2))
    print("====================================")


def reconcile_orders():
    print("\n========== RECONCILIATION ==========")
    discrepancies = 0

    for order_id, product_id, quantity, discount, status in orders:
        dispatched_quantity = 0
        returned_quantity = 0

        for dispatch_id, dispatch_qty in dispatches:
            if dispatch_id == order_id:
                dispatched_quantity += dispatch_qty

        for return_id, return_qty in returns:
            if return_id == order_id:
                returned_quantity += return_qty

        if dispatched_quantity > quantity:
            print("ERROR: Over-dispatch for order", order_id)
            discrepancies += 1

        if returned_quantity > dispatched_quantity:
            print("ERROR: Excess returns for order", order_id)
            discrepancies += 1

        if status == "DISPATCHED" and dispatched_quantity != quantity:
            print("WARNING: Dispatch mismatch for order", order_id)
            discrepancies += 1

        if returned_quantity > 0 and returned_quantity <= dispatched_quantity:
            print(
                "Order", order_id,
                "- Dispatched:", dispatched_quantity,
                "| Returned:", returned_quantity
            )

    if discrepancies == 0:
        print("No order/dispatch discrepancies detected.")

    print("Discrepancies found:", discrepancies)
    print("====================================")


def inventory_reconciliation():
    print("\n========== INVENTORY RECONCILIATION ==========")

    for product_id, name, price, stock in inventory:
        ordered = 0
        dispatched = 0
        returned = 0

        for order_id, pid, quantity, discount, status in orders:
            if pid == product_id:
                ordered += quantity

        for dispatch_id, quantity in dispatches:
            order = find_order(dispatch_id)
            if order is not None and order[1] == product_id:
                dispatched += quantity

        for return_id, quantity in returns:
            order = find_order(return_id)
            if order is not None and order[1] == product_id:
                returned += quantity

        # Expected stock based on order reservation and returns.
        initial_stock = next(
            item[1] for item in [
                (101, 10), (102, 20), (103, 30), (104, 25)
            ] if item[0] == product_id
        )

        expected_stock = initial_stock - ordered + returned

        print("\nProduct:", name)
        print("Initial stock:", initial_stock)
        print("Ordered:", ordered)
        print("Dispatched:", dispatched)
        print("Returned:", returned)
        print("Actual stock:", stock)
        print("Expected stock:", expected_stock)

        if stock != expected_stock:
            print("DISCREPANCY: Stock mismatch!")
        else:
            print("Stock reconciled successfully.")

    print("\n==============================================")


def final_summary():
    print("\n========== FINAL INVENTORY SUMMARY ==========")

    total_products = len(inventory)
    total_units = 0
    inventory_value = 0.0
    low_stock = []

    for product_id, name, price, stock in inventory:
        total_units += stock
        inventory_value += price * stock

        if stock < 5:
            low_stock.append(name)

        print(
            f"{product_id} | {name:<15} | "
            f"Stock: {stock:<4} | Value: Rs. {price * stock:.2f}"
        )

    print("\nTotal product types:", total_products)
    print("Total units in stock:", total_units)
    print("Inventory value: Rs.", round(inventory_value, 2))

    if low_stock:
        print("Low-stock products:", ", ".join(low_stock))
    else:
        print("No low-stock products.")

    print("Total orders:", len(orders))
    print("Total dispatch records:", len(dispatches))
    print("Total return records:", len(returns))
    print("=============================================")


def main():
    while True:
        print("\n===== E-COMMERCE ORDER MANAGEMENT =====")
        print("1. Display Inventory")
        print("2. Place Order")
        print("3. Dispatch Order")
        print("4. Process Return")
        print("5. Revenue Report")
        print("6. Reconcile Orders")
        print("7. Reconcile Inventory")
        print("8. Final Inventory Summary")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_inventory()
        elif choice == "2":
            place_order()
        elif choice == "3":
            dispatch_order()
        elif choice == "4":
            return_order()
        elif choice == "5":
            revenue_report()
        elif choice == "6":
            reconcile_orders()
        elif choice == "7":
            inventory_reconciliation()
        elif choice == "8":
            final_summary()
        elif choice == "0":
            print("Exiting E-Commerce Management System.")
            break
        else:
            print("Invalid choice! Try again.")


main()
