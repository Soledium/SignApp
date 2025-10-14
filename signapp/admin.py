# from django.contrib import admin
# from django.utils import timezone
# from datetime import timedelta
# from .models import Proceso
# import secrets

# @admin.register(Proceso)
# class ProcesoAdmin(admin.ModelAdmin):
#     list_display = ("ref_rrhh", "estado", "creado", "expira", "link", "descarga")
#     list_filter = ("estado", ("creado", admin.DateFieldListFilter), ("expira", admin.DateFieldListFilter))
#     search_fields = ("ref_rrhh", "pdf_hash")
#     date_hierarchy = "creado"
#     ordering = ("-creado")


#     fieldsets = (
#         ("Datos del proceso", {"fields": ("ref_rrhh",)}),
#         ("Enlace (solo lectura)", {"fields": ("token", "creado", "expira", "link_publico"),}),
#         ("Estado", {"fields": ("estado",),}),
#         ("Documento final", {"fields": ("pdf_firmado", "pdf_hash"),}),
#     )

#     readonly_fields = ("token", "creado", "expira", "link", "pdf_hash", "pdf_firmado")

#     def has_delete_permission(self, request, obj=None):
#         return request.user.is_superuser
    
#     def link_publico(self, obj):
#         if not obj.token:
#             return "—"

#         url = f"/firma/{obj.token}/"
#         return url
#     link_publico.short_description = "URL pública"

#     def descargar_pdf(self, obj):
#         if obj.pdf_firmado:
#             return "Descargar"
#         return "—"
#     descargar_pdf.short_description = "PDF firmado"