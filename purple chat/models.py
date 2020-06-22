class Canal:
	def __init__(self, visibilidade, senha, nome):
		self.visibilidade = visibilidade
		self.senha = senha
		self.mensagens = []
		self.nome = nome

	def addMensagem(self, mensagem):
		self.mensagens.append(mensagem)
		if len(self.mensagens) == 100:
			self.mensagens.pop(0)

class Mensagem:
	def __init__(self, nome, cor, texto, dataHora):
		self.nome = nome
		self.cor = cor
		self.texto = texto
		self.dataHora = dataHora