from django import forms
from .models import Auth

class FormularioRegistro(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Ingresar Contraseña',
        'class': 'form-control',
    }))

    confirmar_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirmar Contraseña',
        'class': 'form-control',
    }))
    class Meta:
        model= Auth
        fields=['nombre','apellido','email','telefono','password']
    

    def __init__(self, *args,**kwargs):
        super(FormularioRegistro,self).__init__(*args,**kwargs)
        self.fields['nombre'].widget.attrs['placeholder']= 'ingresar Nombre'
        self.fields['apellido'].widget.attrs['placeholder']= 'Ingresar Apellido'
        self.fields['email'].widget.attrs['placeholder']= 'ingresar Email'
        self.fields['telefono'].widget.attrs['placeholder']= 'ingresar Telefono'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        limpiar_datos= super(FormularioRegistro, self).clean()
        password= limpiar_datos.get('password')
        confirmar_password= limpiar_datos.get('confirmar_password')

        if password != confirmar_password:
            raise forms.ValidationError(
                "Ups las contraseñas no Coinciden!"
            )
