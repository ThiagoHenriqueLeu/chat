import eventlet
eventlet.monkey_patch()  # 🔥 TEM QUE VIR PRIMEIRO

from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# HTML como string
html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat em Tempo Real</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }

    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #1e1e2f;
      color: #f0f0f0;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      min-height: 100vh;
      padding: 1rem;
    }

    #login, #chat {
      background-color: #2a2a3d;
      padding: 2rem;
      border-radius: 0.625rem;
      box-shadow: 0 0.25rem 1.25rem rgba(0, 0, 0, 0.4);
      width: 100%;
      max-width: 37.5rem; /* Aumentado de 25rem para 37.5rem (600px) */
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    h2 {
      text-align: center;
      color: #61dafb;
      font-size: clamp(1.4rem, 5vw, 1.8rem); /* Ajustado para maior largura */
      margin-bottom: 0.5rem;
    }

    input {
      width: 100%;
      padding: 0.75rem;
      border: none;
      border-radius: 0.3125rem;
      font-size: clamp(0.9rem, 4vw, 1rem);
      background-color: #3c3c50;
      color: #fff;
    }

    input::placeholder {
      color: #aaa;
    }

    button {
      width: 100%;
      padding: 0.875rem;
      background-color: #61dafb;
      color: #000;
      border: none;
      border-radius: 0.3125rem;
      font-weight: bold;
      cursor: pointer;
      transition: background-color 0.3s ease;
      font-size: clamp(0.9rem, 4vw, 1rem);
    }

    button:hover {
      background-color: #4dbde9;
    }

    #mensagens {
      max-height: 70vh; /* Aumentado de 60vh para 70vh */
      overflow-y: auto;
      background-color: #1a1a2b;
      padding: 0.625rem;
      border-radius: 0.3125rem;
      border: 1px solid #333;
      margin-bottom: 1rem;
      scroll-behavior: smooth;
    }

    .mensagem {
      margin-bottom: 0.5rem;
      padding: 0.625rem;
      border-radius: 0.3125rem;
      word-wrap: break-word;
      background-color: rgba(255, 99, 71, 0.85);
      color: #fff;
      font-size: clamp(0.85rem, 3.5vw, 0.9375rem);
    }

    /* Responsividade */
    @media (max-width: 768px) {
      #login, #chat {
        padding: 1.5rem;
        max-width: 90%;
      }

      #mensagens {
        max-height: 60vh; /* Ajustado para telas menores */
      }
    }

    @media (max-width: 480px) {
      #login, #chat {
        padding: 1rem;
        max-width: 95%;
      }

      h2 {
        font-size: clamp(1.2rem, 4.5vw, 1.4rem);
      }

      input, button {
        padding: 0.625rem;
        font-size: clamp(0.85rem, 4vw, 0.9375rem);
      }

      #mensagens {
        max-height: 55vh; /* Ajustado para telas menores */
      }
    }

    @media (max-width: 360px) {
      #login, #chat {
        padding: 0.75rem;
        max-width: 100%;
      }

      h2 {
        font-size: clamp(1.1rem, 4vw, 1.2rem);
      }

      input, button {
        padding: 0.5rem;
        font-size: clamp(0.8rem, 3.8vw, 0.875rem);
      }

      #mensagens {
        max-height: 50vh; /* Ajustado para telas muito pequenas */
      }
    }
  </style>
</head>
<body>
  <div id="login">
    <h2>Digite seu nome para entrar no chat:</h2>
    <input id="nomeInput" placeholder="Seu nome" />
    <button onclick="entrarNoChat()">Entrar</button>
  </div>

  <div id="chat" style="display: none;">
    <h2>Chat</h2>
    <div id="mensagens"></div>
    <input id="mensagemInput" placeholder="Digite uma mensagem..." />
    <button onclick="enviarMensagem()">Enviar</button>
  </div>

  <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
  <script>
    let socket;
    let nome = localStorage.getItem("nome");
    const cores = {};
    const coresPossiveis = ['#ff6347', '#4682b4', '#32cd32', '#ffa500', '#9370db', '#ff69b4'];

    if (!nome) {
      document.getElementById("login").style.display = "block";
    } else {
      iniciarChat();
    }

    function entrarNoChat() {
      nome = document.getElementById("nomeInput").value.trim();
      if (!nome) return alert("Digite um nome");
      localStorage.setItem("nome", nome);
      iniciarChat();
    }

    function iniciarChat() {
      document.getElementById("login").style.display = "none";
      document.getElementById("chat").style.display = "flex";
      document.getElementById("mensagens").scrollTop = document.getElementById("mensagens").scrollHeight;

      socket = io();

      socket.emit("usuario_entrou", nome);

      socket.on("mensagem", function(dado) {
        if (!cores[dado.ip]) {
          cores[dado.ip] = coresPossiveis[Math.floor(Math.random() * coresPossiveis.length)];
        }

        const msg = document.createElement("div");
        msg.className = "mensagem";
        msg.style.backgroundColor = cores[dado.ip];
        msg.textContent = `${dado.nome} (${dado.ip}): ${dado.texto}`;
        document.getElementById("mensagens").appendChild(msg);
        document.getElementById("mensagens").scrollTop = document.getElementById("mensagens").scrollHeight;
      });
    }

    function enviarMensagem() {
      const input = document.getElementById("mensagemInput");
      const texto = input.value;
      if (texto) {
        socket.emit("mensagem", { nome, texto });
        input.value = "";
      }
    }
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return html_content  # Retorna o conteúdo HTML diretamente

@socketio.on('mensagem')
def handle_message(dado):
    ip = request.remote_addr
    print(f'Mensagem de {ip}: {dado}')
    emit('mensagem', {
        'nome': dado['nome'],
        'texto': dado['texto'],
        'ip': ip
    }, broadcast=True)

@socketio.on('usuario_entrou')
def usuario_entrou(nome):
    print(f'Usuário entrou: {nome}')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80)
