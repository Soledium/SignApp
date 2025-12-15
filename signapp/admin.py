from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.core.signing import Signer
from django.utils.html import format_html
import uuid

from .models import Proceso, PlantillaContrato


@admin.register(PlantillaContrato)
class PlantillaContratoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "pagina_firma",)
    list_filter = ("activo",)
    search_fields = ("nombre",)
    fieldsets = (
        ("Información", {"fields": ("nombre", "archivo", "activo")}),
        ("Firma", {"fields": ("pagina_firma", "firma_x_rel", "firma_y_rel", "firma_ancho_rel", "firma_alto_rel")}),
    )


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ("ref_rrhh","candidato_email","plantilla","estado","creado","expira","link","pdf",)
    list_filter = ("estado",("creado", admin.DateFieldListFilter),("expira", admin.DateFieldListFilter),)
    search_fields = ("ref_rrhh", "candidato_email", 'estado',)
    date_hierarchy = "creado"
    ordering = ("-creado",)

    fieldsets = (
        ("Datos del proceso", {
            "fields": ("ref_rrhh", "candidato_email", "plantilla"),
        }),
        ("Enlace (solo lectura)", {
            "fields": ("token", "creado", "expira", "link"),
        }),
        ("Estado", {
            "fields": ("estado",),
        }),
        ("Documento final", {
            "fields": ("pdf_firmado",),
        }),
    )

    readonly_fields = ("token", "creado", "expira", "link", "pdf_hash", "pdf_firmado", "estado",)

    def has_delete_permission(self, request, obj=None):
        # solo superusuario puede borrar procesos
        return request.user.is_superuser

    def link(self, obj):
        if not obj.token:
            return format_html('<span style="color: grey;">(Pendiente)</span>')
        url = f"/firma/{obj.token}/"
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)
    link.short_description = "Enlace Público"

    def pdf(self, obj):
        if obj.pdf_firmado:
            return format_html(
                '<a href="{0}" target="_blank">Descargar</a>',
                obj.pdf_firmado.url
            )
        return "—"
    pdf.short_description = "PDF firmado"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # 48 horas de validez
            obj.expira = timezone.now() + timedelta(hours=48)

            # generar token único
            signer = Signer()
            unique_id = str(uuid.uuid4())
            data = f"{unique_id}:{obj.ref_rrhh}"
            obj.token = signer.sign(data)[:50]

        super().save_model(request, obj, form, change)
