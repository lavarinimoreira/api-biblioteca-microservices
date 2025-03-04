from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy import select
import os

from app.models.user import Usuario
from app.models.book import Livro
from app.models.loan import Emprestimo
from app.services.celery.notifications import enviar_notificacao
from app.services.celery.celery_config import SessionLocalCelery  # Sessão síncrona para o Celery
from app.models.__all_models import Base 

# Configurando o Celery
celery_app = Celery(
    'tasks',
    broker='redis://broker:6379/0',
    backend='redis://broker:6379/0'
)

celery_app.conf.beat_schedule = {
    'verificar-emprestimos-diario': {
        'task': 'app.services.celery.celery_app.verificar_emprestimos_vencidos',
        # 'schedule': timedelta(days=1),
        'schedule': timedelta(hours=12)
        # 'schedule': timedelta(seconds=30)
    },
    'limpar-imagens-orfas': {
        'task': 'app.services.celery.celery_app.limpar_imagens_orfas',
        # 'schedule': timedelta(days=1),
        'schedule': timedelta(hours=12)
        # 'schedule': timedelta(seconds=30)
    },
}

@celery_app.task
def verificar_emprestimos_vencidos():
    with SessionLocalCelery() as session:
        try:
            # Obtém a data atual
            agora = datetime.utcnow()
            # Calcula a data limite (7 dias atrás)
            data_limite = agora - timedelta(days=7)

            # Consulta os empréstimos ativos com data de devolução ultrapassada
            result = session.execute(
                select(Emprestimo)
                .filter(
                    Emprestimo.status == "Ativo",  # Filtra empréstimos ativos
                    Emprestimo.data_devolucao < data_limite,  # Filtra empréstimos com mais de 7 dias
                )
            )
            emprestimos = result.scalars().all()

            # Atualiza o status e notifica os usuários
            for emprestimo in emprestimos:
                emprestimo.status = "Atrasado"
                session.add(emprestimo)

                # Notifica o usuário
                enviar_notificacao(
                    email=emprestimo.usuario.email,  
                    usuario_nome=emprestimo.usuario.nome,  
                    nome_do_livro=emprestimo.livro.titulo  
                )

            session.commit()
            return f"Atualizados {len(emprestimos)} empréstimos vencidos e notificações enviadas."
        except Exception as e:
            session.rollback()
            print(f"Erro ao processar empréstimos: {e}")
            raise e
        

@celery_app.task
def limpar_imagens_orfas():
    UPLOAD_DIR = "upload"
    profile_dir = os.path.join(UPLOAD_DIR, "profile")
    book_cover_dir = os.path.join(UPLOAD_DIR, "book_cover")

    # Obtém a lista de arquivos nos diretórios, se existirem
    arquivos_profile = os.listdir(profile_dir) if os.path.exists(profile_dir) else []
    arquivos_book_cover = os.listdir(book_cover_dir) if os.path.exists(book_cover_dir) else []

    # Consulta o banco de dados para obter os nomes dos arquivos referenciados
    with SessionLocalCelery() as session:
        # Para os usuários
        usuarios = session.execute(select(Usuario.profile_picture_url)).scalars().all()
        # Para os livros
        livros = session.execute(select(Livro.image_url)).scalars().all()

    # Extrai apenas o nome do arquivo (basename) das URLs registradas
    referenciados_profile = {os.path.basename(url) for url in usuarios if url}
    referenciados_book = {os.path.basename(url) for url in livros if url}

    arquivos_removidos = []

    # Verifica e remove arquivos órfãos no diretório de perfil
    for arquivo in arquivos_profile:
        if arquivo not in referenciados_profile:
            caminho_arquivo = os.path.join(profile_dir, arquivo)
            try:
                os.remove(caminho_arquivo)
                arquivos_removidos.append(caminho_arquivo)
            except Exception as e:
                print(f"Erro ao remover {caminho_arquivo}: {e}")

    # Verifica e remove arquivos órfãos no diretório de capas de livros
    for arquivo in arquivos_book_cover:
        if arquivo not in referenciados_book:
            caminho_arquivo = os.path.join(book_cover_dir, arquivo)
            try:
                os.remove(caminho_arquivo)
                arquivos_removidos.append(caminho_arquivo)
            except Exception as e:
                print(f"Erro ao remover {caminho_arquivo}: {e}")

    return f"Arquivos órfãos removidos: {arquivos_removidos}"