from django import forms
from .models import Produto, Categoria


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'quantidade', 'preco', 'preco_custo', 'estoque_minimo', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
