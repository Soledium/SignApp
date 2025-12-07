from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.core.signing import Signer
from django.utils.html import format_html
import uuid

from .models import Proceso, PlantillaContrato


@admin.register(PlantillaContrato)
class PlantillaContratoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = (
        "ref_rrhh",
        "candidato_email",
        "plantilla",
        "estado",
        "creado",
        "expira",
        "link",
        "pdf",
    )
    list_filter = (
        "estado",
        ("creado", admin.DateFieldListFilter),
        ("expira", admin.DateFieldListFilter),
    )
    search_fields = ("ref_rrhh", "candidato_email", "pdf_hash", "token")
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
            "fields": ("pdf_firmado", "pdf_hash"),
        }),
    )

    # Estos campos no los edita RR.HH. a mano
    readonly_fields = ("token", "creado", "expira", "link", "pdf_hash", "pdf_firmado")

    def has_delete_permission(self, request, obj=None):
        # Solo superusuario puede borrar procesos
        return request.user.is_superuser

    def link(self, obj):
        """Enlace público para el candidato."""
        if not obj.token:
            return format_html('<span style="color: grey;">(Pendiente)</span>')
        url = f"/firma/{obj.token}/"
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)
    link.short_description = "Enlace Público"

    def pdf(self, obj):
        """Link de descarga al PDF firmado, si existe."""
        if obj.pdf_firmado:
            return format_html(
                '<a href="{0}" target="_blank">Descargar</a>',
                obj.pdf_firmado.url
            )
        return "—"
    pdf.short_description = "PDF firmado"

    def save_model(self, request, obj, form, change):
        """Al crear un proceso nuevo, se genera token y fecha de expiración (48 h)."""
        if not obj.pk:
            # 48 horas desde ahora
            obj.expira = timezone.now() + timedelta(hours=48)

            # Generar token firmado basado en UUID + ref_rrhh
            signer = Signer()
            unique_id = str(uuid.uuid4())
            data = f"{unique_id}:{obj.ref_rrhh}"
            obj.token = signer.sign(data)[:50]

        super().save_model(request, obj, form, change)
