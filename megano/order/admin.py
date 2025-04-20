from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'item_cost']
    fields = ['product', 'quantity', 'price', 'item_cost']

    def item_cost(self, instance):
        if instance.quantity is None or instance.price is None:
            return 0
        return instance.quantity * instance.price

    item_cost.short_description = 'Стоимость'


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_date', 'card_number_masked']
    fields = ['payment_date', 'card_number_masked', 'card_name', 'card_exp_month',
              'card_exp_year', 'amount', 'status']

    def card_number_masked(self, instance):
        return f"****-****-****-{instance.card_number[-4:]}" if instance.card_number else "N/A"

    card_number_masked.short_description = 'Номер карты'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'full_name', 'email', 'total_cost',
                    'delivery_type', 'payment_type', 'status', 'order_actions']
    list_filter = ['status', 'delivery_type', 'payment_type', 'created_at']
    search_fields = ['id', 'full_name', 'email', 'phone', 'city']
    readonly_fields = ['created_at', 'order_summary']
    fieldsets = [
        ('Основная информация', {
            'fields': ['created_at', 'status', 'user']
        }),
        ('Данные клиента', {
            'fields': ['full_name', 'email', 'phone']
        }),
        ('Доставка и оплата', {
            'fields': ['delivery_type', 'payment_type', 'total_cost']
        }),
        ('Адрес', {
            'fields': ['city', 'address']
        }),
        ('Дополнительно', {
            'fields': ['order_summary']
        })
    ]
    inlines = [OrderItemInline, PaymentInline]

    def order_summary(self, instance):
        items = instance.products.all()
        return format_html(
            "<h4>Итого: {} ₽</h4>"
            "<p>Товаров: {}</p>"
            "<p>Способ доставки: {}</p>"
            "<p>Способ оплаты: {}</p>",
            instance.total_cost,
            items.count(),
            instance.get_delivery_type_display(),
            instance.get_payment_type_display()
        )

    order_summary.short_description = 'Сводка заказа'

    def order_actions(self, obj):
        if obj.pk:
            return format_html(
                '<div class="order-actions">'
                '<a class="button" href="{}">Изменить</a>&nbsp;'
                '<a class="button" href="{}">История</a>'
                '</div>',
                f'{obj.pk}/change/',
                f'{obj.pk}/history/'
            )
        return ""

    order_actions.short_description = 'Действия'

    class Media:
        css = {
            'all': ['admin/css/orders.css']
        }


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'payment_date', 'card_number_masked', 'amount', 'status']
    list_filter = ['status', 'payment_date']
    readonly_fields = ['payment_date', 'card_number_masked']

    def card_number_masked(self, obj):
        return f"****-****-****-{obj.card_number[-4:]}" if obj.card_number else "N/A"

    card_number_masked.short_description = 'Номер карты'

    def order_id(self, obj):
        return obj.order.id

    order_id.short_description = 'ID заказа'