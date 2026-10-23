
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
import uuid
import base64
from datetime import datetime

# =========================
# CONFIGURAÇÕES
# =========================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
ARQUIVO = "conversas_chatin.json"
IMAGEM = "image.png"

st.set_page_config(
    page_title="CHATIN",
    page_icon="⚡",
    layout="wide"
)

# =========================
# CONECTAR À GROQ
# =========================

if not API_KEY:
    st.error("Configure GROQ_API_KEY no arquivo .env.")
    st.stop()

client = Groq(api_key=API_KEY)

# =========================
# PERSONALIDADES
# =========================

personalidades = {
    "Nerd 🤓": """
Você é inteligente, curioso e gosta de aprender.
Explique os assuntos claramente e compartilhe curiosidades.
""",

    "Descolado 😎": """
Você é divertido e descontraído.
Use gírias brasileiras naturalmente e fale informalmente.
""",

    "Cria 🔥": """
Você é criativo e cheio de atitude.
Use gírias brasileiras, linguagem informal e ideias originais.
""",

    "Santo 😇": """
Você é sempre educado, gentil e respeitoso.
Responda com paciência e cordialidade. Evite gírias.
""",

    "Tédio 😴": """
Você é Tédio, extremamente preguiçoso.
Quando alguém perguntar algo, diga que não sabe,
que está com preguiça ou que não quer pensar.
Responda de forma curta, engraçada e desinteressada.
Exemplos: "Sei lá, pesquisa no Google 😴",
"Ih, tô com preguiça.", "Não faço ideia e nem quero descobrir."
Mesmo quando souber, finja que não sabe.
"""
}

# =========================
# HISTÓRICO DE CONVERSAS
# =========================

