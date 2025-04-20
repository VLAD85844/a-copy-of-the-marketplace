from django.contrib import admin
from django import forms
import json
from .models import Product, Category, Specification, Review
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html


class TagsAdminWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if value and isinstance(value, list):
            decoded_tags = [
                tag.encode('utf-8').decode('unicode-escape') if isinstance(tag, str) else str(tag)
                for tag in value
            ]
            value = ", ".join(decoded_tags)
        attrs = attrs or {}
        attrs.update({
            'style': 'font-family: monospace; width: 95%;',
            'rows': '3'
        })
        return super().render(name, value, attrs, renderer)


class ProductForm(forms.ModelForm):
    tags_input = forms.CharField(
        widget=TagsAdminWidget(),
        required=False,
        label="Теги",
        help_text="Вводите теги в JSON-формате или через запятую"
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.tags:
            self.initial['tags_input'] = json.dumps(
                self.instance.tags,
                ensure_ascii=False,
                indent=2
            )

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '').strip()
        if not tags_input:
            return []

        if not (tags_input.startswith('[') and tags_input.endswith(']')):
            return [tag.strip() for tag in tags_input.split(',') if tag.strip()]

        try:
            tags = json.loads(tags_input)
            if not isinstance(tags, list):
                raise forms.ValidationError("Должен быть массив тегов")
            return [tag.strip() for tag in tags if tag.strip()]
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Некорректный JSON: {str(e)}")


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    fields = ['author', 'email', 'text', 'rate', 'is_published']
    readonly_fields = ['created_at']


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
    fields = ['name', 'value']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'price', 'display_image', 'is_limited', 'on_sale', 'display_decoded_tags', 'rating']
    list_filter = ['is_limited', 'categories', 'free_delivery']
    search_fields = ['name', 'tags']
    filter_horizontal = ['categories']
    inlines = [SpecificationInline, ReviewInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'full_description', 'image', 'price', 'count')
        }),
        ('Категории и теги', {
            'fields': ('categories', 'tags_input')
        }),
        ('Доставка и рейтинг', {
            'fields': ('free_delivery', 'rating')
        }),
        ('Распродажа', {
            'fields': ('sale_price', 'date_from', 'date_to'),
            'classes': ('collapse',)
        }),
        ('Лимитированная серия', {
            'fields': ('is_limited',),
            'classes': ('collapse',)
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "-"
    display_image.short_description = "Изображение"

    def display_decoded_tags(self, obj):
        if obj.tags:
            decoded_tags = [
                tag.encode('utf-8').decode('unicode-escape')
                if isinstance(tag, str) else str(tag)
                for tag in obj.tags
            ]
            return ", ".join(decoded_tags)
        return "-"
    display_decoded_tags.short_description = "Теги"

    def on_sale(self, obj):
        return obj.sale_price is not None
    on_sale.boolean = True
    on_sale.short_description = "Распродажа"

    def save_model(self, request, obj, form, change):
        if 'tags_input' in form.cleaned_data:
            obj.tags = form.cleaned_data['tags_input']
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'is_featured', 'parent_link')
    list_editable = ('is_featured',)
    search_fields = ('name',)
    list_filter = ('is_featured', 'parent')
    fields = ('parent', 'name', 'image', 'is_featured')

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "-"
    display_image.short_description = "Изображение"

    def parent_link(self, obj):
        if obj.parent:
            url = reverse('admin:app_category_change', args=[obj.parent.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return "-"
    parent_link.short_description = "Родительская категория"