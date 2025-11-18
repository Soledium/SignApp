from django import forms

class FirmaContratoForm(forms.Form):
    # =======================================================
    # 1. Campos de Archivo (Upload)
    # =======================================================
    
    # RF04: Firma (PNG/JPG)
    firma_img = forms.FileField(
        label='1. Sube tu imagen de Firma (PNG o JPG)',
        widget=forms.ClearableFileInput(),
        required=True,
        help_text="Máximo 5 MB. Se recomienda fondo transparente."
    )
    
    # RF04: Contrato (PDF)
    contrato_pdf = forms.FileField(
        label='2. Sube el Documento a Firmar (PDF)',
        widget=forms.ClearableFileInput(),
        required=True,
        help_text="Máximo 20 MB."
    )
    
    # =======================================================
    # 2. Campo de Consentimiento (HU03)
    # =======================================================
    consentimiento = forms.BooleanField(
        label='Acepto que la imagen de mi firma sea estampada de forma digital e irreversible en el documento.',
        required=True
    )
    
    # =======================================================
    # 3. Lógica de Validación (clean methods) (RNF01)
    # =======================================================
    
    def clean_firma_img(self):
        archivo = self.cleaned_data['firma_img']
        
        # Validar tipo de archivo (solo PNG/JPG)
        if not archivo.content_type in ['image/jpeg', 'image/png']:
            raise forms.ValidationError("La firma debe ser una imagen PNG o JPG. Otro tipo de archivo detectado.")
        
        # Validar tamaño (5MB)
        if archivo.size > (5 * 1024 * 1024): 
            raise forms.ValidationError("La imagen de la firma no debe superar los 5 MB.")
            
        return archivo

    def clean_contrato_pdf(self):
        archivo = self.cleaned_data['contrato_pdf']
        
        # Validar tipo de archivo (solo PDF)
        if not archivo.content_type == 'application/pdf':
            raise forms.ValidationError("El documento a firmar debe ser un archivo PDF.")
        
        # Validar tamaño (20MB)
        if archivo.size > (20 * 1024 * 1024):
            raise forms.ValidationError("El contrato no debe superar los 20 MB.")
            
        return archivo