ALTER TABLE endereco ADD empresa_id INTEGER;

do $$
declare _row_count INTEGER = 1;
begin
    WHILE _row_count > 0 LOOP
        UPDATE endereco
        SET empresa_id = cliente.empresa_id
        FROM cliente
        WHERE cliente.id = endereco.cliente_id
            AND endereco.id IN (SELECT id FROM endereco WHERE empresa_id IS NULL LIMIT 100000);

        GET DIAGNOSTICS _row_count = ROW_COUNT;
    END LOOP;
end $$;

DELETE FROM endereco WHERE cliente_id IS NULL;

ALTER TABLE endereco ALTER COLUMN empresa_id set not null;



-- remapear PRIMARY KEY da tabela usuario
ALTER TABLE cliente DROP CONSTRAINT cliente_usuario_id_fkey;
ALTER TABLE endereco DROP CONSTRAINT endereco_usuario_id_fkey;
ALTER TABLE pedido DROP CONSTRAINT pedido_usuario_id_fkey;
ALTER TABLE produto DROP CONSTRAINT produto_usuario_id_fkey;
ALTER TABLE pedido_produto DROP CONSTRAINT pedido_produto_usuario_id_fkey;

ALTER TABLE usuario DROP CONSTRAINT usuario_pkey;

ALTER TABLE usuario ADD PRIMARY KEY (empresa_id, id);

ALTER TABLE pedido_produto ADD CONSTRAINT fk_pedido_produto_usuario FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario;
ALTER TABLE produto ADD CONSTRAINT fk_produto_usuario FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario;
ALTER TABLE pedido ADD CONSTRAINT fk_pedido_usuario FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario;
ALTER TABLE endereco ADD CONSTRAINT fk_endereco_usuario FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario;
ALTER TABLE cliente ADD CONSTRAINT fk_cliente_usuario FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario;



-- remepar PRIMARY KEY da tabela cliente
ALTER TABLE endereco DROP CONSTRAINT endereco_cliente_id_fkey;
ALTER TABLE pedido DROP CONSTRAINT pedido_cliente_id_fkey;

ALTER TABLE cliente DROP CONSTRAINT cliente_pkey;

ALTER TABLE cliente ADD PRIMARY KEY (empresa_id, id);

ALTER TABLE pedido ADD CONSTRAINT fk_pedido_cliente FOREIGN KEY (empresa_id, cliente_id) REFERENCES cliente;
ALTER TABLE endereco ADD CONSTRAINT fk_endereco_cliente FOREIGN KEY (empresa_id, cliente_id) REFERENCES cliente;




-- remapear PRIMARY KEY da tabela endereco
ALTER TABLE endereco DROP CONSTRAINT endereco_pkey;

ALTER TABLE endereco ADD PRIMARY KEY (empresa_id, id);




-- remepar PRIMARY KEY da tabela pedido
ALTER TABLE pedido_produto DROP CONSTRAINT pedido_produto_pedido_id_fkey;

ALTER TABLE pedido DROP CONSTRAINT pedido_pkey;

ALTER TABLE pedido ADD PRIMARY KEY (empresa_id, id);

ALTER TABLE pedido_produto ADD CONSTRAINT fk_pedido_produto_pedido FOREIGN KEY (empresa_id, pedido_id) REFERENCES pedido;



-- remepar PRIMARY KEY da tabela produto
ALTER TABLE pedido_produto DROP CONSTRAINT pedido_produto_produto_id_fkey;

ALTER TABLE produto DROP CONSTRAINT produto_pkey;

ALTER TABLE produto ADD PRIMARY KEY (empresa_id, id);

ALTER TABLE pedido_produto ADD CONSTRAINT fk_pedido_produto_produto FOREIGN KEY (empresa_id, produto_id) REFERENCES produto;



-- remapear PRIMARY KEY da tabela pedido_produto
ALTER TABLE pedido_produto DROP CONSTRAINT pedido_produto_pkey;

ALTER TABLE pedido_produto ADD PRIMARY KEY (empresa_id, pedido_id, produto_id);





CREATE INDEX pedido_produto_pedido_id ON pedido_produto (pedido_id);
CREATE INDEX pedido_produto_produto_id ON pedido_produto (produto_id);
CREATE INDEX pedido_produto_usuario_id ON pedido_produto (usuario_id);
CREATE INDEX produto_usuario_id ON produto (usuario_id);
CREATE INDEX pedido_cliente_id ON pedido (cliente_id);
CREATE INDEX pedido_usuario_id ON pedido (usuario_id);
CREATE INDEX endereco_cliente_id ON endereco (cliente_id);
CREATE INDEX endereco_usuario_id ON endereco (usuario_id);
CREATE INDEX cliente_usuario_id ON cliente (usuario_id);
