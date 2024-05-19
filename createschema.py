import psycopg2
import traceback
import io
import csv

db1 = psycopg2.connect(database="tcc2",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port="5432")

db2 = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port="5436")



try: 
    for i in range(1, 1001):
        batch_size = 10000

        with db2.cursor() as db2_cursor:
            print(f'Banco {i}')
            db2_cursor.execute(f"DROP SCHEMA IF EXISTS c_{i:04d} CASCADE")
            db2_cursor.execute(f"CREATE SCHEMA c_{i:04d}")
            db2_cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS c_{i:04d}.empresa (
                        id serial NOT NULL,
                        nome text NOT NULL,
                        cnpj character varying(14) NOT NULL,
                        data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id)
                    );

                    CREATE TABLE IF NOT EXISTS c_{i:04d}.usuario (
                        id serial NOT NULL,
                        nome text NOT NULL,
                        senha text NOT NULL,
                        data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY (empresa_id) REFERENCES c_{i:04d}.empresa(id)
                    );


                    CREATE TABLE IF NOT EXISTS c_{i:04d}.cliente (
                        id serial NOT NULL,
                        nome text NOT NULL,
                        email text,
                        telefone text,
                        cpf character varying(11),
                        data_cadastro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                        usuario_id integer NOT NULL,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY (empresa_id) REFERENCES c_{i:04d}.empresa(id),
                        FOREIGN KEY (usuario_id) REFERENCES c_{i:04d}.usuario(id)
                    );

                    CREATE TABLE IF NOT EXISTS c_{i:04d}.endereco (
                        id serial NOT NULL,
                        cliente_id integer NOT NULL,
                        rua text,
                        cidade text,
                        estado text,
                        cep text,
                        usuario_id integer NOT NULL,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY (cliente_id) REFERENCES c_{i:04d}.cliente(id),
                        FOREIGN KEY (usuario_id) REFERENCES c_{i:04d}.usuario(id)
                    );

                    CREATE TABLE IF NOT EXISTS c_{i:04d}.pedido (
                        id serial NOT NULL,
                        cliente_id integer NOT NULL,
                        valor_total numeric(10,2),
                        data_pedido timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                        usuario_id integer NOT NULL,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY (cliente_id) REFERENCES c_{i:04d}.cliente(id),
                        FOREIGN KEY (empresa_id) REFERENCES c_{i:04d}.empresa(id),
                        FOREIGN KEY (usuario_id) REFERENCES c_{i:04d}.usuario(id)
                    );

                    CREATE TABLE IF NOT EXISTS c_{i:04d}.produto (
                        id serial NOT NULL,
                        nome text NOT NULL,
                        descricao text,
                        preco_unitario numeric(10,2),
                        usuario_id integer NOT NULL,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (id),
                        FOREIGN KEY (empresa_id) REFERENCES c_{i:04d}.empresa(id),
                        FOREIGN KEY (usuario_id) REFERENCES c_{i:04d}.usuario(id)
                    );


                    CREATE TABLE IF NOT EXISTS c_{i:04d}.pedido_produto (
                        pedido_id integer NOT NULL,
                        produto_id integer NOT NULL,
                        quantidade integer,
                        usuario_id integer NOT NULL,
                        empresa_id integer NOT NULL,
                        PRIMARY KEY (pedido_id, produto_id),
                        FOREIGN KEY (empresa_id) REFERENCES c_{i:04d}.empresa(id),
                        FOREIGN KEY (pedido_id) REFERENCES c_{i:04d}.pedido(id),
                        FOREIGN KEY (produto_id) REFERENCES c_{i:04d}.produto(id),
                        FOREIGN KEY (usuario_id) REFERENCES c_{i:04d}.usuario(id)
                    );
                               """)
            
            db2_cursor.execute(f"CREATE INDEX pedido_produto_empresa_id ON c_{i:04d}.pedido_produto (empresa_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_produto_pedido_id ON c_{i:04d}.pedido_produto (pedido_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_produto_produto_id ON c_{i:04d}.pedido_produto (produto_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_produto_usuario_id ON c_{i:04d}.pedido_produto (usuario_id);")
            db2_cursor.execute(f"CREATE INDEX produto_usuario_id ON c_{i:04d}.produto (usuario_id);")
            db2_cursor.execute(f"CREATE INDEX produto_empresa_id ON c_{i:04d}.produto (empresa_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_cliente_id ON c_{i:04d}.pedido (cliente_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_empresa_id ON c_{i:04d}.pedido (empresa_id);")
            db2_cursor.execute(f"CREATE INDEX pedido_usuario_id ON c_{i:04d}.pedido (usuario_id);")
            db2_cursor.execute(f"CREATE INDEX endereco_cliente_id ON c_{i:04d}.endereco (cliente_id);")
            db2_cursor.execute(f"CREATE INDEX endereco_usuario_id ON c_{i:04d}.endereco (usuario_id);")
            db2_cursor.execute(f"CREATE INDEX cliente_empresa_id ON c_{i:04d}.cliente (empresa_id);")
            db2_cursor.execute(f"CREATE INDEX cliente_usuario_id ON c_{i:04d}.cliente (usuario_id);")
            db2_cursor.execute(f"CREATE INDEX usuario_empresa_id ON c_{i:04d}.usuario (empresa_id);")

            db2_cursor.execute(f"INSERT INTO c_{i:04d}.empresa (id, nome, cnpj, data_criacao) VALUES ({i}, 't', '1', CURRENT_TIMESTAMP)")
            db2.commit()

            for transfer_table_name in ['usuario', 'cliente', 'endereco', 'pedido', 'produto', 'pedido_produto']:
                with db1.cursor() as cursor:
                    cursor.itersize = batch_size
                    cursor.execute(f'SELECT * FROM {transfer_table_name} WHERE empresa_id = {i}')

                    while True:
                        rows = cursor.fetchmany(batch_size)
                        if not rows:
                            break
                        
                        csv_io = io.StringIO()
                        writer = csv.writer(csv_io)
                        writer.writerows(rows)
                        
                        csv_io.seek(0)

                        db2_cursor.copy_expert(
                            f'COPY c_{i:04d}.{transfer_table_name} FROM STDIN WITH (NULL \'\', DELIMITER \',\', FORMAT CSV)',
                            csv_io
                        )
                        db2.commit()

except (Exception, psycopg2.Error) as error:
    traceback.print_exc() 
    print("Failed to insert record into cliente table", error)

