from django import forms
from .models import Produto, Categoria

# --- FORMULÁRIO DE PRODUTO (O papel para cadastrar o lanche) ---
class ProdutoForm(forms.ModelForm):
    class Meta:
        # 1. ORIGEM: Diz para o Django: "Baseie este formulário na tabela Produto"
        model = Produto
        
        # 2. CAMPOS: Quais informações o usuário deve preencher?
        fields = ['nome', 'categoria', 'quantidade', 'preco', 'preco_custo', 'estoque_minimo', 'descricao']
        
        # 3. WIDGETS (A "Maquiagem" do campo): 
        # Aqui é onde a gente coloca as classes do CSS (como 'form-control') para 
        # o formulário não ficar feio e desarrumado na tela.
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            # 'min': '0' impede que o cara tente digitar "-5" coxinhas no teclado
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            # 'step': '0.01' permite os centavos (9.99)
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            # Textarea é aquele campo maior para textos longos
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# --- FORMULÁRIO DE CATEGORIA (O papel para cadastrar o grupo, ex: Bebidas) ---
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }