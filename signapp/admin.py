from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Proceso
from django.core.signing import Signer
from django.utils.html import format_html
import uuid

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ("ref_rrhh", "estado", "creado", "expira", "link", "pdf")
    list_filter = ("estado", ("creado", admin.DateFieldListFilter), ("expira", admin.DateFieldListFilter))
    search_fields = ("ref_rrhh", "pdf_hash")
    date_hierarchy = "creado"
    ordering = ("-creado",)


    fieldsets = (
        ("Datos del proceso", {"fields": ("ref_rrhh","candidato_email"),}),
        ("Enlace (solo lectura)", {"fields": ("token", "creado", "expira", "link"),}),
        ("Estado", {"fields": ("estado",),}),
        ("Documento final", {"fields": ("pdf_firmado", "pdf_hash"),}),
    )

    readonly_fields = ("token", "creado", "expira", "link", "pdf_hash", "pdf_firmado")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def link(self, obj):
        if not obj.token:
            return format_html ('<span style="color: grey;">(Pendiente)</span>') 
        url = f"/firma/{obj.token}/"
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)
    link.short_description = "Enlace Público"

    def pdf(self, obj):
        if obj.pdf_firmado:
            return "Descargar"
        return "—"
    pdf.short_description = "PDF firmado"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.expira = timezone.now() + timedelta(hours = 48)
            signer = Signer()
            unique_id =str(uuid.uuid4())
            data = f"{unique_id}:{obj.ref_rrhh}"
            obj.token = signer.sign(data)[:50]
            
        super().save_model(request, obj, form, change)