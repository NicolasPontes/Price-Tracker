from app.database.connection import engine


def testar_conexao():
    try:
        with engine.connect() as connection:
            print("✅ Conexão com SQL Server realizada com sucesso!")

    except Exception as error:
        print("❌ Erro ao conectar com o SQL Server:")
        print(error)


if __name__ == "__main__":
    testar_conexao()