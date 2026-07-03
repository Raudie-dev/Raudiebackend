from django.contrib import admin
from .models import User_admin, ConfigBot, ContextFile, TelegramMessage, Departamento, Agente, ClienteConsulta, CostItem, ProjectHourlyRate, ProjectCostType, IncomeRecord, ExpenseRecord

@admin.register(User_admin)
class UserAdminAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'bloqueado')

@admin.register(ConfigBot)
class ConfigBotAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'owner', 'api_provider', 'created_at')

@admin.register(ContextFile)
class ContextFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'bot', 'uploaded_at')

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('bot', 'chat_id', 'push_name', 'replied', 'transferido', 'received_at')
    list_filter = ('replied', 'transferido', 'bot')

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'owner')

@admin.register(Agente)
class AgenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telegram_id', 'activo', 'owner')

@admin.register(ClienteConsulta)
class ClienteConsultaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'plan_interes', 'created_at')
    list_filter = ('bot', 'plan_interes')

@admin.register(CostItem)
class CostItemAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'precio')

@admin.register(ProjectHourlyRate)
class ProjectHourlyRateAdmin(admin.ModelAdmin):
    list_display = ('rate',)

@admin.register(ProjectCostType)
class ProjectCostTypeAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'horas')

@admin.register(IncomeRecord)
class IncomeRecordAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'cliente', 'monto_usd', 'tasa_dia', 'total_bs', 'cobrada')
    list_filter = ('cobrada',)

@admin.register(ExpenseRecord)
class ExpenseRecordAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'proveedor', 'monto_usd', 'tasa_dia', 'total_bs', 'pagada', 'fecha_credito')
    list_filter = ('pagada',)


