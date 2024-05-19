from typing import Optional
import asyncio, datetime
import asyncpg
from enum import Enum
import random
import csv

class Tipo(Enum):
    ORIGINAL = 'original',
    CITUS_ROW = 'citus_row',
    CITUS_SCHEMA = 'citus_schema'

class DbPoolSingleton:
    db_pool: Optional[asyncpg.pool.Pool] = None

    @staticmethod
    async def create_pool(tipo: Tipo):
        match tipo:
            case Tipo.ORIGINAL:
                pool = await asyncpg.create_pool(
                    user='postgres',
                    password='postgres',
                    database='postgres',
                    host='localhost',
                    port=5433,
                    min_size=5,
                    max_size=100
                )

            case Tipo.CITUS_ROW:
                pool = await asyncpg.create_pool(
                    user='postgres',
                    password='postgres',
                    database='postgres',
                    host='localhost',
                    port=5435,
                    min_size=5,
                    max_size=100
                )

            case Tipo.CITUS_SCHEMA:
                pool = await asyncpg.create_pool(
                    user='postgres',
                    password='postgres',
                    database='postgres',
                    host='localhost',
                    port=5436,
                    min_size=5,
                    max_size=100
                )
        return pool

    @staticmethod
    async def get_pool(tipo: Tipo) -> asyncpg.pool.Pool:
        if not DbPoolSingleton.db_pool:
            DbPoolSingleton.db_pool = await DbPoolSingleton.create_pool(tipo)
        return DbPoolSingleton.db_pool

    @staticmethod
    async def terminate_pool(tipo: Tipo):
        (await DbPoolSingleton.get_pool(tipo)).terminate()
        DbPoolSingleton.db_pool = None

async def run_query(pool, sql, ids) -> tuple:
    tuples = []

    for empresa_id in ids:
        async with pool.acquire() as conn:
            times = []
            for _ in range(10):
                qstart = datetime.datetime.now()
                result = await conn.fetch(sql.replace("{empresa_id}", f"c_{empresa_id:04d}"), empresa_id)
                qend = datetime.datetime.now()
                times.append((qend - qstart).total_seconds())
            tuples.append(sum(times) / len(times))

    return tuples

def flatten(xss):
    return [x for xs in xss for x in xs]

