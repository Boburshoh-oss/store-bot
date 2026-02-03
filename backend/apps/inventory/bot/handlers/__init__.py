from .common import start_handler, help_handler, list_handler, cancel_handler
from .warehouse import (
    add_product_handler,
    give_order_handler,
    orders_handler,
    history_handler,
    categories_handler,
    products_handler,
)
from .requester import order_handler, my_orders_handler
from .admin import users_handler, set_role_handler

__all__ = [
    # Common
    "start_handler",
    "help_handler",
    "list_handler",
    "cancel_handler",
    # Warehouse
    "add_product_handler",
    "give_order_handler",
    "orders_handler",
    "history_handler",
    "categories_handler",
    "products_handler",
    # Requester
    "order_handler",
    "my_orders_handler",
    # Admin
    "users_handler",
    "set_role_handler",
]
