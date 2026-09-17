"""
Migração pontual para o sistema de login:
1. Cria a tabela `usuarios` (nova, via create_all).
2. Limpa produtos/histórico de teste que existem sem dono
   (não dá pra ter usuario_id NOT NULL em linhas antigas sem usuário).
3. Adiciona a coluna `usuario_id` na tabela `produtos`, se ainda não existir.

Rode com: python -m tests.migrar_usuarios
"""

from sqlalchemy import text

from app.database.connection import engine
from app.database.init_db import criar_tabelas


def migrar():
    # 1) Cria a tabela `usuarios` (e qualquer outra tabela nova que falte)
    criar_tabelas()

    with engine.begin() as conn:
        coluna_existe = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = 'produtos' AND COLUMN_NAME = 'usuario_id'"
        )).fetchone()

        if coluna_existe:
            print("Coluna 'usuario_id' já existe em 'produtos'. Nada a fazer.")
            return

        print("Limpando produtos de teste (sem dono) antes de adicionar a coluna...")
        conn.execute(text("DELETE FROM historico_precos"))
        conn.execute(text("DELETE FROM produtos"))

        print("Adicionando coluna 'usuario_id'...")
        conn.execute(text(
            "ALTER TABLE produtos ADD usuario_id INT NOT NULL "
            "CONSTRAINT FK_produtos_usuario_id REFERENCES usuarios(id)"
        ))

    print("✅ Migração concluída! A partir de agora, cadastre produtos pela interface (com login).")


if __name__ == "__main__":
    migrar()