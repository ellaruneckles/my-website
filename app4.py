from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'onsie_secret_key' 

products = [
    { 
     "id": 0,
     "name": "Shark onesie", 
     "price": 22.99, 
     "description": "A blue coloured soft shark slip on onesie for all.", 
     "image": "shark.png",
     "impact":4 },

    { "id": 1,
     "name": "Chicken onesie", 
     "price": 19.99, 
     "description": "A comedic cream coloured chicken lookalike button up onesie for all.",
      "image": "chicken.png",
       "impact":2 },

    { "id": 2,
     "name": "Bear onesie", 
     "price": 21.99, 
     "description": "A comfy brown bear lookalike zip up onesie for all.",
      "image": "bear.png",
       "impact":3 },
    
    { "id": 3,
     "name": "Dinosaur onesie", 
     "price": 20.99, 
     "description": "A green zip up soft comedic dinosaur onesie for all ",
     "image": "dinosaur.png",
      "impact":1 }
]

def get_basket():
    if 'basket' not in session:
        session['basket'] = []
    return session['basket']

def basket_count():
    basket = get_basket()
    return sum(item['quantity'] for item in basket)

@app.route('/')
def galleryPage():
    sort_by = request.args.get('sort', 'name')
    sorted_products = products[:]

    if sort_by == 'name':
        sorted_products.sort(key=lambda x: x['name'])
    elif sort_by == 'price':
        sorted_products.sort(key=lambda x: x['price'])
    elif sort_by == 'impact':
        sorted_products.sort(key=lambda x: x['impact'])

    return render_template('index.html', products=sorted_products, basket_count=basket_count())

@app.route('/item/<int:itemId>', methods=["GET", "POST"])
def singleProductPage(itemId):
    product = products[itemId]

    if request.method == "POST":
        quantity = int(request.form.get("quantity",1))
        basket = get_basket()

        found = False 
        for item in basket:
            if item['id'] == product['id']:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            basket.append({
                'id': product["id"],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity
            })
        
        session['basket'] = basket
        session.modified = True
        return redirect(url_for('basketPage'))

    return render_template('SingleProduct.html', product = product, basket_count = basket_count())

@app.route('/basket')
def basketPage():
    basket = get_basket()
    total = sum(item['price'] * item['quantity'] for item in basket)
    return render_template('basket.html', basket=basket, total=total, basket_count = basket_count())

@app.route('/remove_from_basket/<int:itemId>', methods=["POST"])
def remove_from_basket(itemId):
    basket = get_basket()
    basket = [item for item in basket if item["id"] != itemId]
    session['basket'] = basket
    session.modified = True
    return redirect(url_for('basketPage'))

@app.route('/clear_basket', methods=["POST"])
def clear_basket():
    session['basket'] = []
    session.modified = True
    return redirect(url_for('basketPage'))

@app.route('/add_to_basket/<int:itemId>', methods=["POST"])
def add_to_basket(itemId):
    product = products[itemId]
    quantity = int(request.form.get("quantity", 1))
    basket = get_basket()

    found = False
    for item in basket:
        if item['id'] == product['id']:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        basket.append({
            'id': product["id"],
            'name': product['name'],
            'price': product['price'],
            'image': product['image'],
            'quantity': quantity
        })

    session['basket'] = basket
    session.modified = True
    return redirect(url_for('basketPage'))

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        card = request.form.get("card", "").replace (" ", "").replace("-", "")

        if not name or not card or not address:
            error = "Please fill in all fields."
        elif len(card) != 16 or not card.isdigit():
            error = "Please enter a valid 16-digit card number."
        else:
            session['basket'] = []
            session.modified = True
            return render_template('success.html')

    return render_template('checkout.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)

