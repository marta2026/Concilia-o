# 📊 Sistema de Conciliação Contábil

Sistema web para conciliação contábil das empresas **Nutricash** e **MaxiFrota**, construído com **Streamlit**.

---

## 🚀 Execução local

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/conciliacao-contabil.git
cd conciliacao-contabil
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute o app
```bash
streamlit run app.py
```

---

## ☁️ Deploy no Streamlit Cloud

1. Faça push deste projeto para um repositório GitHub público ou privado.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e clique em **New app**.
3. Selecione o repositório, branch `main` e o arquivo `app.py`.
4. Clique em **Deploy** — pronto!

---

## 📁 Estrutura do projeto

```
conciliacao-contabil/
├── app.py                  # Entry point principal
├── requirements.txt
├── README.md
├── pages/
│   ├── empresa.py          # Tela de seleção de empresa
│   ├── dashboard.py        # Painel + histórico
│   └── modulo.py           # Módulo de conciliação (formulário + resultado)
└── utils/
    ├── config.py           # Configurações: empresas e contas
    ├── state.py            # Gerenciamento de estado (session_state)
    ├── helpers.py          # Funções auxiliares: cálculo, formatação, export
    └── style.css           # CSS customizado
```

---

## 🏦 Contas disponíveis

### Ativo
| Conta | Código |
|-------|--------|
| Adiantamento a Fornecedores | 18805000003 |
| Adiantamento de Férias | 18803000003 |
| Adiantamento de Salários | 18803000001 |
| IRRF Antecipado | 18845100003 |

### Passivo
| Conta | Código |
|-------|--------|
| IRRF s/ Serviços a Recolher | 49420100001 |
| IRRF s/ Comissões a Recolher | 49420100002 |
| PIS a Recolher | 49420900001 |
| COFINS a Recolher | 49420900002 |
| ISS a Recolher | 49420900003 |
| Fornecedores | 49992000001 |
| Rede Conveniada a Pagar (NC) | 49992000002 |
| Moeda Eletrônica PAT Papel (NC) | 49992000022 |
| Moeda Eletrônica Frota Papel (MF) | 49992000023 |

---

## ✨ Funcionalidades

- ✅ Seleção de empresa (Nutricash / MaxiFrota) com temas visuais distintos
- ✅ Painel com KPIs e gráfico de status (Plotly)
- ✅ Cards de contas com status (OK / Pendente)
- ✅ Histórico de conciliações por empresa
- ✅ Preenchimento manual dos campos por conta
- ✅ Auto-preenchimento via upload de XLSX / CSV / TXT / JSON
- ✅ Cálculo automático da diferença (Razão − Auxiliar)
- ✅ Resultado visual com indicador APROVADA / REVISAR
- ✅ Export para Excel (.xlsx)
- ✅ Persistência de estado na sessão (histórico + status)

---

## 🔧 Adicionando novas contas

Edite `utils/config.py` e adicione um novo item à lista `contas`:

```python
{
    "id": "minha-conta",
    "nome": "Nome da Conta",
    "codigo": "XXXXXXXXXXXXX",
    "tipo": "ativo",   # ou "passivo"
    "icon": "💡",
    "empresas": ["nc", "mf"],  # ou só ["nc"] / ["mf"]
    "campos": ["Saldo Inicial", "Entradas", "Saídas", "Saldo Razão"],
    "wip": False,
},
```

---

## 📝 Licença

Uso interno. Todos os direitos reservados.
