# TP1 – Sistema de Gestão de Usuários, Grupos e Eventos

Este é um projeto de console em Python que implementa um sistema de gestão de utilizadores, grupos e eventos, com autenticação, controle de permissões e interação via menu dinâmico.

O projeto utiliza **SQLAlchemy** para persistência em banco de dados SQLite e **JSON** para gestão de permissões e roles.

```text
tp1/
│
├─ app/
│  ├─ auth.py           # Autenticação e registo de utilizadores
│  ├─ menus.py          # Menus dinâmicos e handlers de ações
│  ├─ permissions.py    # Gestão de roles e permissões
│  └─ handlers/
│     ├─ chats.py         # Handler dos chats
│     ├─ check_user.py    # Handler para demonstrar informação sobre o utilizador
│     ├─ create_group.py  # Handler para criar grupos
│     ├─ edit_users.py    # Handler para editar utilizadores
│     ├─ events.py        # Handler para ações acerca de eventos
│     ├─ login.py         # Handler para tratar dos logins.
│     ├─ register.py      # Handler para registar um novo utilizador.
│     ├─ roles.py         # Handler para criar roles novas.
│     ├─ view_group.py    # Handler para ver grupos.
│     ├─ view_users.py    # Handler para ver utilizadores.
│     └─ _helper.py       # Helper para selecionar utilizadores.
│
├─ db/
│  ├─ db_controller.py  # Controller central para DB
│  ├─ init_db.py        # Inicialização e seed do DB
│  └─ schema.py         # Modelos SQLAlchemy
│
├─ vars/dev/
│  ├─ permissions.json  # Roles e permissões
│  └─ vars.json         # Configurações gerais e DB URL
│
├─ main_app.py          # Entry point principal
└─ README.md
```
    

## Funcionalidades

1. **Autenticação e Autorização**
   - Registro de usuários, incluindo criação automática do root se nenhum usuário existir.
   - Login seguro com hash SHA-256.
   - Controle de permissões baseado em roles definidas no `permissions.json`.

2. **Gestão de Usuários**
   - Visualização de todos os usuários.
   - Edição de dados do usuário (username, email, senha e role).
   - Diferenciação de usuários por roles: root e user.

3. **Gestão de Grupos**
   - Criação de grupos com um usuário dono/owner.
   - Adição e remoção de membros.
   - Visualização de grupos por proprietário ou como membro.
   - Exclusão de grupos.

4. **Gestão de Eventos**
   - Criação de eventos com data, descrição e lista de participantes.
   - Edição de evento, incluindo atualização de participantes.
   - Visualização de eventos pelos participantes.

5. **Menus Dinâmicos**
   - Menu principal adaptável conforme o login do usuário e permissões.
   - Opções de administração e operação restritas por role.

## Tecnologias utilizadas

- Python 3.11+
- SQLAlchemy (ORM para persistência de dados)
- SQLite (banco de dados leve para desenvolvimento)
- JSON (armazenamento de roles e permissões)
- hashlib (hashing de senhas com SHA-256)

## Instalações necessárias

```bash
pip install sqlalchemy
pip install sphinx_rtd_theme
```

## Autores 

Alexandre Saynov a89971
Sergiy Iurchenko a89831
