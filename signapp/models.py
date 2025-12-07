from django.db import models
from django.utils import timezone

class PlantillaContrato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to="contratos/plantillas/")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Proceso(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = "VIGENTE", "vigente"
        USADO = "USADO", "usado"
        EXPIRADO = "EXPIRADO", "expirado"
#info rrhh
    ref_rrhh = models.CharField(max_length=180, db_index=True)
    candidato_email = models.EmailField(max_length=254, unique=True, db_index=True)
    plantilla = models.ForeignKey(PlantillaContrato, on_delete=models.PROTECT)
#link unico
    token = models.SlugField(unique=True, db_index=True)
    estado = models.CharField(max_length=10,choices=Estado.choices,default=Estado.VIGENTE,db_index=True,)
    usado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True, db_index=True)
    expira = models.DateTimeField(db_index=True)
    pdf_firmado = models.FileField(upload_to="contratos/firmados/", blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    pdf_hash = models.CharField(max_length=70, blank=True, null=True)
    
    acceso_link = models.DateTimeField(blank=True, null=True)

    def ha_expirado(self):
        """Verifica si la fecha de expiración ha sido superada."""
        return timezone.now() > self.expira
    
    def __str__(self) -> str:
        return f"{self.ref_rrhh} - {self.candidato_email}"


