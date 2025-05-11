# products/fixtures/initial_data.py
import os
from datetime import datetime, timedelta
from django.core.files import File
from django.db import transaction
from product.models import Category, Product, Review, Specification, Banner


def create_initial_data():
    with transaction.atomic():
        # Создаем категории
        electronics = Category.objects.create(
            name="Electronics",
            is_featured=True
        )

        computers = Category.objects.create(
            name="Computers",
            parent=electronics,
            is_featured=True
        )

        video_cards = Category.objects.create(
            name="Video Cards",
            parent=computers,
            is_featured=False
        )

        # Создаем продукты
        product1 = Product.objects.create(
            name="NVIDIA GeForce RTX 4090",
            description="High-end video card",
            fullDescription="NVIDIA GeForce RTX 4090 is the ultimate GeForce GPU. It brings a quantum leap in performance, efficiency, and AI-powered graphics.",
            price=1599.99,
            count=10,
            free_delivery=True,
            rating=4.8,
            is_limited=True,
            sort_index=100
        )
        product1.categories.add(video_cards)

        product2 = Product.objects.create(
            name="AMD Radeon RX 7900 XTX",
            description="High-performance video card",
            fullDescription="AMD Radeon RX 7900 XTX graphics card, with 24GB GDDR6 memory, AMD RDNA 3 architecture",
            price=999.99,
            count=15,
            free_delivery=True,
            rating=4.6,
            sort_index=90
        )
        product2.categories.add(video_cards)

        image_paths = [
            "media/products/fab7087cf712eab8bab164ed06a7c31e_5P2TFvV.jpg",
            "media/products/fab7087cf712eab8bab164ed06a7c31e_5P2TFvV.jpg"
        ]

        for i, path in enumerate(image_paths):
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    if i == 0:
                        product1.image.save(os.path.basename(path), File(f))
                    else:
                        product2.image.save(os.path.basename(path), File(f))


        Review.objects.create(
            product=product1,
            author="Annoying Orange",
            email="no-reply@mail.ru",
            text="Great performance but runs hot",
            rate=4,
            created_at=datetime(2023, 5, 5, 12, 12)
        )

        Review.objects.create(
            product=product2,
            author="Happy Customer",
            email="customer@example.com",
            text="Excellent price/performance ratio",
            rate=5,
            created_at=datetime(2023, 6, 1, 14, 30)
        )


        Specification.objects.create(
            product=product1,
            name="Memory",
            value="24GB GDDR6X"
        )

        Specification.objects.create(
            product=product1,
            name="Interface",
            value="PCIe 4.0"
        )

        Specification.objects.create(
            product=product2,
            name="Memory",
            value="24GB GDDR6"
        )

        # Создаем баннеры
        Banner.objects.create(
            title="Summer Sale",
            description="Up to 50% off on selected items",
            image="banners/summer_sale.jpg",
            link="/sale",
            is_active=True
        )

        today = datetime.now().date()
        product1.sale_price = 1399.99
        product1.date_from = today
        product1.date_to = today + timedelta(days=14)
        product1.save()

        product2.sale_price = 899.99
        product2.date_from = today
        product2.date_to = today + timedelta(days=7)
        product2.save()

        print("Initial data created successfully!")


if __name__ == "__main__":
    create_initial_data()