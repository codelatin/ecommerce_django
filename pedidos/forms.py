from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre', 'apellido', 'direccion','telefono', 'ciudad', 'pais', 'observacion_pedido']
    
    def __init__(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs['placeholder'] = 'Ingrese su Nombre'
        self.fields['apellido'].widget.attrs['placeholder'] = 'Ingrese su Apellido'
        self.fields['direccion'].widget.attrs['placeholder'] = 'Ingrese su Dirección'
        self.fields['ciudad'].widget.attrs['placeholder'] = 'Ingrese su Ciudad'
        self.fields['pais'].widget.attrs['placeholder'] = 'Ingrese su País'
        self.fields['observacion_pedido'].widget.attrs['placeholder'] = 'Observaciones sobre el pedido (opcional)'
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'