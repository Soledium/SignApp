from django.db import models
from django.utils import timezone

class PlantillaContrato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to="contratos/plantillas/")
    activo = models.BooleanField(default=True)
    pagina_firma = models.PositiveIntegerField(default=1, help_text="Página donde se ubicará la firma.")
    firma_x_rel = models.FloatField(default=0.65, help_text="Posición X relativa (0=izq, 1=der)")
    firma_y_rel = models.FloatField(default=0.10, help_text="Posición Y relativa (0=abajo, 1=arriba)")
    firma_alto_rel = models.FloatField(default=0.12, help_text="Alto relativo de la firma (en alto de página)")
    firma_ancho_rel = models.FloatField(default=0.3, help_text="Ancho relativo de la firma (En el ancho de la página).")

    def __str__(self):
        return self.nombre

class Proceso(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = "VIGENTE", "vigente"
        USADO = "USADO", "usado"
        EXPIRADO = "EXPIRADO", "expirado"
#info rrhh
    ref_rrhh = models.CharField(max_length=180, db_index=True)
    candidato_email = models.EmailField(max_length=254, db_index=True)
    candidato_nombre = models.CharField(max_length=120, blank=True, null=True)
    candidato_rut = models.CharField(max_length=15, blank=True, null=True)
    candidato_cargo = models.CharField(max_length=120, blank=True, null=True)
    candidato_fecha_ingreso = models.DateField(blank=True, null=True)

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
        return timezone.now() > self.expira
    
    def __str__(self) -> str:
        return f"{self.ref_rrhh} - {self.candidato_email}"


