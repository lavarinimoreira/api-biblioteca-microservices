from notifications import enviar_notificacao

if __name__ == "__main__":
    # Substitua pelos dados que você deseja testar
    destinatario = "lavarinimoreira@gmail.com"
    usuario_nome = "Gabriel"
    nome_do_livro = "Livro de Teste"
    enviar_notificacao(destinatario, usuario_nome, nome_do_livro)
