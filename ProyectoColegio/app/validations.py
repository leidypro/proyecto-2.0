from django import forms
from django.contrib.auth.forms import AuthenticationForm

class ValidationsLogin(AuthenticationForm):
    def clean_username(self):
        correo = self.cleaned_data['username']
        dominios_p = ('@gmail.com','@hotmail')
        
        if not correo.endswith(dominios_p):
            self.fields['username'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError(f"Solo es permitido los dominios {dominios_p}")
        return correo
    
    def clean_password(self):
        contraseña  = self.cleaned_data['password']
        if len(contraseña) < 3 :
            raise forms.ValidationError(f"La contraseña es muy corta")
        return contraseña
    
    error_messages = {
        'invalid_login':(
            "El correo y la contraseña pueden estar mal verifica"
        )
    }