# Generated by Django 5.2 on 2025-04-17 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="date_from",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата начала акции"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="date_to",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата окончания акции"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sale_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Цена со скидкой",
            ),
        ),
    ]
