from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'onsie_secret_key' 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    impact = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref='reviews')


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
    search = request.args.get('search', '').lower()

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if sort_by == 'price':
        query = query.order_by(Product.price)
    elif sort_by == 'impact':
        query = query.order_by(Product.impact)
    else:
        query = query.order_by(Product.name)

    products = query.all()

    return render_template(
        'index.html',
        products=products,
        basket_count=basket_count()
    )

@app.route('/item/<int:itemId>', methods=["GET", "POST"])
def singleProductPage(itemId):
    product = Product.query.get_or_404(itemId)

    if request.method == "POST":

        action = request.form.get("action")

        #REVIEW
        if action == "review":
            review_text = request.form.get("review", "").strip()
            rating = request.form.get("rating", "").strip()

        if review_text and rating:
            new_review = Review(
                product_id=product.id,
                username=session.get("user", "Anonymous"),
                text=review_text,
                rating=int(rating)
            )

            db.session.add(new_review)
            db.session.commit()

      
        

        #ADD TO BASKET
        elif action == "basket":
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

    reviews = Review.query.filter_by(product_id=product.id).all()

    return render_template(
        'SingleProduct.html', 
        product = product, 
        reviews = reviews, 
        basket_count = basket_count()
        )

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
    product = Product.query.get_or_404(itemId)
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

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "admin" and password == "password123":
            session['user'] = username
            return redirect(url_for('galleryPage'))
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error)

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('galleryPage'))


@app.route('/clear_reviews/<int:itemId>', methods=["POST"])
def clear_reviews_item(itemId):
    Review.query.filter_by(product_id=itemId).delete()
    db.session.commit()
    return redirect(url_for("singleProductPage", itemId=itemId))

@app.route('/product_info/<int:itemId>')
def product_info(itemId):
    product = Product.query.get_or_404(itemId)

    return {
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "impact": product.impact,
        "image": product.image
    }

if __name__ == '__main__':
    app.run(debug=True)

