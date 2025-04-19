from django.contrib import admin
from django import forms
import json
from .models import Product, Category, Specification


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'price', 'display_decoded_tags']
    search_fields = ['name', 'tags']

    def display_decoded_tags(self, obj):
        if obj.tags:
            decoded_tags = [
                tag.encode('utf-8').decode('unicode-escape')
                if isinstance(tag, str) else str(tag)
                for tag in obj.tags
            ]
            return ", ".join(decoded_tags)
        return "-"

    display_decoded_tags.short_description = "Теги (читаемый вид)"

    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'tags_input')
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'tags_input' in form.cleaned_data:
            obj.tags = form.cleaned_data['tags_input']
        super().save_model(request, obj, form, change)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value')
    list_editable = ('value',)
    search_fields = ('product__name', 'name', 'value')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured')
    list_editable = ('is_featured',)
    search_fields = ('name',)