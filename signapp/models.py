# from django.db import models

# class Proceso(models.Model):
#     class Estado(models.TextChoices):

#         VIGENTE = "VIGENTE", 'vigente'
#         USADO = "USADO", "usado"
#         EXPIRADO = "EXPIRADO", "expirado"

#     ref_rrhh = models.CharField(max_length = 180, db_index = True)
#     token = models.SlugField(unique = True, db_index = True)
#     estado = models.CharField(max_length = 10, choices = Estado.choices, default=Estado.VIGENTE, db_index = True)
#     creado = models.DateTimeField(auto_now_add = True, db_index = True)
#     expira = models.DateTimeField(db_index = True)

#     pdf_firmado = models.FileField(upload_to = 'contratos/', blank = True, null = True)
#     pdf_hash = models.CharField(max_length = 70, blank = True, null = True)
#     acceso_link = models.DateTimeField(blank = True, null = True)

#     def __str__(self) -> str:
#         return f"{self.ref_rrhh} ({self.estado})"
        
