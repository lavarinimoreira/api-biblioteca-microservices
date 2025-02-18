"""
Arquivo responsável pela lógica de envio de notificação.
"""
def enviar_notificacao(email: str, usuario_nome: str, nome_do_livro: str):
    print(f"Enviando email para {email}... {usuario_nome}, o livro {nome_do_livro} está Atrasado.")


