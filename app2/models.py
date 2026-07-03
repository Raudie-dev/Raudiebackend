from django.db import models

class User_admin(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    bloqueado = models.BooleanField(default=False)
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    permisos = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.nombre

class ConfigBot(models.Model):
    nombre = models.CharField(max_length=255)
    owner = models.ForeignKey(User_admin, on_delete=models.CASCADE, null=True, blank=True, related_name='bots')
    mensaje_bienvenida = models.TextField(blank=True)
    instrucciones_ia = models.TextField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    api_provider = models.CharField(max_length=50, default='deepseek')
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_response_chars = models.IntegerField(default=1000, help_text='Límite de caracteres en respuestas del bot')
    mensaje_cierre = models.CharField(max_length=500, blank=True, default='', help_text='Mensaje al cerrar conversación por inactividad')
    inactividad_minutos = models.IntegerField(default=0, help_text='Minutos de inactividad para cerrar conversación (0 = desactivado)')

    def __str__(self):
        return f"{self.nombre} (Owner: {self.owner})"

class ContextFile(models.Model):
    bot = models.ForeignKey(ConfigBot, on_delete=models.CASCADE, related_name='context_files')
    file = models.FileField(upload_to='context_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} - Bot: {self.bot.nombre}"

class TelegramMessage(models.Model):
    bot = models.ForeignKey(ConfigBot, on_delete=models.CASCADE, related_name='messages')
    chat_id = models.CharField(max_length=255)
    push_name = models.CharField(max_length=255, blank=True, null=True)
    message_text = models.TextField(blank=True, null=True)
    reply_text = models.TextField(blank=True, null=True)
    replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)
    transferido = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg from {self.push_name or self.chat_id} to {self.bot.nombre}"

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    owner = models.ForeignKey(User_admin, on_delete=models.CASCADE, related_name='departamentos')

    def __str__(self):
        return self.nombre

class Agente(models.Model):
    nombre = models.CharField(max_length=100)
    telegram_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID de chat o usuario de Telegram")
    activo = models.BooleanField(default=True)
    owner = models.ForeignKey(User_admin, on_delete=models.CASCADE, related_name='agentes')
    departamentos = models.ManyToManyField(Departamento, blank=True, related_name='agentes')

    def __str__(self):
        return self.nombre


class ClienteConsulta(models.Model):
    bot = models.ForeignKey(ConfigBot, on_delete=models.CASCADE, related_name='consultas')
    remote_jid = models.CharField(max_length=200, blank=True)
    nombre = models.CharField(max_length=200, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    empresa = models.CharField(max_length=200, blank=True)
    plan_interes = models.CharField(max_length=200, blank=True)
    resumen = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre or self.remote_jid} — {self.created_at:%d/%m/%Y}"


class CostItem(models.Model):
    descripcion = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.descripcion


class ProjectHourlyRate(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=25.0)


class ProjectCostType(models.Model):
    descripcion = models.CharField(max_length=255)
    horas = models.DecimalField(max_digits=10, decimal_places=2)
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return self.descripcion


class IncomeRecord(models.Model):
    fecha = models.DateField(null=True, blank=True)
    cliente = models.CharField(max_length=255)
    monto_usd = models.DecimalField(max_digits=12, decimal_places=2)
    tasa_dia = models.DecimalField(max_digits=12, decimal_places=2)
    total_bs = models.DecimalField(max_digits=15, decimal_places=2)
    cobrada = models.BooleanField(default=True)
    cuota = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"{self.cliente} - {self.monto_usd}$"


class ExpenseRecord(models.Model):
    fecha = models.DateField(null=True, blank=True)
    proveedor = models.CharField(max_length=255)
    monto_usd = models.DecimalField(max_digits=12, decimal_places=2)
    tasa_dia = models.DecimalField(max_digits=12, decimal_places=2)
    total_bs = models.DecimalField(max_digits=15, decimal_places=2)
    pagada = models.BooleanField(default=True)
    fecha_credito = models.CharField(max_length=100, default='no aplica')

    def __str__(self):
        return f"{self.proveedor} - {self.monto_usd}$"


class PublicacionMarketing(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter / X'),
        ('otro', 'Otro'),
    ]
    
    FORMATO_CHOICES = [
        ('video', 'Video'),
        ('imagen', 'Imagen'),
    ]

    owner = models.ForeignKey(User_admin, on_delete=models.CASCADE, null=True, blank=True, related_name='publicaciones_marketing')
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    plataforma = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='instagram')
    formato = models.CharField(max_length=20, choices=FORMATO_CHOICES, default='video')
    guion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.get_plataforma_display()} ({self.fecha})"


