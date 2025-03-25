from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Product, Category, Branch, RegistrationAttempt

# 🔹 Filtro para separar usuarios por grupo en la administración
class GroupFilter(admin.SimpleListFilter):
    title = _('User Group')  # El título del filtro
    parameter_name = 'group'  # Nombre del parámetro en la URL

    def lookups(self, request, model_admin):
        return (
            ('admin', _('Admin')),
            ('user', _('User')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(groups__name='admin')
        if self.value() == 'user':
            return queryset.filter(groups__name='user')
        return queryset

# 🔹 Personalización del administrador de usuarios con opción de bloqueo/desbloqueo
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')  # Muestra el estado del usuario
    list_filter = ('is_staff', 'is_active', GroupFilter)  # Filtros
    actions = ['bloquear_usuarios', 'desbloquear_usuarios']  # Acciones para el admin

    def bloquear_usuarios(self, request, queryset):
        queryset.update(is_active=False)  # Bloquea a los usuarios seleccionados
        self.message_user(request, "Los usuarios seleccionados han sido bloqueados.")
    bloquear_usuarios.short_description = "❌ Bloquear usuarios seleccionados"

    def desbloquear_usuarios(self, request, queryset):
        queryset.update(is_active=True)  # Desbloquea a los usuarios seleccionados
        self.message_user(request, "Los usuarios seleccionados han sido desbloqueados.")
    desbloquear_usuarios.short_description = "✅ Desbloquear usuarios seleccionados"
    

# 🔹 Personalización del administrador de productos
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'branch')
    
    

# 🔹 Personalización del administrador de intentos de registro (Login)
class RegistrationAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'user', 'timestamp', 'is_allowed')
    list_filter = ('is_allowed', 'timestamp')
    actions = ['permitir_registros', 'bloquear_registros']

    def permitir_registros(self, request, queryset):
        queryset.update(is_allowed=True)
        self.message_user(request, "Registros permitidos.")
    permitir_registros.short_description = "✅ Permitir registros seleccionados"

    def bloquear_registros(self, request, queryset):
        queryset.update(is_allowed=False)
        self.message_user(request, "Registros bloqueados.")
    bloquear_registros.short_description = "❌ Bloquear registros seleccionados"


# 🔹 Registrar modelos en el panel de administración
admin.site.unregister(User)  # Desregistrar el modelo User original
admin.site.register(User, UserAdmin)  # Registrar el modelo User con personalización
admin.site.register(RegistrationAttempt, RegistrationAttemptAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Branch)
admin.site.register(Category)


