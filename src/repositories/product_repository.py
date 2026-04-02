from sqlalchemy.orm import Session
from src.models import Product

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_product(self, name: str, price: int, production_time: int) -> Product:
        new_product = Product(name=name, price=price, production_time=production_time, status=True)
        self.session.add(new_product)
        self.session.commit()
        self.session.refresh(new_product)
        return new_product

    def check_product(self, id_product: int) -> Product:
        return self.session.query(Product).filter(Product.id_product == id_product).first()

    def list_active_products(self):
        return self.session.query(Product).filter(Product.status == True).all()
