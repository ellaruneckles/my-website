from app4 import app, db, Product, Review

with app.app_context():
    db.drop_all()
    db.create_all()

    products = [
        Product(
            name="Shark onesie",
            price=22.99,
            description="A blue coloured soft shark slip on onesie for all.",
            image="shark.png",
            impact=4
        ),
        Product(
            name="Chicken onesie",
            price=19.99,
            description="A comedic cream coloured chicken lookalike button up onesie for all.",
            image="chicken.png",
            impact=2
        ),
        Product(
            name="Bear onesie",
            price=21.99,
            description="A comfy brown bear lookalike zip up onesie for all.",
            image="bear.png",
            impact=3
        ),
        Product(
            name="Dinosaur onesie",
            price=20.99,
            description="A green zip up soft comedic dinosaur onesie for all.",
            image="dinosaur.png",
            impact=1
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    print("Database created successfully.")