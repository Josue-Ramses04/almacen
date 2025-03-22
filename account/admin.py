from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Product, Category, Branch
from .models import RegistrationAttempt

# Filtro personalizado para separar usuarios por grupo
class GroupFilter(admin.SimpleListFilter):
    title = _('User Group')  # El título del filtro
    parameter_name = 'group'  # El nombre del parámetro en la URL

    def lookups(self, request, model_admin):
        # Devolver las opciones del filtro
        return (
            ('admin', _('Admin')),
            ('user', _('User')),
        )

    def queryset(self, request, queryset):
        # Filtrar los usuarios según el grupo seleccionado
        if self.value() == 'admin':
            return queryset.filter(groups__name='admin')  # Filtrar por grupo "admin"
        if self.value() == 'user':
            return queryset.filter(groups__name='user')  # Filtrar por grupo "user"
        return queryset

# Personalización del administrador de User
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')  # Columnas a mostrar
    list_filter = ('is_staff', 'is_active', GroupFilter)  # Filtro por grupos y estado


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'branch')





class RegistrationAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'user', 'timestamp', 'is_allowed')
    list_filter = ('is_allowed', 'timestamp')
    actions = ['permitir_registros', 'bloquear_registros']

    def permitir_registros(self, request, queryset):
        queryset.update(is_allowed=True)
    permitir_registros.short_description = "Permitir registros seleccionados"

    def bloquear_registros(self, request, queryset):
        queryset.update(is_allowed=False)
    bloquear_registros.short_description = "Bloquear registros seleccionados"



admin.site.register(RegistrationAttempt, RegistrationAttemptAdmin)


admin.site.register(Product, ProductAdmin)


admin.site.register(Branch)


# Registra el modelo de usuario con la personalización
admin.site.unregister(User)


admin.site.register(User, UserAdmin)

admin.site.register(Category)