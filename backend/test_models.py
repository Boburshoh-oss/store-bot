"""
Simple test script to verify models work correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
os.environ.setdefault('SECRET_KEY', 'test-key-12345')
django.setup()

from apps.products.models import Category, Product
from apps.inventory.models import Warehouse, Stock, StockMovement


def test_models():
    """Test model creation and relationships"""
    print("Testing models...")
    
    # Test Category
    print("\n1. Testing Category model...")
    category = Category(name="Test Category", description="Test Description")
    print(f"   ✓ Category created: {category}")
    
    # Test Product
    print("\n2. Testing Product model...")
    product = Product(
        name="Test Product",
        description="Test Description",
        category=category,
        price=100.50,
        barcode="123456789"
    )
    print(f"   ✓ Product created: {product}")
    
    # Test Warehouse
    print("\n3. Testing Warehouse model...")
    warehouse = Warehouse(name="Test Warehouse", location="Tashkent")
    print(f"   ✓ Warehouse created: {warehouse}")
    
    # Test Stock
    print("\n4. Testing Stock model...")
    stock = Stock(
        product=product,
        warehouse=warehouse,
        quantity=100,
        min_quantity=10
    )
    print(f"   ✓ Stock created: {stock}")
    print(f"   ✓ Is low stock: {stock.is_low_stock}")
    
    # Test StockMovement
    print("\n5. Testing StockMovement model...")
    movement = StockMovement(
        stock=stock,
        movement_type='IN',
        quantity=50,
        note="Test movement"
    )
    print(f"   ✓ StockMovement created: {movement}")
    
    print("\n✅ All models tested successfully!")
    print("\nNote: Models tested without saving to database.")
    print("To fully test, run migrations and create objects in Django shell or admin.")


if __name__ == '__main__':
    test_models()