def carregar_conversas():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
                return dados if isinstance(dados, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def salvar_conversas():
    temporario = ARQUIVO + ".tmp"

    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(
            st.session_state.conversas,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    os.replace(temporario, ARQUIVO)


def nova_conversa():
    identificador = str(uuid.uuid4())

    st.session_state.conversas[identificador] = {
        "titulo": "Nova conversa",
        "personalidade": st.session_state.personalidade,
        "mensagens": [],
        "criada_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    st.session_state.conversa_atual = identificador
    salvar_conversas()


# =========================
# INICIALIZAÇÃO
# =========================

if "conversas" not in st.session_state:
    st.session_state.conversas = carregar_conversas()

if "personalidade" not in st.session_state:
    st.session_state.personalidade = "Descolado 😎"

if "conversa_atual" not in st.session_state:
    st.session_state.conversa_atual = None

if st.session_state.conversa_atual not in st.session_state.conversas:
    if st.session_state.conversas:
        st.session_state.conversa_atual = next(
            reversed(st.session_state.conversas)
        )
    else:
        nova_conversa()

# =========================
# FUNDO COM IMAGEM
# =========================

try:
    with open(IMAGEM, "rb") as arquivo_imagem:
        imagem_base64 = base64.b64encode(
            arquivo_imagem.read()
        ).decode()

    fundo = f"""
    background-image:
        linear-gradient(
            rgba(15, 0, 0, 0.35),
            rgba(15, 0, 0, 0.60)
        ),
        url("data:image/png;base64,{imagem_base64}");
    """
except FileNotFoundError:
    fundo = """
    background: linear-gradient(150deg, #160707, #400909, #101010);
    """

# =========================
# DESIGN DO CHATIN
# =========================

st.markdown(f"""
<style>
.stApp {{
    {fundo}
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
}}

[data-testid="stSidebar"] {{
    background-color: rgba(30, 5, 5, 0.96);
    border-right: 3px solid #ffcc00;
}}

.title95 {{
    text-align: center;
    font-size: 100px;
    font-weight: 1000;
    color: #ff3030;
    text-shadow: 5px 5px 0px #ffcc00,
                 8px 8px 15px #000000;
    letter-spacing: 5px;
    margin-top: 10px;
}}

.subtitle95 {{
    text-align: center;
    color: #ffcc00;
    font-size: 24px;
    font-weight: bold;
}}

[data-testid="stChatMessage"] {{
    background-color: rgba(30, 10, 10, 0.90);
    border: 1px solid #ffcc00;
    border-radius: 15px;
}}

.stButton > button {{
    background-color: #ff3030;
    color: white;
    border: 2px solid #ffcc00;
    border-radius: 10px;
    font-weight: bold;
}}

.stButton > button:hover {{
    background-color: #ffcc00;
    color: black;
}}

[data-testid="stChatInput"] {{
    border: 2px solid #ffcc00;
    border-radius: 12px;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================

st.markdown(
    '<div class="title95">⚡ CHATIN ⚡</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle95">Seu parceiro de conversa!</div>',
    unsafe_allow_html=True
)

st.divider()

# =========================
# BARRA LATERAL
# =========================

with st.sidebar:
    st.markdown("# ⚡ CHATIN")
    st.caption("Sua central de conversas")

    if st.button("➕ Nova conversa", use_container_width=True):
        nova_conversa()
        st.rerun()

    st.divider()
    st.markdown("### 🎭 Personalidade")

    nomes = list(personalidades.keys())

    personalidade_escolhida = st.selectbox(
        "Como o CHATIN deve conversar?",
        nomes,
        index=nomes.index(st.session_state.personalidade),
        key="seletor_personalidade"
    )

    if personalidade_escolhida != st.session_state.personalidade:
        st.session_state.personalidade = personalidade_escolhida

        conversa = st.session_state.conversas[
            st.session_state.conversa_atual
        ]

        conversa["personalidade"] = personalidade_escolhida
        salvar_conversas()
        st.rerun()

    st.divider()
    st.markdown("### 💬 Conversas anteriores")

    ids = list(st.session_state.conversas.keys())
    ids.reverse()

    for identificador in ids:
        item = st.session_state.conversas[identificador]
        titulo = item.get("titulo", "Nova conversa")

        prefixo = (
            "🟡 " if identificador == st.session_state.conversa_atual
            else "💬 "
        )

        if st.button(
            prefixo + titulo,
            key="abrir_" + identificador,
            use_container_width=True
        ):
            st.session_state.conversa_atual = identificador
            st.session_state.personalidade = item.get(
                "personalidade", "Descolado 😎"
            )
            st.rerun()

    st.divider()

    if st.button("🗑️ Excluir conversa atual",
                 use_container_width=True):
        identificador = st.session_state.conversa_atual
        st.session_state.conversas.pop(identificador, None)

        if st.session_state.conversas:
            st.session_state.conversa_atual = next(
                reversed(st.session_state.conversas)
            )
        else:
            st.session_state.conversa_atual = None

        salvar_conversas()
        st.rerun()

    st.caption("🔴 Vermelho | 🟡 Amarelo | ⚡ CHATIN")

# =========================
# CHAT PRINCIPAL
# =========================

identificador = st.session_state.conversa_atual
conversa = st.session_state.conversas[identificador]

st.caption(f"Personalidade: {conversa['personalidade']}")

for mensagem in conversa["mensagens"]:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta = st.chat_input("Mande sua mensagem para o CHATIN...")

if pergunta:
    conversa["mensagens"].append({
        "role": "user",
        "content": pergunta
    })

    if conversa["titulo"] == "Nova conversa":
        conversa["titulo"] = pergunta[:35]
        if len(pergunta) > 35:
            conversa["titulo"] += "..."

    salvar_conversas()

    with st.chat_message("user"):
        st.markdown(pergunta)

    try:
        with st.chat_message("assistant"):
            with st.spinner("⚡ Pensando..."):
                mensagens_api = [
                    {
                        "role": "system",
                        "content": (
                            "Seu nome é CHATIN. "
                            "Responda em português brasileiro. "
                            "Siga esta personalidade: "
                            + personalidades[conversa["personalidade"]]
                        )
                    }
                ] + conversa["mensagens"]

                resposta = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=mensagens_api
                )

                texto = resposta.choices[0].message.content
                st.markdown(texto)

        conversa["mensagens"].append({
            "role": "assistant",
            "content": texto
        })

        salvar_conversas()

    except Exception as erro:
        st.error(f"Erro ao gerar resposta: {erro}")
        salvar_conversas()
