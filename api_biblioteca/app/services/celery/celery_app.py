from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy import select

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
        'schedule': timedelta(days=1),
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