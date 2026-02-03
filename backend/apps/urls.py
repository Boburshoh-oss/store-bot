from django.urls import path, include

urlpatterns = [
    # path("dashboard/", include("apps.dashboard.urls")),
    path("products/", include("apps.products.urls")),
    path("inventory/", include("apps.inventory.urls")),
]
