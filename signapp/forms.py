from django import forms

class FirmaContratoForm(forms.Form):

    # Firma (PNG/JPG)
    firma_img = forms.FileField(
        label='1. Sube tu imagen de Firma (PNG o JPG)',
        widget=forms.ClearableFileInput(),
        required=True,
        help_text="Máximo 5 MB. Se recomienda fondo claro."
    )

    consentimiento = forms.BooleanField(
        label='Acepto que la imagen de mi firma sea estampada de forma digital e irreversible en el contrato seleccionado por RR.HH.',
        required=True
    )
    
    def clean_firma_img(self):
        archivo = self.cleaned_data['firma_img']
        
        # Validar tipo de archivo (solo PNG/JPG)
        if archivo.content_type not in ['image/jpeg', 'image/png']:
            raise forms.ValidationError(
                "La firma debe ser una imagen PNG o JPG. Otro tipo de archivo detectado."
            )
        
        # Validar tamaño (5MB)
        if archivo.size > (5 * 1024 * 1024): 
            raise forms.ValidationError(
                "La imagen de la firma no debe superar los 5 MB."
            )
            
        return archivo
