from faker import Faker
import psycopg2
import re
import random
import traceback
from faker_vehicle import VehicleProvider

conn = psycopg2.connect(database="tcc2",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port="5432")

fake = Faker('pt_BR')
fake.add_provider(VehicleProvider)

def criar_empresa(cursor):
    postgres_insert_query = """INSERT INTO empresa (nome, cnpj) VALUES (%s,%s) RETURNING id"""
    record_to_insert = (fake.unique.company(), re.sub('\\D', '', fake.unique.cnpj()))
    cursor.execute(postgres_insert_query, record_to_insert)

    return cursor.fetchone()[0]

def criar_usuario(cursor, empresa_id):
    postgres_insert_query = """INSERT INTO usuario (nome, senha, empresa_id) VALUES (%s,%s,%s) RETURNING id"""
    record_to_insert = (fake.unique.name(), fake.password(), empresa_id)
    cursor.execute(postgres_insert_query, record_to_insert)

    return cursor.fetchone()[0]

def criar_cliente(cursor, usuario_id, empresa_id):
    postgres_insert_query = """INSERT INTO cliente (nome, cpf, email, telefone, usuario_id, empresa_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id"""
    record_to_insert = (fake.unique.name(), re.sub('\\D', '', fake.unique.cpf()), fake.unique.email(), fake.unique.phone_number(), usuario_id, empresa_id)
    cursor.execute(postgres_insert_query, record_to_insert)

    cliente_id = cursor.fetchone()[0]

    for x in range(0, random.randint(0, 2)):
        criar_endereco(cursor, cliente_id, usuario_id)
    
    return cliente_id


def criar_endereco(cursor, cliente_id, usuario_id):
    postgres_insert_query = """INSERT INTO endereco (cliente_id, rua, cidade, estado, cep, usuario_id) VALUES (%s,%s,%s,%s,%s, %s)"""
    record_to_insert = (cliente_id, fake.unique.street_address(), fake.city(), fake.state(), fake.postcode(), usuario_id)
    cursor.execute(postgres_insert_query, record_to_insert)

def criar_produto(cursor, usuario_id, empresa_id):
    postgres_insert_query = """INSERT INTO produto (nome, descricao, preco_unitario, usuario_id, empresa_id) VALUES (%s,%s,%s,%s,%s) RETURNING id"""
    car = fake.vehicle_object()
    valor_unitario = random.randint(5000, 300000)
    record_to_insert = (car.get('Model'), car.get('Make') + ' - ' + car.get('Category') + ' (' + str(car.get('Year')) + ')', valor_unitario, usuario_id, empresa_id)
    cursor.execute(postgres_insert_query, record_to_insert)

    return cursor.fetchone()[0], valor_unitario

def criar_pedido(cursor, empresa_id, usuario_id, cliente_id, produto_id, valor_unitario):
    quantidade_produtos = random.randint(1, 3)
    postgres_insert_query = """INSERT INTO pedido (cliente_id, valor_total, data_pedido, usuario_id, empresa_id) VALUES (%s,%s,%s,%s,%s) RETURNING id"""
    record_to_insert = (cliente_id, quantidade_produtos * valor_unitario, fake.date_time_this_decade(), usuario_id, empresa_id)
    cursor.execute(postgres_insert_query, record_to_insert)

    pedido_id = cursor.fetchone()[0]

    postgres_insert_query = """INSERT INTO pedido_produto (pedido_id, produto_id, quantidade, usuario_id, empresa_id) VALUES (%s,%s,%s,%s,%s)"""
    record_to_insert = (pedido_id, produto_id, quantidade_produtos, usuario_id, empresa_id)
    cursor.execute(postgres_insert_query, record_to_insert)

try:
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="localhost",
                                  port="5432",
                                  database="tcc2")
    cursor = connection.cursor()
 
    for i in range(1000):
        empresa_id = criar_empresa(cursor)
        usuarios = []
        produtos = []
        clientes = []
        quantidade_usuarios = random.randint(10, 300)
        quantidade_produtos = random.randint(10, 200)
        quantidade_clientes = (int) (quantidade_usuarios / 10 * random.randint(300, 1000))

        for x in range(quantidade_usuarios):
            usuarios.append(criar_usuario(cursor, empresa_id))

        for x in range(quantidade_produtos):
            produtos.append(criar_produto(cursor, random.choice(usuarios), empresa_id))

        for x in range(quantidade_clientes):
            clientes.append(criar_cliente(cursor, random.choice(usuarios), empresa_id))

        for cliente_id in random.choices(clientes, k=random.randint(1, (int) (quantidade_clientes * 0.5))):
            for (produto_id, valor_unitario) in random.choices(produtos, k=random.randint(1, (int) (quantidade_produtos * 0.5))):
                criar_pedido(cursor, empresa_id, random.choice(usuarios), cliente_id, produto_id, valor_unitario)

        fake.unique.clear()
        connection.commit()

except (Exception, psycopg2.Error) as error:
    traceback.print_exc() 
    print("Failed to insert record into cliente table", error)