async def test_asynchronous(tipo: Tipo, query: str, queryId: int, clientes: int) -> None:
    print(f"Tipo: {tipo} queryId: {queryId} clientes: {clientes}")
    pool = await DbPoolSingleton.get_pool(tipo)
    total_start = datetime.datetime.now()

    if queryId != 5:
        ids = list(range(1, 1001))
        random.shuffle(ids)
        step = int(1000 / clientes)
    else:
        ids = list(range(1, 101))
        step = int(100 / clientes)
    tasks = []

    for i in range(0, len(ids), step):
        x = i
        ids_chunk = ids[x:x+step]
        tasks.append(run_query(pool, query, ids_chunk))

    results = await asyncio.gather(*tasks)
    runtime_total = sum(flatten(results))
    total_end = datetime.datetime.now()

    await DbPoolSingleton.terminate_pool(tipo)

    with open(f'resultados/all_results_v4.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for r in flatten(results):
            writer.writerow([tipo.name, queryId, clientes, r])

    print(f"async total query took:  {(total_end-total_start).total_seconds()} wallclock seconds and {runtime_total} run seconds")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    tipos = {
        Tipo.ORIGINAL: [
                # Top 10 vendedores
                """
                SELECT usuario.nome, SUM(pedido.valor_total) AS valor_total
                FROM pedido
                INNER JOIN usuario ON pedido.empresa_id = usuario.empresa_id and pedido.usuario_id = usuario.id
                WHERE pedido.empresa_id = $1
                GROUP BY usuario.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 produtos mais vendidos
                """
                SELECT produto.nome, SUM(produto.preco_unitario * pedido_produto.quantidade) AS valor_total
                FROM produto
                INNER JOIN pedido_produto ON produto.id = pedido_produto.produto_id
                WHERE produto.empresa_id = $1
                GROUP BY produto.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 clientes
                """
                SELECT cliente.nome, COUNT(*) AS total_pedidos
                FROM cliente
                INNER JOIN pedido ON cliente.id = pedido.cliente_id
                WHERE cliente.empresa_id = $1
                GROUP BY cliente.nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """,
                # Top 10 cidades com mais vendas
                """
                SELECT endereco.cidade, SUM(pedido.valor_total) AS valor_total
                FROM pedido
                INNER JOIN cliente ON cliente.id = pedido.cliente_id
                INNER JOIN endereco ON endereco.cliente_id = cliente.id
                WHERE pedido.empresa_id = $1
                GROUP BY endereco.cidade
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 empresas com mais clientes
                """
                SELECT empresa.nome, COUNT(*) AS quantidade_clientes
                FROM empresa
                INNER JOIN cliente ON empresa.id = cliente.empresa_id
                WHERE $1 < 10000
                GROUP BY empresa.nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """
            ],
        Tipo.CITUS_ROW: [
                # Top 10 vendedores
                """
                SELECT usuario.nome, SUM(pedido.valor_total) AS valor_total
                FROM pedido
                INNER JOIN usuario ON pedido.empresa_id = usuario.empresa_id and pedido.usuario_id = usuario.id
                WHERE pedido.empresa_id = $1
                GROUP BY usuario.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 produtos mais vendidos
                """
                SELECT produto.nome, SUM(produto.preco_unitario * pedido_produto.quantidade) AS valor_total
                FROM produto
                INNER JOIN pedido_produto ON produto.empresa_id = pedido_produto.empresa_id and produto.id = pedido_produto.produto_id
                WHERE produto.empresa_id = $1
                GROUP BY produto.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 clientes
                """
                SELECT cliente.nome, COUNT(*) AS total_pedidos
                FROM cliente
                INNER JOIN pedido ON cliente.empresa_id = pedido.empresa_id and cliente.id = pedido.cliente_id
                WHERE cliente.empresa_id = $1
                GROUP BY cliente.nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """,
                # Top 10 cidades com mais vendas
                """
                SELECT endereco.cidade, SUM(pedido.valor_total) AS valor_total
                FROM pedido
                INNER JOIN cliente ON cliente.empresa_id = pedido.empresa_id and cliente.id = pedido.cliente_id
                INNER JOIN endereco ON endereco.empresa_id = cliente.empresa_id and endereco.cliente_id = cliente.id
                WHERE pedido.empresa_id = $1
                GROUP BY endereco.cidade
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 empresas com mais clientes
                """
                SELECT empresa.nome, COUNT(*) AS quantidade_clientes
                FROM empresa
                INNER JOIN cliente ON empresa.id = cliente.empresa_id
                WHERE $1 < 10000
                GROUP BY empresa.nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """
            ],
        Tipo.CITUS_SCHEMA: [
                # Top 10 vendedores
                """
                SELECT usuario.nome, SUM(pedido.valor_total) AS valor_total
                FROM {empresa_id}.pedido
                INNER JOIN {empresa_id}.usuario ON pedido.usuario_id = usuario.id
                WHERE $1 > 0
                GROUP BY usuario.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 produtos mais vendidos
                """
                SELECT produto.nome, SUM(produto.preco_unitario * pedido_produto.quantidade) AS valor_total
                FROM {empresa_id}.produto
                INNER JOIN {empresa_id}.pedido_produto ON produto.id = pedido_produto.produto_id
                WHERE $1 > 0
                GROUP BY produto.nome
                ORDER BY 2 DESC
                LIMIT 10
                """,
                # Top 10 clientes
                """
                SELECT cliente.nome, COUNT(*) AS total_pedidos
                FROM {empresa_id}.cliente
                INNER JOIN {empresa_id}.pedido ON cliente.id = pedido.cliente_id
                WHERE $1 > 0
                GROUP BY cliente.nome
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """,
                # Top 10 cidades com mais vendas
                """
                SELECT endereco.cidade, SUM(pedido.valor_total) AS valor_total
                FROM {empresa_id}.pedido
                INNER JOIN {empresa_id}.cliente ON cliente.id = pedido.cliente_id
                INNER JOIN {empresa_id}.endereco ON endereco.cliente_id = cliente.id
                WHERE $1 > 0
                GROUP BY endereco.cidade
                ORDER BY 2 DESC
                LIMIT 10
                """
            ]
    }

    for tipo, queries in tipos.items():
        if tipo == Tipo.ORIGINAL:
            for i, query in enumerate(queries):
                if i == 3:
                    for clientes in [5, 10, 25, 50, 100]:
                        loop.run_until_complete(test_asynchronous(tipo, query, i + 1, clientes))
