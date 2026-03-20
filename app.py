import streamlit as st
import io, hashlib, datetime
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Conciliação Contábil", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════
# USUÁRIOS  — perfil: "admin" | "nc" | "mf"
# Para trocar senha gere um novo hash:
#   python3 -c "import hashlib; print(hashlib.sha256('SUA_SENHA'.encode()).hexdigest())"
# ══════════════════════════════════════════════════════════════════════
USUARIOS = {
    "admin":     {"nome":"Administrador",      "hash":hashlib.sha256("admin123".encode()).hexdigest(), "perfil":"admin"},
    "nutricash": {"nome":"Analista Nutricash", "hash":hashlib.sha256("nc2024".encode()).hexdigest(),   "perfil":"nc"},
    "maxifrota": {"nome":"Analista MaxiFrota", "hash":hashlib.sha256("mf2024".encode()).hexdigest(),   "perfil":"mf"},
}

# ══════════════════════════════════════════════════════════════════════
# CSS — fiel ao layout original HTML
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*{box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
[data-testid="stToolbar"]{display:none}
body,.stApp{background:#F7FAFC!important;font-family:'Inter',sans-serif;font-size:13px;color:#2D3748}
.block-container{padding-top:0!important;padding-bottom:0!important;max-width:100%!important}

/* TOPBAR */
.topbar{height:56px;display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;position:sticky;top:0;z-index:300;box-shadow:0 2px 8px rgba(0,0,0,.18)}
.topbar-l{display:flex;align-items:center;gap:14px}
.topbar-title{font-size:12px;font-weight:600;color:rgba(255,255,255,.8);letter-spacing:.04em;text-transform:uppercase}
.topbar-div{width:1px;height:30px;background:rgba(255,255,255,.2)}
.topbar-user{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:4px 12px;
  color:rgba(255,255,255,.9);font-size:11px;font-weight:600}

/* SIDEBAR */
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #E2E8F0!important}
.sb-lbl{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:#A0AEC0;padding:10px 12px 3px}
.sb-conta{display:flex;align-items:center;justify-content:space-between;
  padding:5px 12px;font-size:11px;color:#718096;border-left:3px solid transparent;cursor:pointer}
.sb-conta:hover{background:#ECEEF0;color:#2D3748}
.dot-ok{width:7px;height:7px;border-radius:50%;background:#27AE60;flex-shrink:0}
.dot-pend{width:7px;height:7px;border-radius:50%;background:#E67E22;flex-shrink:0}
.dot-conc{width:7px;height:7px;border-radius:50%;background:#2196C4;flex-shrink:0}

/* KPI */
.kpi{background:#fff;border:1px solid #E2E8F0;border-radius:5px;padding:14px 16px;
  display:flex;align-items:center;gap:12px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.kpi-ico{width:38px;height:38px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0}
.kpi-lbl{font-size:10px;font-weight:600;color:#A0AEC0;text-transform:uppercase;letter-spacing:.04em;margin-bottom:2px}
.kpi-val{font-size:21px;font-weight:700;line-height:1}
.kpi-sub{font-size:10px;color:#A0AEC0;margin-top:2px}

/* CONTA CARD */
.cc{background:#fff;border:1px solid #E2E8F0;border-radius:5px;padding:14px;cursor:pointer;
  transition:all .18s;box-shadow:0 1px 3px rgba(0,0,0,.04);position:relative;overflow:hidden}
.cc::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.cc.ativo::before{background:linear-gradient(90deg,#1D4ED8,#60A5FA)}
.cc.passivo::before{background:linear-gradient(90deg,#9D174D,#EC4899)}
.cc.wip{opacity:.55;cursor:default}
.cc-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:9px}
.cc-ico{font-size:20px}
.cc-name{font-size:12px;font-weight:700;color:#2D3748;margin-bottom:3px;line-height:1.3}
.cc-cod{font-family:'JetBrains Mono',monospace;font-size:10px;color:#A0AEC0}

/* STATUS VISUAL GRANDE — no card */
.status-ok{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:4px;
  font-size:10px;font-weight:700;background:#E8F8EF;color:#27AE60;border:1px solid #A7F3D0}
.status-pend{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:4px;
  font-size:10px;font-weight:700;background:#FEF3E7;color:#E67E22;border:1px solid #FED7AA;
  font-style:italic;letter-spacing:.03em}
.status-conc{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:4px;
  font-size:10px;font-weight:700;background:#EBF8FF;color:#2196C4;border:1px solid #90CDF4}
.status-none{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:4px;
  font-size:10px;font-weight:700;background:#F1F5F9;color:#94A3B8}

/* BADGE TIPO */
.badge-ativo{background:#DBEAFE;color:#1E40AF;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:700}
.badge-passivo{background:#FCE7F3;color:#9D174D;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:700}

/* BANNER */
.banner{display:flex;align-items:flex-start;gap:12px;background:#EBF8FF;
  border-left:4px solid #2196C4;border-radius:4px;padding:12px 16px;
  margin-bottom:20px;font-size:12px;color:#1A6980;line-height:1.6}

/* HIST ROW */
.hist-row{display:flex;align-items:center;justify-content:space-between;
  padding:8px 10px;border-radius:4px;background:#F7FAFC;margin-bottom:6px}
.hist-nome{font-size:12px;font-weight:600;color:#2D3748}
.hist-ref{font-size:10px;color:#A0AEC0;font-family:'JetBrains Mono',monospace}

/* CARD */
.card{background:#fff;border:1px solid #E2E8F0;border-radius:5px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card-hdr{padding:12px 16px;border-bottom:1px solid #E2E8F0;display:flex;align-items:center;justify-content:space-between}
.card-title{font-size:12px;font-weight:700;color:#2D3748}
.card-body{padding:14px 16px}

/* MÓDULO */
.mod-topbar{height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;background:#fff;border-bottom:1px solid #E2E8F0;
  position:sticky;top:0;z-index:200;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.mod-bc{font-size:11px;color:#A0AEC0}
.step{background:#fff;border:1px solid #E2E8F0;border-radius:5px;padding:22px;
  margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.step-n{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#A0AEC0;margin-bottom:5px}
.step-h{font-size:15px;font-weight:700;color:#2D3748;margin-bottom:4px}
.step-p{font-size:12px;color:#718096;margin-bottom:18px;line-height:1.6}

/* RESULTADO */
.r-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.r-kpi{background:#F7FAFC;border:1px solid #E2E8F0;border-radius:4px;padding:12px 14px}
.r-kpi-lbl{font-size:10px;font-weight:700;color:#A0AEC0;text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px}
.r-kpi-val{font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700}
.r-kpi-sub{font-size:10px;color:#A0AEC0;margin-top:2px}
.r-blk-ttl{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:#A0AEC0;margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #E2E8F0}
.diff-box{border-radius:5px;padding:16px 20px;display:flex;align-items:center;
  justify-content:space-between;margin-bottom:14px}
.diff-box.ok{background:#E8F8EF;border:1px solid #A7F3D0}
.diff-box.nok{background:#FDEDEC;border:1px solid #FECACA}
.diff-lbl{font-size:13px;font-weight:700}
.diff-val{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700}
.diff-bdg{font-size:10px;font-weight:700;padding:4px 12px;border-radius:3px;color:#fff;letter-spacing:.04em}
.diff-box.ok .diff-lbl,.diff-box.ok .diff-val{color:#27AE60}
.diff-box.ok .diff-bdg{background:#27AE60}
.diff-box.nok .diff-lbl,.diff-box.nok .diff-val{color:#E74C3C}
.diff-box.nok .diff-bdg{background:#E74C3C}
.note-box{background:#FFF8E1;border:1px solid #FFE082;border-left:4px solid #F59E0B;
  border-radius:4px;padding:10px 14px;font-size:11px;color:#78350F;line-height:1.7;margin-bottom:14px}

/* TIPO-LBL divisor */
.tipo-lbl{display:flex;align-items:center;gap:10px;font-size:10px;font-weight:700;
  color:#A0AEC0;letter-spacing:.08em;text-transform:uppercase;margin:16px 0 10px}
.tipo-lbl::after{content:'';flex:1;height:1px;background:#E2E8F0}

/* LOGIN */
.stButton>button{border-radius:4px!important;font-weight:700!important;font-size:13px!important;transition:all .15s}
[data-testid="stSidebar"] .stButton>button{font-size:11px!important;padding:4px 8px!important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# DADOS
# ══════════════════════════════════════════════════════════════════════
EMPRESAS = {
    "nc": {"id":"nc","nome":"Nutricash","razao":"NUTRICASH LTDA","hdr":"#1C3557","acc":"#2196C4"},
    "mf": {"id":"mf","nome":"MaxiFrota","razao":"MAXIFROTA LTDA","hdr":"#003D78","acc":"#F5A800"},
}

MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# Campos padrão por tipo de conta
_campos_banco     = ["Saldo Extrato Bancário","Saldo Razão"]
_campos_aplicacao = ["Saldo Extrato Aplicação","Saldo Razão"]
_campos_adto      = ["Saldo Inicial","Adiantamentos do Período","Baixas","Saldo Razão"]
_campos_tributo   = ["Saldo Inicial","Valor Apurado/Retido no Período","Recolhimentos","Saldo Razão"]
_campos_simples   = ["Saldo Relatório Auxiliar","Saldo Razão"]
_campos_fornec    = ["Saldo Inicial","NF Recebidas / Lançamentos","Pagamentos Realizados","Saldo Razão"]
_campos_provisao  = ["Saldo Inicial","Provisão do Período","Reversões / Baixas","Saldo Razão"]
_campos_imob      = ["Saldo Inicial","Adições","Baixas / Depreciação","Saldo Razão"]

CONTAS = [
    # ════════════════════════════════════════════════════════
    # NUTRICASH — ATIVO
    # ════════════════════════════════════════════════════════
    {"id":"nc-11110000001","nome":"Caixa","codigo":"1.1.11.000.0001","tipo":"ativo","icon":"💵","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-11230000001","nome":"Banco do Brasil - 10927-4","codigo":"1.1.23.000.0001","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000102","nome":"Santander - 13019419-6","codigo":"1.1.23.000.0102","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000103","nome":"Santander - 13005710-3","codigo":"1.1.23.000.0103","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000200","nome":"Caixa Econômica Federal - 1277-8","codigo":"1.1.23.000.0200","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000300","nome":"Bradesco - 078288-2","codigo":"1.1.23.000.0300","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000400","nome":"Safra - 401811-6","codigo":"1.1.23.000.0400","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000500","nome":"Banese - 125042-2","codigo":"1.1.23.000.0500","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000601","nome":"Itaú - 10026-5","codigo":"1.1.23.000.0601","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000600","nome":"Itaú - 03973-1","codigo":"1.1.23.000.0600","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000602","nome":"Itaú - 03882-1","codigo":"1.1.23.000.0602","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000603","nome":"Itaú - 11407-7","codigo":"1.1.23.000.0603","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000609","nome":"Itaú - 89168-5","codigo":"1.1.23.000.0609","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-11230000610","nome":"Itaú - 56247-3","codigo":"1.1.23.000.0610","tipo":"ativo","icon":"🏦","empresas":["nc"],"campos":_campos_banco,"wip":False},
    {"id":"nc-13110250001","nome":"CDB Bradesco","codigo":"1.3.11.025.0001","tipo":"ativo","icon":"📈","empresas":["nc"],"campos":_campos_aplicacao,"wip":False},
    {"id":"nc-13115300300","nome":"Banco do Brasil (Aplicação)","codigo":"1.3.11.530.0300","tipo":"ativo","icon":"📈","empresas":["nc"],"campos":_campos_aplicacao,"wip":False},
    {"id":"nc-13115300001","nome":"Itaú (Aplicação)","codigo":"1.3.11.530.0001","tipo":"ativo","icon":"📈","empresas":["nc"],"campos":_campos_aplicacao,"wip":False},
    {"id":"nc-13115300100","nome":"Safra (Aplicação)","codigo":"1.3.11.530.0100","tipo":"ativo","icon":"📈","empresas":["nc"],"campos":_campos_aplicacao,"wip":False},
    {"id":"nc-18803000001","nome":"Adiantamento de Salários","codigo":"1.8.80.300.0001","tipo":"ativo","icon":"💼","empresas":["nc"],"campos":_campos_adto,"wip":False},
    {"id":"nc-18803000002","nome":"Adiantamento de 13º Salário","codigo":"1.8.80.300.0002","tipo":"ativo","icon":"💼","empresas":["nc"],"campos":_campos_adto,"wip":False},
    {"id":"nc-18803000003","nome":"Adiantamento de Férias","codigo":"1.8.80.300.0003","tipo":"ativo","icon":"🏖️","empresas":["nc"],"campos":_campos_adto,"wip":False},
    {"id":"nc-18803000004","nome":"Empréstimos Concedidos","codigo":"1.8.80.300.0004","tipo":"ativo","icon":"💰","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18805000002","nome":"Adiantamento a Funcionários (Desp. Adm.)","codigo":"1.8.80.500.0002","tipo":"ativo","icon":"💼","empresas":["nc"],"campos":_campos_adto,"wip":False},
    {"id":"nc-18805000003","nome":"Adiantamento a Fornecedores","codigo":"1.8.80.500.0003","tipo":"ativo","icon":"🏭","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18805000004","nome":"Adiantamento de Boletos Multibenefícios","codigo":"1.8.80.500.0004","tipo":"ativo","icon":"🃏","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18810000001","nome":"Adiantamentos por Conta de Imobilizações","codigo":"1.8.81.000.0001","tipo":"ativo","icon":"🏗️","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18825500003","nome":"IR - Valores Pagos a Maior","codigo":"1.8.82.550.0003","tipo":"ativo","icon":"💰","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18825500004","nome":"CSLL - Valores Pagos a Maior","codigo":"1.8.82.550.0004","tipo":"ativo","icon":"💰","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18840200001","nome":"Bloqueio Judicial Banco do Brasil","codigo":"1.8.84.020.0001","tipo":"ativo","icon":"⚖️","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18840209999","nome":"Depósito Judicial Ações Trabalhistas","codigo":"1.8.84.020.9999","tipo":"ativo","icon":"⚖️","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18845100001","nome":"IRRF s/ Prestação de Serviço","codigo":"1.8.84.510.0001","tipo":"ativo","icon":"💰","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-18845100003","nome":"IRRF Antecipado","codigo":"1.8.84.510.0003","tipo":"ativo","icon":"💰","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-18845900004","nome":"COFINS a Recuperar","codigo":"1.8.84.590.0004","tipo":"ativo","icon":"🔖","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18845900007","nome":"Retenções s/ Valores Intermediados","codigo":"1.8.84.590.0007","tipo":"ativo","icon":"🔖","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18845900011","nome":"IRRF s/ Valores Intermediados","codigo":"1.8.84.590.0011","tipo":"ativo","icon":"🔖","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18850000001","nome":"IRRF s/ Aplicação","codigo":"1.8.85.000.0001","tipo":"ativo","icon":"📈","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-18892000003","nome":"Outros Valores a Receber","codigo":"1.8.89.200.0003","tipo":"ativo","icon":"📄","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-19910000001","nome":"Seguros a Apropriar","codigo":"1.9.91.000.0001","tipo":"ativo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-19910000002","nome":"Assinatura de Periódicos","codigo":"1.9.91.000.0002","tipo":"ativo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-19910000003","nome":"Contrato de Manutenção","codigo":"1.9.91.000.0003","tipo":"ativo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-19910000004","nome":"IPTU","codigo":"1.9.91.000.0004","tipo":"ativo","icon":"🏢","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-19910009999","nome":"Despesas Antecipadas Diversas","codigo":"1.9.91.000.9999","tipo":"ativo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-22530100001","nome":"Móveis e Utensílios","codigo":"2.2.53.010.0001","tipo":"ativo","icon":"🪑","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-22530200001","nome":"Equipamentos de Processamento de Dados","codigo":"2.2.53.020.0001","tipo":"ativo","icon":"💻","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-22530900001","nome":"Máquinas e Equipamentos","codigo":"2.2.53.090.0001","tipo":"ativo","icon":"⚙️","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-22599300001","nome":"Depreciação Móveis/Utensílios (-)","codigo":"2.2.59.930.0001","tipo":"ativo","icon":"📉","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-22599300002","nome":"Depreciação Máquinas/Equipamentos (-)","codigo":"2.2.59.930.0002","tipo":"ativo","icon":"📉","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-22599900001","nome":"Depreciação Equipamentos de Proc. (-)","codigo":"2.2.59.990.0001","tipo":"ativo","icon":"📉","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-25115100001","nome":"Software - Adquiridos","codigo":"2.5.11.510.0001","tipo":"ativo","icon":"💿","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-25115200001","nome":"Software - Gerados Internamente","codigo":"2.5.11.520.0001","tipo":"ativo","icon":"💿","empresas":["nc"],"campos":_campos_imob,"wip":False},
    {"id":"nc-25130000001","nome":"Marcas","codigo":"2.5.13.000.0001","tipo":"ativo","icon":"™️","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-25190000001","nome":"Desenvolvimento de Produtos","codigo":"2.5.19.000.0001","tipo":"ativo","icon":"🔬","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-25198000005","nome":"Intangível em Desenvolvimento","codigo":"2.5.19.800.0005","tipo":"ativo","icon":"🔬","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-25199000002","nome":"Amort. Acumulada Ativos Intangíveis (-)","codigo":"2.5.19.900.0002","tipo":"ativo","icon":"📉","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-25199150001","nome":"(-) Amortização Softwares","codigo":"2.5.19.915.0001","tipo":"ativo","icon":"📉","empresas":["nc"],"campos":_campos_simples,"wip":False},

    # ════════════════════════════════════════════════════════
    # NUTRICASH — PASSIVO
    # ════════════════════════════════════════════════════════
    {"id":"nc-49410000001","nome":"Imposto de Renda a Recolher","codigo":"4.9.41.000.0001","tipo":"passivo","icon":"💰","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49410000002","nome":"Contribuição Social a Recolher","codigo":"4.9.41.000.0002","tipo":"passivo","icon":"💰","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420100001","nome":"IRRF s/ Serviços a Recolher (1708)","codigo":"4.9.42.010.0001","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420100002","nome":"IRRF s/ Comissões a Recolher (8045)","codigo":"4.9.42.010.0002","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420100003","nome":"PIS/COFINS/CSLL s/ Serviços (5952)","codigo":"4.9.42.010.0003","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420100004","nome":"INSS s/ Serviços a Recolher","codigo":"4.9.42.010.0004","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420100007","nome":"ISS Retido na Fonte","codigo":"4.9.42.010.0007","tipo":"passivo","icon":"🏙️","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420200001","nome":"INSS a Recolher","codigo":"4.9.42.020.0001","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420200002","nome":"FGTS a Recolher","codigo":"4.9.42.020.0002","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420200003","nome":"IRRF s/ Rendimento Trabalho Assalariado","codigo":"4.9.42.020.0003","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420200004","nome":"Contribuição Sindical a Recolher","codigo":"4.9.42.020.0004","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420900001","nome":"PIS a Recolher","codigo":"4.9.42.090.0001","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420900002","nome":"COFINS a Recolher","codigo":"4.9.42.090.0002","tipo":"passivo","icon":"🔖","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420900003","nome":"ISS a Recolher","codigo":"4.9.42.090.0003","tipo":"passivo","icon":"🏙️","empresas":["nc"],"campos":_campos_tributo,"wip":False},
    {"id":"nc-49420900005","nome":"Parc. Adm. Débitos Federais CP","codigo":"4.9.42.090.0005","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49420900007","nome":"Parc. Adm. Débitos Federais LP","codigo":"4.9.42.090.0007","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49420900009","nome":"Parc. Adm. Débitos Municipais","codigo":"4.9.42.090.0009","tipo":"passivo","icon":"📋","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49930100004","nome":"Provisão de 13º Salário a Pagar","codigo":"4.9.93.010.0004","tipo":"passivo","icon":"💼","empresas":["nc"],"campos":_campos_provisao,"wip":False},
    {"id":"nc-49930100007","nome":"Provisão de Férias a Pagar","codigo":"4.9.93.010.0007","tipo":"passivo","icon":"🏖️","empresas":["nc"],"campos":_campos_provisao,"wip":False},
    {"id":"nc-49992000001","nome":"Fornecedores","codigo":"4.9.99.200.0001","tipo":"passivo","icon":"🤝","empresas":["nc"],"campos":_campos_fornec,"wip":False},
    {"id":"nc-49992000002","nome":"Rede Conveniada a Pagar","codigo":"4.9.99.200.0002","tipo":"passivo","icon":"🏪","empresas":["nc"],"campos":_campos_fornec,"wip":False},
    {"id":"nc-49992000003","nome":"Moeda Eletrônica - PAT","codigo":"4.9.99.200.0003","tipo":"passivo","icon":"🃏","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000004","nome":"Moeda Eletrônica - Frota","codigo":"4.9.99.200.0004","tipo":"passivo","icon":"⛽","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000005","nome":"Moeda Eletrônica - Nutricash Premium","codigo":"4.9.99.200.0005","tipo":"passivo","icon":"⭐","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000007","nome":"Transitória Transações Pré - PAT","codigo":"4.9.99.200.0007","tipo":"passivo","icon":"🔄","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000008","nome":"Transitória Transações Pré - Frota","codigo":"4.9.99.200.0008","tipo":"passivo","icon":"🔄","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000009","nome":"Transitória Transações Pré - NC Premium","codigo":"4.9.99.200.0009","tipo":"passivo","icon":"🔄","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000014","nome":"Adiantamento de Clientes","codigo":"4.9.99.200.0014","tipo":"passivo","icon":"💼","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000022","nome":"Moeda Eletrônica - PAT Papel","codigo":"4.9.99.200.0022","tipo":"passivo","icon":"🃏","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000023","nome":"Moeda Eletrônica - Frota Papel","codigo":"4.9.99.200.0023","tipo":"passivo","icon":"⛽","empresas":["nc"],"campos":_campos_simples,"wip":False},
    {"id":"nc-49992000099","nome":"Outras Contas a Pagar","codigo":"4.9.99.200.0099","tipo":"passivo","icon":"📄","empresas":["nc"],"campos":_campos_simples,"wip":False},

    # ════════════════════════════════════════════════════════
    # MAXIFROTA — ATIVO
    # ════════════════════════════════════════════════════════
    {"id":"mf-11110000001","nome":"Caixa","codigo":"1.1.11.000.0001","tipo":"ativo","icon":"💵","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-11230000002","nome":"Banco do Brasil - 21122-2","codigo":"1.1.23.000.0002","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000101","nome":"Santander - 13005708-6","codigo":"1.1.23.000.0101","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000201","nome":"Caixa Econômica Federal - 2617-5","codigo":"1.1.23.000.0201","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000301","nome":"Bradesco - 0002901-7","codigo":"1.1.23.000.0301","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000401","nome":"Safra - 401811-6","codigo":"1.1.23.000.0401","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000501","nome":"Banese - 130695-9","codigo":"1.1.23.000.0501","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000605","nome":"Itaú - 60527-5","codigo":"1.1.23.000.0605","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000606","nome":"Itaú - 36651-1","codigo":"1.1.23.000.0606","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000607","nome":"Itaú - 36985-3","codigo":"1.1.23.000.0607","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000608","nome":"Banco Daycoval - 749245-8","codigo":"1.1.23.000.0608","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000611","nome":"Itaú - 0098692-0","codigo":"1.1.23.000.0611","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000950","nome":"Banco Sofisa - 52-1","codigo":"1.1.23.000.0950","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230000960","nome":"Sicredi - 01182-3","codigo":"1.1.23.000.0960","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-11230001001","nome":"Transpocred","codigo":"1.1.23.000.1001","tipo":"ativo","icon":"🏦","empresas":["mf"],"campos":_campos_banco,"wip":False},
    {"id":"mf-13115300001","nome":"Itaú 60527 (Aplicação)","codigo":"1.3.11.530.0001","tipo":"ativo","icon":"📈","empresas":["mf"],"campos":_campos_aplicacao,"wip":False},
    {"id":"mf-13115300201","nome":"Santander (Aplicação)","codigo":"1.3.11.530.0201","tipo":"ativo","icon":"📈","empresas":["mf"],"campos":_campos_aplicacao,"wip":False},
    {"id":"mf-13115300500","nome":"Bradesco (Aplicação)","codigo":"1.3.11.530.0500","tipo":"ativo","icon":"📈","empresas":["mf"],"campos":_campos_aplicacao,"wip":False},
    {"id":"mf-13115300900","nome":"Banco Sofisa (Aplicação)","codigo":"1.3.11.530.0900","tipo":"ativo","icon":"📈","empresas":["mf"],"campos":_campos_aplicacao,"wip":False},
    {"id":"mf-13115300960","nome":"Sicredi (Aplicação)","codigo":"1.3.11.530.0960","tipo":"ativo","icon":"📈","empresas":["mf"],"campos":_campos_aplicacao,"wip":False},
    {"id":"mf-18803000001","nome":"Adiantamento de Salários","codigo":"1.8.80.300.0001","tipo":"ativo","icon":"💼","empresas":["mf"],"campos":_campos_adto,"wip":False},
    {"id":"mf-18803000002","nome":"Adiantamento de 13º Salário","codigo":"1.8.80.300.0002","tipo":"ativo","icon":"💼","empresas":["mf"],"campos":_campos_adto,"wip":False},
    {"id":"mf-18803000003","nome":"Adiantamento de Férias","codigo":"1.8.80.300.0003","tipo":"ativo","icon":"🏖️","empresas":["mf"],"campos":_campos_adto,"wip":False},
    {"id":"mf-18803000004","nome":"Empréstimos Concedidos","codigo":"1.8.80.300.0004","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18805000001","nome":"Adiantamento para Viagens","codigo":"1.8.80.500.0001","tipo":"ativo","icon":"✈️","empresas":["mf"],"campos":_campos_adto,"wip":False},
    {"id":"mf-18805000002","nome":"Adiantamento a Funcionários (Desp. Adm.)","codigo":"1.8.80.500.0002","tipo":"ativo","icon":"💼","empresas":["mf"],"campos":_campos_adto,"wip":False},
    {"id":"mf-18805000003","nome":"Adiantamento a Fornecedores","codigo":"1.8.80.500.0003","tipo":"ativo","icon":"🏭","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18825500001","nome":"IR - Valores Diferidos","codigo":"1.8.82.550.0001","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18825500002","nome":"CSLL - Valores Diferidos","codigo":"1.8.82.550.0002","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18825500003","nome":"IR - Valores Pagos a Maior","codigo":"1.8.82.550.0003","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18825500004","nome":"CSLL - Valores Pagos a Maior","codigo":"1.8.82.550.0004","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18845100001","nome":"IRRF s/ Prestação de Serviço","codigo":"1.8.84.510.0001","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-18845100002","nome":"IRRF a Recuperar","codigo":"1.8.84.510.0002","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18845100003","nome":"IRRF Antecipado","codigo":"1.8.84.510.0003","tipo":"ativo","icon":"💰","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-18845200002","nome":"CSLL a Recuperar","codigo":"1.8.84.520.0002","tipo":"ativo","icon":"🔖","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18880200005","nome":"Emissor Nutricash","codigo":"1.8.88.020.0005","tipo":"ativo","icon":"📄","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18892000004","nome":"Caucões","codigo":"1.8.89.200.0004","tipo":"ativo","icon":"🔐","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-18892000005","nome":"Chargeback","codigo":"1.8.89.200.0005","tipo":"ativo","icon":"🔄","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-19910000003","nome":"Contrato de Manutenção","codigo":"1.9.91.000.0003","tipo":"ativo","icon":"📋","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-19910000004","nome":"IPTU","codigo":"1.9.91.000.0004","tipo":"ativo","icon":"🏢","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-19910009999","nome":"Despesas Antecipadas Diversas","codigo":"1.9.91.000.9999","tipo":"ativo","icon":"📋","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-22530100001","nome":"Móveis e Utensílios","codigo":"2.2.53.010.0001","tipo":"ativo","icon":"🪑","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-22550000001","nome":"Benfeitorias em Imóveis de Terceiros","codigo":"2.2.55.000.0001","tipo":"ativo","icon":"🏢","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-22530200001","nome":"Equipamentos de Processamento de Dados","codigo":"2.2.53.020.0001","tipo":"ativo","icon":"💻","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-22530900001","nome":"Máquinas e Equipamentos","codigo":"2.2.53.090.0001","tipo":"ativo","icon":"⚙️","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-25115100001","nome":"Software - Adquiridos","codigo":"2.5.11.510.0001","tipo":"ativo","icon":"💿","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-25115200001","nome":"Software - Gerados Internamente","codigo":"2.5.11.520.0001","tipo":"ativo","icon":"💿","empresas":["mf"],"campos":_campos_imob,"wip":False},
    {"id":"mf-25130000001","nome":"Marcas","codigo":"2.5.13.000.0001","tipo":"ativo","icon":"™️","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-25198000005","nome":"Intangível em Desenvolvimento","codigo":"2.5.19.800.0005","tipo":"ativo","icon":"🔬","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-25199000002","nome":"Amort. Acumulada Ativos Intangíveis (-)","codigo":"2.5.19.900.0002","tipo":"ativo","icon":"📉","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-25199150001","nome":"(-) Amortização Softwares","codigo":"2.5.19.915.0001","tipo":"ativo","icon":"📉","empresas":["mf"],"campos":_campos_simples,"wip":False},

    # ════════════════════════════════════════════════════════
    # MAXIFROTA — PASSIVO
    # ════════════════════════════════════════════════════════
    {"id":"mf-49410000001","nome":"Imposto de Renda a Recolher","codigo":"4.9.41.000.0001","tipo":"passivo","icon":"💰","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49410000002","nome":"Contribuição Social a Recolher","codigo":"4.9.41.000.0002","tipo":"passivo","icon":"💰","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100001","nome":"IRRF s/ Serviços a Recolher (1708)","codigo":"4.9.42.010.0001","tipo":"passivo","icon":"📋","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100002","nome":"IRRF s/ Comissões a Recolher (8045)","codigo":"4.9.42.010.0002","tipo":"passivo","icon":"📋","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100003","nome":"PIS/COFINS/CSLL s/ Serviços (5952)","codigo":"4.9.42.010.0003","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100004","nome":"INSS s/ Serviços a Recolher","codigo":"4.9.42.010.0004","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100007","nome":"ISS Retido na Fonte","codigo":"4.9.42.010.0007","tipo":"passivo","icon":"🏙️","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420100009","nome":"IRRF s/ Serviços a Recolher (3426)","codigo":"4.9.42.010.0009","tipo":"passivo","icon":"📋","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420200001","nome":"INSS a Recolher","codigo":"4.9.42.020.0001","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420200002","nome":"FGTS a Recolher","codigo":"4.9.42.020.0002","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420200003","nome":"IRRF s/ Rendimento Trabalho Assalariado","codigo":"4.9.42.020.0003","tipo":"passivo","icon":"📋","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420900001","nome":"PIS a Recolher","codigo":"4.9.42.090.0001","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420900002","nome":"COFINS a Recolher","codigo":"4.9.42.090.0002","tipo":"passivo","icon":"🔖","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420900003","nome":"ISS a Recolher","codigo":"4.9.42.090.0003","tipo":"passivo","icon":"🏙️","empresas":["mf"],"campos":_campos_tributo,"wip":False},
    {"id":"mf-49420900009","nome":"Parc. Adm. Débitos Municipais","codigo":"4.9.42.090.0009","tipo":"passivo","icon":"📋","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49930100004","nome":"Provisão de 13º Salário a Pagar","codigo":"4.9.93.010.0004","tipo":"passivo","icon":"💼","empresas":["mf"],"campos":_campos_provisao,"wip":False},
    {"id":"mf-49930100007","nome":"Provisão de Férias a Pagar","codigo":"4.9.93.010.0007","tipo":"passivo","icon":"🏖️","empresas":["mf"],"campos":_campos_provisao,"wip":False},
    {"id":"mf-49930100011","nome":"Folha a Pagar","codigo":"4.9.93.010.0011","tipo":"passivo","icon":"💼","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000001","nome":"Fornecedores","codigo":"4.9.99.200.0001","tipo":"passivo","icon":"🤝","empresas":["mf"],"campos":_campos_fornec,"wip":False},
    {"id":"mf-49992000002","nome":"Rede Conveniada a Pagar","codigo":"4.9.99.200.0002","tipo":"passivo","icon":"🏪","empresas":["mf"],"campos":_campos_fornec,"wip":False},
    {"id":"mf-49992000004","nome":"Moeda Eletrônica - Frota","codigo":"4.9.99.200.0004","tipo":"passivo","icon":"⛽","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000007","nome":"Transitória Transações Pré - PAT","codigo":"4.9.99.200.0007","tipo":"passivo","icon":"🔄","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000008","nome":"Transitória Transações Pré - Frota","codigo":"4.9.99.200.0008","tipo":"passivo","icon":"🔄","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000014","nome":"Adiantamento de Clientes","codigo":"4.9.99.200.0014","tipo":"passivo","icon":"💼","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000016","nome":"Empréstimo Consignado Colaboradores","codigo":"4.9.99.200.0016","tipo":"passivo","icon":"💰","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000023","nome":"Moeda Eletrônica - Frota Papel","codigo":"4.9.99.200.0023","tipo":"passivo","icon":"⛽","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000027","nome":"Transações MX","codigo":"4.9.99.200.0027","tipo":"passivo","icon":"🔄","empresas":["mf"],"campos":_campos_simples,"wip":False},
    {"id":"mf-49992000099","nome":"Outras Contas a Pagar","codigo":"4.9.99.200.0099","tipo":"passivo","icon":"📄","empresas":["mf"],"campos":_campos_simples,"wip":False},
]

# ══════════════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════════════
for k, v in [("page","login"),("logado",False),("usuario_atual",None),
             ("empresa",None),("conta",None),("tab","dashboard"),
             ("historico",[]),("status",{}),("resultado",None),("login_erro",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def fmt_br(v):
    if v is None: return "—"
    try: return f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "—"

def parse_br(t):
    if not t: return 0.0
    try: return float(t.strip().replace(".","").replace(",","."))
    except: return 0.0

def calcular(campos, valores):
    sR = valores[-1] if valores else 0.0
    tA = valores[0] if len(campos)==2 else sum(
        v if i%2==0 else -v for i,v in enumerate(valores[:-1]))
    diff = sR - tA
    return {"sR":sR,"tA":tA,"diff":diff,"ok":abs(diff)<0.01}

def get_status(emp_id, conta_id):
    return st.session_state.status.get(f"{emp_id}_{conta_id}", "pendente")

def set_status(emp_id, conta_id, val):
    st.session_state.status[f"{emp_id}_{conta_id}"] = val

def add_historico(item):
    h = [x for x in st.session_state.historico
         if not (x["emp"]==item["emp"] and x["id"]==item["id"] and x["ref"]==item["ref"])]
    h.append(item); st.session_state.historico = h

def get_contas(emp_id):
    return [c for c in CONTAS if emp_id in c["empresas"]]

def perfil_ok(emp_id):
    u = USUARIOS.get(st.session_state.usuario_atual or "",{})
    p = u.get("perfil",""); return p=="admin" or p==emp_id

def uinfo(): return USUARIOS.get(st.session_state.usuario_atual or "",{})

def status_html(st_val):
    if st_val=="ok":
        return '<span class="status-ok">✅ CONCILIADA</span>'
    elif st_val=="conciliando":
        return '<span class="status-conc">🔵 CONCILIANDO</span>'
    else:
        return '<span class="status-pend">🔴 PENDENTE</span>'

def auto_fill(rows, campos):
    flat=[]
    for row in rows:
        if not row: continue
        row=list(row)
        for ci in range(len(row)):
            cell=row[ci]
            if isinstance(cell,str) and cell.strip():
                for j in range(ci+1,len(row)):
                    if isinstance(row[j],(int,float)):
                        flat.append({"lbl":cell.strip().lower(),"val":abs(float(row[j]))}); break
    def find(kws):
        for kw in kws:
            hit=next((f["val"] for f in flat if kw in f["lbl"]),None)
            if hit is not None: return hit
        return None
    kw_r=["saldo razão","saldo razao","razão ","razao "]
    kw_a=["saldo relat","posição","posicao","saldo auxiliar","saldo da conta","saldo em conta","saldo extrato"]
    kw_i=["saldo inicial","saldo anterior"]
    kw_e=["adiantamento","retenção","retencao","apurado","emissão","emissao","transaç","nf recebid","valor apurado","retido no período"]
    kw_s=["baixa","recolhimento","compensaç","resgate","repasse","pagamento realiz"]
    result={}
    if len(campos)==2:
        v=find(kw_a) or find(kw_i)
        if v is not None: result[campos[0]]=v
        v=find(kw_r)
        if v is not None: result[campos[1]]=v
    else:
        vals={"ini":find(kw_i),"entr":find(kw_e),"saida":find(kw_s),"razao":find(kw_r),"aux":find(kw_a)}
        for i,campo in enumerate(campos):
            n=campo.lower(); v=None
            if "razã" in n or "razao" in n: v=vals["razao"]
            elif "inicial" in n or "anterior" in n: v=vals["ini"]
            elif "auxiliar" in n or "relat" in n or "extrato" in n: v=vals["aux"]
            elif any(k in n for k in ["saída","saida","baixa","recolh","compensaç","resgate","repasse","pagamento"]): v=vals["saida"]
            else: v=vals["entr"]
            if v is not None: result[campo]=v
    return result

def read_upload(file_bytes,filename):
    try:
        ext=filename.rsplit(".",1)[-1].lower()
        buf=io.BytesIO(file_bytes)
        if ext=="xlsx": df=pd.read_excel(buf,header=None,engine="openpyxl")
        elif ext=="xls":
            try: df=pd.read_excel(buf,header=None,engine="xlrd")
            except: df=pd.read_excel(buf,header=None)
        elif ext in("csv","txt"):
            try: df=pd.read_csv(buf,header=None,sep=None,engine="python")
            except: df=pd.read_csv(io.BytesIO(file_bytes),header=None,sep=";")
        elif ext=="json":
            import json; df=pd.DataFrame(json.loads(file_bytes))
        else: df=pd.read_excel(buf,header=None,engine="openpyxl")
        return df.values.tolist()
    except: return []

def gerar_excel(conta,emp,valores,ref_label,calc):
    campos=conta["campos"]
    rows=[[f"CONCILIAÇÃO — {conta['nome'].upper()}","",""],
          [f"{emp['razao']}  |  Conta: {conta['codigo']}  |  Ref.: {ref_label}","",""],
          ["","",""],["Descrição","Valor (R$)","D/C"]]
    for i,(c,v) in enumerate(zip(campos[:-1],valores[:-1])):
        rows.append([c,v,"D" if i%2==0 else "C"])
    rows+=[ ["Total Auxiliar",calc["tA"],""],["Saldo Razão",calc["sR"],""],
            ["DIFERENÇA",calc["diff"],"ZERADA" if calc["ok"] else "REVISAR"],
            ["","",""],
            [f"Emitido em: {datetime.date.today().strftime('%d/%m/%Y')}","",""]]
    buf=io.BytesIO()
    pd.DataFrame(rows).to_excel(buf,index=False,header=False,engine="openpyxl")
    return buf.getvalue()

def _logout():
    for k in ["logado","usuario_atual","empresa","conta","tab","historico","status","resultado","login_erro"]:
        st.session_state.pop(k,None)
    st.session_state.page="login"; st.rerun()

def _topbar(bg,titulo,usuario_nome,empresa_nome=None):
    emp_part=f'<div class="topbar-div"></div><span class="topbar-title" style="color:rgba(255,255,255,.95);font-size:13px;font-weight:700;text-transform:none;letter-spacing:0">{empresa_nome}</span>' if empresa_nome else ""
    st.markdown(f"""
    <div class="topbar" style="background:{bg}">
      <div class="topbar-l">
        <span style="font-size:20px">📊</span>
        <div class="topbar-div"></div>
        <span class="topbar-title">{titulo}</span>
        {emp_part}
      </div>
      <div class="topbar-user">👤 {usuario_nome}</div>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════
def page_login():
    st.markdown("""<div style="position:fixed;inset:0;background:linear-gradient(135deg,#1C3557 0%,#2c6694 55%,#2196C4 100%);z-index:-1"></div>""",unsafe_allow_html=True)
    st.markdown("<br><br>",unsafe_allow_html=True)
    _,col,_=st.columns([1,1.1,1])
    with col:
        st.markdown("""
        <div style="background:#fff;border-radius:16px;padding:44px 40px 36px;box-shadow:0 24px 64px rgba(0,0,0,.30);">
          <div style="text-align:center;margin-bottom:28px">
            <div style="font-size:52px;margin-bottom:8px">📊</div>
            <div style="font-size:21px;font-weight:700;color:#1C3557">Conciliação Contábil</div>
            <div style="font-size:12px;color:#718096;margin-top:4px">Acesso restrito — faça login para continuar</div>
          </div>
        </div>""",unsafe_allow_html=True)
        if st.session_state.login_erro:
            st.error("❌ Usuário ou senha incorretos.")
        with st.form("form_login"):
            usuario=st.text_input("👤 Usuário",placeholder="Digite seu usuário")
            senha=st.text_input("🔒 Senha",placeholder="Digite sua senha",type="password")
            st.markdown("<br>",unsafe_allow_html=True)
            entrar=st.form_submit_button("🔐  ENTRAR",use_container_width=True,type="primary")
        if entrar:
            u=USUARIOS.get(usuario.strip().lower())
            if u and u["hash"]==hashlib.sha256(senha.encode()).hexdigest():
                st.session_state.logado=True
                st.session_state.usuario_atual=usuario.strip().lower()
                st.session_state.login_erro=False
                perfil=u["perfil"]
                if perfil=="admin": st.session_state.page="empresa"
                else: st.session_state.empresa=perfil; st.session_state.page="dashboard"
                st.rerun()
            else:
                st.session_state.login_erro=True; st.rerun()
        st.markdown("""
        <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:6px;padding:12px 14px;font-size:11px;color:#0369A1;margin-top:16px;line-height:2.1">
          <strong>Credenciais de demonstração:</strong><br>
          👤 <code>admin</code> · 🔒 <code>admin123</code> — Acesso total<br>
          👤 <code>nutricash</code> · 🔒 <code>nc2024</code> — Somente Nutricash<br>
          👤 <code>maxifrota</code> · 🔒 <code>mf2024</code> — Somente MaxiFrota
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# EMPRESA SELECT
# ══════════════════════════════════════════════════════════════════════
def page_empresa():
    u=uinfo(); _topbar("#1C3557","Conciliação Contábil",u.get("nome",""))
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:22px;font-weight:700;color:#2D3748;letter-spacing:-.02em">Selecione a empresa</div>',unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:13px;color:#718096;margin-bottom:36px">Escolha a empresa para acessar o módulo de conciliação contábil</div>',unsafe_allow_html=True)
    _,col_nc,col_mf,_=st.columns([1,2,2,1])
    for col,eid,nome,desc,border,emoji in [
        (col_nc,"nc","Nutricash","Benefícios, alimentação e gestão de pagamentos corporativos","#2196C4","🏢"),
        (col_mf,"mf","MaxiFrota","Gestão de frotas, abastecimento e mobilidade corporativa","#F5A800","🚛"),
    ]:
        with col:
            disabled=not perfil_ok(eid)
            op="0.4" if disabled else "1"
            bd="#CBD5E1" if disabled else border
            st.markdown(f"""
            <div style="background:#fff;border:1.5px solid {bd};border-radius:12px;padding:36px 28px;
                 text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);opacity:{op}">
              <div style="font-size:46px;margin-bottom:12px">{emoji}</div>
              <div style="font-size:17px;font-weight:700;color:#2D3748;margin-bottom:6px">{nome}</div>
              <div style="font-size:12px;color:#718096;line-height:1.5;margin-bottom:16px">{desc}</div>
            </div>""",unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            if not disabled:
                if st.button(f"ACESSAR → {nome}",use_container_width=True,type="primary" if eid=="nc" else "secondary",key=f"btn_{eid}"):
                    st.session_state.empresa=eid; st.session_state.page="dashboard"; st.rerun()
            else:
                st.button("⛔ Sem permissão",use_container_width=True,disabled=True,key=f"btn_{eid}_d")
    st.markdown("<br><br>",unsafe_allow_html=True)
    _,mc,_=st.columns([3,2,3])
    with mc:
        if st.button("🚪 Sair do sistema",use_container_width=True): _logout()

# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════
def page_dashboard():
    emp_id=st.session_state.empresa; emp=EMPRESAS[emp_id]
    contas=get_contas(emp_id); u=uinfo()
    _topbar(emp["hdr"],"CONCILIAÇÃO CONTÁBIL",u.get("nome",""),emp["nome"])

    with st.sidebar:
        st.markdown(f'<div class="sb-lbl">{emp["razao"]}</div>',unsafe_allow_html=True)
        tabs=["📊 Painel","🕐 Histórico"]
        nav=st.radio("nav",tabs,label_visibility="collapsed",
                     index=0 if st.session_state.tab=="dashboard" else 1)
        st.session_state.tab="dashboard" if "Painel" in nav else "historico"
        st.markdown("---")
        _sidebar_contas(contas,emp_id,"ativo","ATIVO")
        _sidebar_contas(contas,emp_id,"passivo","PASSIVO")
        st.markdown("---")
        if uinfo().get("perfil")=="admin":
            if st.button("↩ Trocar Empresa",use_container_width=True):
                st.session_state.page="empresa"; st.session_state.empresa=None; st.rerun()
        if st.button("🚪 Sair",use_container_width=True): _logout()

    if st.session_state.tab=="dashboard": _dash(emp,contas,emp_id)
    else: _historico(emp,emp_id)

def _sidebar_contas(contas,emp_id,tipo,titulo):
    grupo=[c for c in contas if c["tipo"]==tipo]
    if not grupo: return
    st.markdown(f'<div class="sb-lbl">{titulo}</div>',unsafe_allow_html=True)
    for c in grupo:
        nome_c=c["nome"][:26]+("…" if len(c["nome"])>26 else "")
        if c["wip"]:
            st.markdown(f'<div class="sb-conta" style="opacity:.45">{c["icon"]} {nome_c} <span style="font-size:9px;color:#CBD5E1">EM BREVE</span></div>',unsafe_allow_html=True)
            continue
        st_val=get_status(emp_id,c["id"])
        dot=f'<span class="dot-{"ok" if st_val=="ok" else ("conc" if st_val=="conciliando" else "pend")}"></span>'
        st.markdown(f'<div class="sb-conta">{c["icon"]} {nome_c} {dot}</div>',unsafe_allow_html=True)
        if st.button("→",key=f"sb_{c['id']}",help=c["nome"]):
            st.session_state.conta=c; st.session_state.page="modulo"
            st.session_state.resultado=None; st.rerun()

def _dash(emp,contas,emp_id):
    contas_ativas=[c for c in contas if not c["wip"]]
    ok_n  =sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="ok")
    pend_n=sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="pendente")
    conc_n=sum(1 for c in contas_ativas if get_status(emp_id,c["id"])=="conciliando")
    hist  =[h for h in st.session_state.historico if h["emp"]==emp_id]

    st.markdown(f'<div style="font-size:19px;font-weight:700;color:#2D3748;margin:16px 0 3px;letter-spacing:-.02em">Painel — {emp["nome"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:12px;color:#718096;margin-bottom:20px">{emp["razao"]} · {len(contas)} contas · {ok_n} OK · {pend_n} pendentes</div>',unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 Selecione uma conta no menu lateral ou nos cards abaixo para iniciar a conciliação.</div>',unsafe_allow_html=True)

    k1,k2,k3,k4=st.columns(4)
    for col,ico,bg,cor,lbl,val,sub in [
        (k1,"✅","#E8F8EF","#27AE60","Contas OK",ok_n,"Conciliadas"),
        (k2,"🔴","#FEF3E7","#E67E22","Pendentes",pend_n,"Aguardando"),
        (k3,"🔵","#EBF5FB",emp["acc"],"Conciliando",conc_n,"Em andamento"),
        (k4,"🕐","#F5F6F7","#718096","Histórico",len(hist),"Registros"),
    ]:
        col.markdown(f'<div class="kpi"><div class="kpi-ico" style="background:{bg}">{ico}</div><div><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="color:{cor}">{val}</div><div class="kpi-sub">{sub}</div></div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    cl,cr=st.columns(2)
    with cl:
        st.markdown('<div class="card"><div class="card-hdr"><span class="card-title">Status das Contas</span></div><div class="card-body">',unsafe_allow_html=True)
        fig=go.Figure(data=[go.Pie(labels=["OK","Pendente","Conciliando"],
            values=[max(ok_n,0),max(pend_n,0),max(conc_n,0)],hole=0.55,
            marker_colors=["#27AE60","#E67E22","#2196C4"],textinfo="label+value",textfont_size=11)])
        fig.update_layout(margin=dict(t=10,b=10,l=0,r=0),height=200,showlegend=False,paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div></div>',unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="card"><div class="card-hdr"><span class="card-title">Últimas Conciliações</span></div><div class="card-body">',unsafe_allow_html=True)
        rec=hist[-5:][::-1]
        if rec:
            for h in rec:
                pill="status-ok" if h["ok"] else "status-pend"
                txt="✅ OK" if h["ok"] else "🔴 DIVERGÊNCIA"
                st.markdown(f'<div class="hist-row"><div><span>{h["ico"]}</span><span class="hist-nome" style="margin-left:6px">{h["conta"]}</span><div class="hist-ref">{h["ref"]}</div></div><span class="{pill}">{txt}</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:24px;color:#A0AEC0"><div style="font-size:32px">📭</div><div>Nenhuma conciliação realizada</div></div>',unsafe_allow_html=True)
        st.markdown('</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-hdr"><span class="card-title">Todas as Contas</span><span style="font-size:11px;color:#A0AEC0">{} conta(s)</span></div><div class="card-body">'.format(len(contas)),unsafe_allow_html=True)
    for tipo in ["ativo","passivo"]:
        grupo=[c for c in contas if c["tipo"]==tipo]
        if not grupo: continue
        st.markdown(f'<div class="tipo-lbl">{tipo.upper()}</div>',unsafe_allow_html=True)
        cols=st.columns(4)
        for i,c in enumerate(grupo):
            with cols[i%4]:
                st_val=get_status(emp_id,c["id"]) if not c["wip"] else "wip"
                st_html=status_html(st_val) if not c["wip"] else '<span class="status-none">EM BREVE</span>'
                badge="badge-ativo" if tipo=="ativo" else "badge-passivo"
                st.markdown(f'<div class="cc {tipo} {"wip" if c["wip"] else ""}"><div class="cc-top"><span class="cc-ico">{c["icon"]}</span><span class="{badge}">{tipo.upper()}</span></div><div class="cc-name">{c["nome"]}</div><div class="cc-cod">{c["codigo"]}</div><div style="margin-top:8px">{st_html}</div></div>',unsafe_allow_html=True)
                if not c["wip"]:
                    if st.button("Abrir",key=f"cc_{c['id']}",use_container_width=True):
                        st.session_state.conta=c; st.session_state.page="modulo"
                        st.session_state.resultado=None; st.rerun()
    st.markdown('</div></div>',unsafe_allow_html=True)

def _historico(emp,emp_id):
    st.markdown(f'<div style="font-size:19px;font-weight:700;color:#2D3748;margin:16px 0 3px">Histórico de Conciliações</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:12px;color:#718096;margin-bottom:18px">{emp["razao"]}</div>',unsafe_allow_html=True)
    hist=[h for h in st.session_state.historico if h["emp"]==emp_id]
    if not hist:
        st.markdown('<div style="text-align:center;padding:40px;color:#A0AEC0"><div style="font-size:34px">📭</div><div style="font-size:14px;font-weight:700;margin-top:8px">Nenhum histórico</div><div>As conciliações processadas aparecerão aqui</div></div>',unsafe_allow_html=True)
        return
    refs=sorted(set(h["ref"] for h in hist),reverse=True)
    fc,sc,_=st.columns([2,2,4])
    filtro_ref=fc.selectbox("Período",["Todos"]+refs,key="h_ref")
    filtro_st=sc.selectbox("Status",["Todos","✅ OK","🔴 Divergência"],key="h_st")
    filtrado=hist[::-1]
    if filtro_ref!="Todos": filtrado=[h for h in filtrado if h["ref"]==filtro_ref]
    if filtro_st=="✅ OK": filtrado=[h for h in filtrado if h["ok"]]
    elif filtro_st=="🔴 Divergência": filtrado=[h for h in filtrado if not h["ok"]]
    if not filtrado: st.info("Nenhum registro com os filtros selecionados."); return
    df=pd.DataFrame([{"Conta":f'{h["ico"]} {h["conta"]}',
                      "Código":h["codigo"],"Período":h["ref"],
                      "Diferença R$":fmt_br(h["diff"]),
                      "Status":"✅ OK" if h["ok"] else "🔴 DIVERGÊNCIA"} for h in filtrado])
    st.dataframe(df,use_container_width=True,hide_index=True)
    buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
    st.download_button("⬇ Exportar Excel",data=buf.getvalue(),
        file_name=f"historico_{emp_id}_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="btn_hist_xls")

# ══════════════════════════════════════════════════════════════════════
# MÓDULO
# ══════════════════════════════════════════════════════════════════════
def page_modulo():
    emp_id=st.session_state.empresa; emp=EMPRESAS[emp_id]
    conta=st.session_state.conta; u=uinfo()
    if not conta: st.session_state.page="dashboard"; st.rerun()
    tipo_bg="#DBEAFE" if conta["tipo"]=="ativo" else "#FCE7F3"
    tipo_color="#1E40AF" if conta["tipo"]=="ativo" else "#9D174D"

    st.markdown(f"""<div class="mod-topbar" style="border-bottom-color:{emp['acc']};border-bottom-width:3px">
      <div style="font-size:11px;color:#A0AEC0">
        <strong style="color:#2D3748">{emp['nome']}</strong> › {conta['tipo'].upper()} › {conta['nome']}
      </div>
      <div style="font-size:11px;color:#A0AEC0">👤 {u.get('nome','')}</div>
    </div>""",unsafe_allow_html=True)

    with st.sidebar:
        if st.button("← Voltar ao Painel",use_container_width=True):
            st.session_state.page="dashboard"; st.session_state.conta=None
            st.session_state.resultado=None; st.rerun()
        st.markdown("---")
        st.markdown(f'<span style="background:{tipo_bg};color:{tipo_color};padding:2px 8px;border-radius:3px;font-size:10px;font-weight:700">{conta["tipo"].upper()}</span>',unsafe_allow_html=True)
        st.markdown(f"<br><strong>{conta['nome']}</strong>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-family:monospace;font-size:11px;color:#718096'>{conta['codigo']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:11px;color:#718096;margin-top:4px'>{emp['razao']}</div>",unsafe_allow_html=True)
        st.markdown("---")
        # Status atual
        st_val=get_status(emp_id,conta["id"])
        st.markdown(status_html(st_val),unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Sair",use_container_width=True): _logout()

    # Cabeçalho da conta
    st.markdown("<div style='padding:22px 0 0'>",unsafe_allow_html=True)
    st.markdown(f'<span style="background:{tipo_bg};color:{tipo_color};padding:3px 9px;border-radius:3px;font-size:10px;font-weight:700;letter-spacing:.04em">{conta["tipo"].upper()}</span>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:22px;font-weight:700;color:#2D3748;margin:6px 0 4px;letter-spacing:-.02em">{conta["nome"]}</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#718096;margin-bottom:22px">Conta: {conta["codigo"]} · {emp["razao"]}</div>',unsafe_allow_html=True)

    # STEP 1
    st.markdown('<div class="step"><div class="step-n">Passo 01 de 02</div><div class="step-h">Período e Documentos</div><div class="step-p">Selecione o mês/ano de referência. Faça upload da planilha auxiliar ou preencha manualmente.</div>',unsafe_allow_html=True)
    now=datetime.date.today()
    cm,ca,_=st.columns([2,1,4])
    mes=cm.selectbox("Mês",[str(i).zfill(2) for i in range(1,13)],
                     format_func=lambda x:MESES[int(x)-1],index=now.month-1,key="ref_mes")
    ano=ca.number_input("Ano",min_value=2020,max_value=2099,value=now.year,step=1,key="ref_ano")
    ref_label=f"{MESES[int(mes)-1]}/{int(ano)}"

    st.markdown("**📂 Relatório Auxiliar — Upload (opcional)**")
    uploaded=st.file_uploader("XLSX / XLS / CSV / TXT / JSON",
                               type=["xlsx","xls","csv","txt","json"],
                               key=f"up_{conta['id']}",label_visibility="collapsed")
    autofill_vals={}
    if uploaded:
        rows=read_upload(uploaded.read(),uploaded.name)
        if rows:
            autofill_vals=auto_fill(rows,conta["campos"])
            if autofill_vals: st.success(f"✅ {len(autofill_vals)} campo(s) preenchido(s) automaticamente de **{uploaded.name}**")
            else: st.info("ℹ️ Arquivo recebido — preencha os valores manualmente.")

    st.markdown("**Valores da Conciliação**")
    campos=conta["campos"]; valores=[]
    idx=0
    for _ in range((len(campos)+2)//3):
        rcols=st.columns(3)
        for ci in range(3):
            if idx>=len(campos): break
            campo=campos[idx]; default=fmt_br(autofill_vals[campo]) if campo in autofill_vals else ""
            with rcols[ci]:
                raw=st.text_input(campo,value=default,placeholder="0,00",key=f"f_{conta['id']}_{idx}")
                valores.append(parse_br(raw))
            idx+=1
    while len(valores)<len(campos): valores.append(0.0)
    st.markdown("</div>",unsafe_allow_html=True)

    all_filled=any(v!=0.0 for v in valores)
    cb,_=st.columns([2,5])
    with cb:
        processar=st.button("⚡ Processar Conciliação",disabled=not all_filled,
                            type="primary",use_container_width=True,key="btn_proc")
    if processar and all_filled:
        calc=calcular(campos,valores)
        add_historico({"emp":emp_id,"id":conta["id"],"conta":conta["nome"],
                       "codigo":conta["codigo"],"ico":conta["icon"],
                       "ref":ref_label,"diff":abs(calc["diff"]),"ok":calc["ok"]})
        set_status(emp_id,conta["id"],"ok" if calc["ok"] else "pendente")
        st.session_state.resultado={"calc":calc,"valores":valores,"campos":campos,
                                    "ref_label":ref_label,"conta":conta,"emp":emp}
    res=st.session_state.resultado
    if res and res.get("conta",{}).get("id")==conta["id"]: _resultado(res)

def _resultado(res):
    calc,valores,campos=res["calc"],res["valores"],res["campos"]
    ref_label,conta,emp=res["ref_label"],res["conta"],res["emp"]
    st.markdown('<div class="step"><div class="step-n">Passo 02 de 02</div><div class="step-h">Resultado da Conciliação</div>',unsafe_allow_html=True)
    st.markdown('<div class="r-kpis">',unsafe_allow_html=True)
    k1,k2,k3=st.columns(3)
    k1.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Saldo Razão</div><div class="r-kpi-val">{fmt_br(calc["sR"])}</div><div class="r-kpi-sub">{ref_label}</div></div>',unsafe_allow_html=True)
    k2.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Rel. Auxiliar</div><div class="r-kpi-val">{fmt_br(calc["tA"])}</div><div class="r-kpi-sub">Composição calculada</div></div>',unsafe_allow_html=True)
    cor="#27AE60" if calc["ok"] else "#E74C3C"
    k3.markdown(f'<div class="r-kpi"><div class="r-kpi-lbl">Diferença</div><div class="r-kpi-val" style="color:{cor}">{fmt_br(abs(calc["diff"]))}</div><div class="r-kpi-sub">{"✓ Zerada" if calc["ok"] else "⚠ Divergência"}</div></div>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown('<div class="r-blk-ttl">Composição do Saldo — Relatório Auxiliar</div>',unsafe_allow_html=True)
    table_rows=[]
    if len(campos)==2: table_rows.append({"Descrição":campos[0],"Valor (R$)":fmt_br(calc["tA"]),"D/C":"D"})
    else:
        for i,(c,v) in enumerate(zip(campos[:-1],valores[:-1])):
            table_rows.append({"Descrição":c,"Valor (R$)":fmt_br(v),"D/C":"D" if i%2==0 else "C"})
        table_rows.append({"Descrição":"Total Auxiliar","Valor (R$)":fmt_br(calc["tA"]),"D/C":""})
    table_rows.append({"Descrição":"Saldo Razão","Valor (R$)":fmt_br(calc["sR"]),"D/C":""})
    st.dataframe(pd.DataFrame(table_rows),use_container_width=True,hide_index=True)

    cls="ok" if calc["ok"] else "nok"
    lbl="✓ Conciliação Zerada" if calc["ok"] else "⚠ Conciliação com Divergência"
    bdg="APROVADA" if calc["ok"] else "REVISAR"
    st.markdown(f'<div class="diff-box {cls}"><div><div class="diff-lbl">{lbl}</div><div style="font-size:11px;margin-top:2px;opacity:.7">Razão ({fmt_br(calc["sR"])}) − Auxiliar ({fmt_br(calc["tA"])})</div></div><div style="display:flex;align-items:center;gap:10px"><div class="diff-val">{fmt_br(abs(calc["diff"]))}</div><span class="diff-bdg">{bdg}</span></div></div>',unsafe_allow_html=True)
    if not calc["ok"]:
        st.markdown(f'<div class="note-box"><strong>⚠ Atenção:</strong> Divergência de <strong>{fmt_br(abs(calc["diff"]))}</strong>. Verifique os lançamentos do período {ref_label}.</div>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    cn,cx,_=st.columns([2,2,5])
    with cn:
        if st.button("← Novo período",key="btn_novo"):
            st.session_state.resultado=None; st.rerun()
    with cx:
        xls=gerar_excel(conta,emp,valores,ref_label,calc)
        st.download_button("⬇ Baixar Excel",data=xls,
            file_name=f"conc_{conta['id']}_{ref_label.replace('/','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="btn_xls")

# ══════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════
if not st.session_state.logado and st.session_state.page!="login":
    st.session_state.page="login"
p=st.session_state.page
if p=="login": page_login()
elif p=="empresa": page_empresa()
elif p=="dashboard":
    if st.session_state.empresa and not perfil_ok(st.session_state.empresa):
        st.error("⛔ Sem permissão para esta empresa.")
        if st.button("Voltar"): st.session_state.page="empresa"; st.rerun()
    else: page_dashboard()
elif p=="modulo": page_modulo()
