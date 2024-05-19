CREATE TABLE empresa (
    id serial NOT NULL,
    nome text NOT NULL,
    cnpj character varying(14) NOT NULL,
    data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE usuario (
    id serial NOT NULL,
    nome text NOT NULL,
    senha text NOT NULL,
    data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    empresa_id integer NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id)
);

CREATE TABLE cliente (
    id serial NOT NULL,
    nome text NOT NULL,
    email text,
    telefone text,
    cpf character varying(11),
    data_cadastro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE endereco (
    id serial NOT NULL,
    cliente_id integer NOT NULL,
    rua text,
    cidade text,
    estado text,
    cep text,
    usuario_id integer NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE pedido (
    id serial NOT NULL,
    cliente_id integer NOT NULL,
    valor_total numeric(10,2),
    data_pedido timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE produto (
    id serial NOT NULL,
    nome text NOT NULL,
    descricao text,
    preco_unitario numeric(10,2),
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);


CREATE TABLE pedido_produto (
    pedido_id integer NOT NULL,
    produto_id integer NOT NULL,
    quantidade integer,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    FOREIGN KEY (pedido_id) REFERENCES pedido(id),
    FOREIGN KEY (produto_id) REFERENCES produto(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE INDEX pedido_produto_empresa_id ON pedido_produto (empresa_id);
CREATE INDEX pedido_produto_pedido_id ON pedido_produto (pedido_id);
CREATE INDEX pedido_produto_produto_id ON pedido_produto (produto_id);
CREATE INDEX pedido_produto_usuario_id ON pedido_produto (usuario_id);
CREATE INDEX produto_usuario_id ON produto (usuario_id);
CREATE INDEX produto_empresa_id ON produto (empresa_id);
CREATE INDEX pedido_cliente_id ON pedido (cliente_id);
CREATE INDEX pedido_empresa_id ON pedido (empresa_id);
CREATE INDEX pedido_usuario_id ON pedido (usuario_id);
CREATE INDEX endereco_cliente_id ON endereco (cliente_id);
CREATE INDEX endereco_usuario_id ON endereco (usuario_id);
CREATE INDEX cliente_empresa_id ON cliente (empresa_id);
CREATE INDEX cliente_usuario_id ON cliente (usuario_id);
CREATE INDEX usuario_empresa_id ON usuario (empresa_id);