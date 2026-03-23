from django.contrib import admin
from django.utils.html import format_html
from .models import Grain, FeedFormula, FeedFormulaItem


@admin.register(Grain)
class GrainAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'protein_bar', 'fat_percent',
                     'carb_percent', 'calories_per_100g')
    list_filter   = ('category',)
    search_fields = ('name', 'description')
    ordering      = ('category', 'name')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description')
        }),
        ('Nutritional Values (per 100g)', {
            'fields': ('protein_percent', 'fat_percent',
                       'carb_percent', 'fiber_percent', 'calories_per_100g')
        }),
    )

    def protein_bar(self, obj):
        pct = min(obj.protein_percent, 30)
        bar_width = int(pct / 30 * 100)
        color = '#16a34a' if obj.protein_percent >= 15 else \
                '#d97706' if obj.protein_percent >= 10 else '#6b7280'
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;">'
            '<div style="width:80px;height:8px;background:#e5e7eb;'
            'border-radius:4px;overflow:hidden;">'
            '<div style="width:{}%;height:100%;background:{};'
            'border-radius:4px;"></div></div>'
            '<span style="font-size:12px;color:{};">'
            '<b>{}%</b></span></div>',
            bar_width, color, color, obj.protein_percent
        )
    protein_bar.short_description = 'Protein'


class FeedFormulaItemInline(admin.TabularInline):
    model  = FeedFormulaItem
    extra  = 3
    fields = ('grain', 'percentage', 'percentage_bar')
    readonly_fields = ('percentage_bar',)

    def percentage_bar(self, obj):
        if not obj.pk:
            return '—'
        bar_width = int(min(obj.percentage, 100))
        return format_html(
            '<div style="width:{}px;height:8px;background:#2563eb;'
            'border-radius:4px;"></div>',
            bar_width
        )
    percentage_bar.short_description = 'Visual'


@admin.register(FeedFormula)
class FeedFormulaAdmin(admin.ModelAdmin):
    list_display  = ('name', 'user_link', 'purpose_badge',
                     'target_protein', 'item_count', 'created_at')
    list_filter   = ('purpose', 'created_at')
    search_fields = ('name', 'user__username', 'notes')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'nutrition_summary')
    inlines       = [FeedFormulaItemInline]

    fieldsets = (
        ('Formula Info', {
            'fields': ('user', 'name', 'purpose', 'target_protein', 'notes')
        }),
        ('Nutrition Summary', {
            'fields': ('nutrition_summary',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def user_link(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/users/user/{}/change/">{}</a>',
                obj.user.pk, obj.user.username
            )
        return format_html('<span style="color:#9ca3af;">Anonymous</span>')
    user_link.short_description = 'User'

    def purpose_badge(self, obj):
        colors = {
            'racing':      '#2563eb',
            'breeding':    '#16a34a',
            'molting':     '#d97706',
            'maintenance': '#6b7280',
            'young':       '#9333ea',
        }
        color = colors.get(obj.purpose, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:999px;font-size:12px;font-weight:600;">{}</span>',
            color, obj.get_purpose_display()
        )
    purpose_badge.short_description = 'Purpose'

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Grains'

    def nutrition_summary(self, obj):
        items = obj.items.select_related('grain').all()
        if not items:
            return 'No grains added yet.'
        total_protein = total_fat = total_carbs = total_cal = 0
        rows = []
        for item in items:
            g = item.grain
            w = item.percentage / 100
            p  = g.protein_percent * w
            f  = g.fat_percent     * w
            c  = g.carb_percent    * w