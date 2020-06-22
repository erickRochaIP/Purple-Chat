import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
from flask_session import Session
from models import Canal, Mensagem
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

canais = []

#functions

def logado():
	if 'nomeusuario' in session:
		return True
	else:
		return False

def ultimoConectado():
	if 'ultimocanal' in session:
		return True
	else:
		return False

@app.route("/", methods=["GET", "POST"])
def index():
	if logado():
		nomeusuario = session['nomeusuario']
		cor = session['cor']
	else:
		nomeusuario = "Visitante"
		cor = 'black'
	return render_template("index.html", nomeusuario=nomeusuario, cor=cor, canais=canais, logado=logado())

@app.route("/indexar", methods=["GET", "POST"])
def indexar():
	session.pop('ultimocanal', None)
	return redirect(url_for('index'))

@app.route("/logar", methods=["POST"])
def logar():
	nomeusuario = request.form.get("nomeusuario")
	cor = request.form.get("cor")
	session['nomeusuario'] = nomeusuario
	session['cor'] = cor
	return redirect(url_for('index'))

@app.route("/logout", methods=["POST"])
def logout():
	session.pop('nomeusuario', None)
	session.pop('cor', None)
	return redirect(url_for('index'))

@app.route("/login", methods=["POST"])
def login():
	return render_template("logar.html")

@app.route("/criarCanal", methods=["POST"])
def criarCanal():
	return render_template("criarCanal.html")

@app.route("/postarCanal", methods=["POST"])
def postarCanal():
	nomecanal = request.form.get("nomecanal")
	senha = request.form.get("senha")
	for canal in canais:
		if canal.nome == nomecanal:
			return redirect(url_for('index'))
	visibilidade = True
	if senha is not "":
		visibilidade = False
	canais.append(Canal(visibilidade, senha, nomecanal))
	return redirect(url_for('index'))

@app.route("/abrirCanal/<string:nome>", methods=["GET", "POST"])
def abrirCanal(nome):
	if not logado():
		return render_template("logar.html")
	else:
		nomeusuario = session['nomeusuario'] 
		cor = session['cor']
		for canal in canais:
			if canal.nome == nome:
				if canal.visibilidade == True:
					return render_template("canal.html", canal=canal, logado = logado(), nomeusuario=nomeusuario, cor=cor)
				else:
					return render_template("pedirSenha.html", canal=canal)

@app.route("/conferirSenha", methods=["POST"])
def conferirSenha():
	nome = request.form.get("nome")
	senha = request.form.get("senha")
	nomeusuario = session['nomeusuario'] 
	cor = session['cor']

	for canal in canais:
		if canal.nome == nome:
			if canal.senha != senha:
				return redirect(url_for('index'))
			return render_template("canal.html", canal=canal, logado = logado(), nomeusuario=nomeusuario, cor=cor)

@socketio.on("enviar mensagem")
def mensagem(data):
	selection = data["selection"]
	nomeusuario = data["nomeusuario"]
	cor = data["cor"]
	canall = data["canal"]
	data_e_hora = datetime.now()
	dataHora = data_e_hora.strftime('%H:%M')
	mensagem = Mensagem(nomeusuario, cor, selection, dataHora)
	for canal in canais:
		if canal.nome == canall:
			canal.addMensagem(mensagem)

	emit("announce mensagem", {"selection": selection, "nomeusuario":nomeusuario, "cor":cor,"canal":canall, "dataHora":dataHora}, broadcast=True)
