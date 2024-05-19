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
    PRIMARY KEY (empresa_id, id), -- primary key composta
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
    PRIMARY KEY (empresa_id, id), -- primary key composta
    FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario(empresa_id, id) -- modificada
);

CREATE TABLE endereco (
    id serial NOT NULL,
    empresa_id integer NOT NULL, -- adicionada
    cliente_id integer NOT NULL,
    rua text,
    cidade text,
    estado text,
    cep text,
    usuario_id integer NOT NULL,
    PRIMARY KEY (empresa_id, id), -- primary key composta
    FOREIGN KEY (empresa_id, cliente_id) REFERENCES cliente(empresa_id, id), -- modificada
    FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario(empresa_id, id) -- modificada
);

CREATE TABLE pedido (
    id serial NOT NULL,
    cliente_id integer NOT NULL,
    valor_total numeric(10,2),
    data_pedido timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (empresa_id, id), -- primary key composta
    FOREIGN KEY (empresa_id, cliente_id) REFERENCES cliente(empresa_id, id), -- modificada
    FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario(empresa_id, id) -- modificada
);

CREATE TABLE produto (
    id serial NOT NULL,
    nome text NOT NULL,
    descricao text,
    preco_unitario numeric(10,2),
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (empresa_id, id), -- primary key composta
    FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario(empresa_id, id) -- modificada
);


CREATE TABLE pedido_produto (
    pedido_id integer NOT NULL,
    produto_id integer NOT NULL,
    quantidade integer,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    PRIMARY KEY (empresa_id, pedido_id, produto_id), -- primary key composta
    FOREIGN KEY (empresa_id, pedido_id) REFERENCES pedido(empresa_id, id), -- modificada
    FOREIGN KEY (empresa_id, produto_id) REFERENCES produto(empresa_id, id), -- modificada
    FOREIGN KEY (empresa_id, usuario_id) REFERENCES usuario(empresa_id, id) -- modificada
);
