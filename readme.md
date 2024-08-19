**Serviço de Notificações Push - App Vendas Plus**

Esse serviço é responsável por:

- receber os textos das notificações;
- receber os tokoens do FCM e o id_representante de cada dispositivo logado no app;
- fazer o envio das notificações através do FCM

---------------------------

Tecnologias utilizadas


|Nome  |Versão |
|---------|---------|
|Python     |3ˆ         |
|Flask     |3.0.3         |
|Flask-Cors     |4.0.1         |
|firebase-admin     |6.5.0         |
|schedule     |1.2.2         |
|sqlite     |3         |

---------------------------

O projeto é constituído por três arquivos principais:

1) main.py
2) endpoints.py
3) database_functions.py

1. main.py

    Este script é o núcleo do sistema de envio de notificações push, integrando várias funcionalidades, desde a comunicação com o Firebase Cloud Messaging (FCM) até a interação com um banco de dados SQLite que gerencia tokens e registros de notificações. A aplicação Flask expõe uma API que pode ser utilizada para manipular esses dados.

    Fluxo Geral:
    - API Flask: Roda em segundo plano para fornecer endpoints que permitem a interação externa.
    - Agendamento: Uma função principal (main_xfunc()) é agendada para ser executada a cada 10 segundos para processar e enviar notificações.
    - Dependências:
        - Bibliotecas Externas:
            - requests: Realiza chamadas HTTP.
            - urllib3: Gerencia conexões HTTP com controle granular sobre o processo.
            - firebase_admin: Lida com autenticação e tokens de acesso para o Firebase.
            - schedule: Facilita o agendamento de tarefas em intervalos regulares.
            - logging: Captura e armazena logs de eventos e erros.
            - flask: Framework para a construção de APIs web.
            - flask_cors: Habilita CORS para permitir requisições de diferentes origens.
        
        - Módulo Local:
           - database_functions: Contém funções para manipular o banco de dados SQLite.
    
    - Principais Funções:
        - get_access_token(): Autentica e obtém um token de acesso do Firebase utilizando um certificado específico.
        - enviar_msg(params, idmsg): Envia uma mensagem via FCM. Verifica se o ID da mensagem já foi enviado para evitar duplicidade. Retorna o status do envio.
        - enviar_notificacao(token, idmsg, title, mensage): Utiliza o token do destinatário para enviar uma notificação com título e mensagem especificados. Se o envio for bem-sucedido, a notificação é marcada como enviada no banco de dados.
        - setando_enviado(idsEnviados): Envia uma lista de IDs de notificações já enviadas para um servidor externo para registro.
        - enviar_token(TOKEN, IDMSG, TITLE, MESSAGE, IMGSRC, URL): Monta a estrutura da mensagem e invoca enviar_msg para efetuar o envio via FCM.
        - chama_msg_noti(): Requisita do servidor externo a lista de notificações que precisam ser enviadas.
        - envia_id_noti(): Envia IDs das notificações que já foram enviadas para o servidor externo e, em caso de sucesso, limpa a lista de IDs enviados.
    
    - Fluxo Detalhado da Função main_xfunc():
        A função main_xfunc() é o coração do sistema, coordenando todas as etapas do processo de envio de notificações. Aqui está um detalhamento do seu fluxo:
		
     - Envio dos IDs de Notificações Já Enviadas (envia_id_noti):       
	   
       - A função começa chamando envia_id_noti(), que coleta IDs de notificações já enviadas da base de dados e tenta enviá-los ao servidor externo. Isso é repetido até três vezes em caso de falha.
       
       - Se os IDs forem enviados com sucesso, a lista de IDs é limpa, garantindo que não haja duplicações em futuras tentativas.



      - Obtenção de Novas Notificações do Servidor (chama_msg_noti):
         1. Em seguida, chama_msg_noti() faz uma requisição GET para o servidor externo, tentando obter notificações novas que ainda não foram processadas.
         2.  Se a resposta for bem-sucedida (status 200) e contiver notificações (items), essas notificações são extraídas e armazenadas no banco de dados local utilizando grava_notificacao().
         3.    Processamento das Notificações do Banco de Dados (retorna_notificacoes_nao_enviadas): 
         4.    Após armazenar as notificações obtidas do servidor externo, a função consulta o banco de dados local para recuperar notificações que ainda não foram enviadas (notificações com sent = 0).
         5.    Se houver notificações não enviadas, a função itera sobre cada uma delas.
         6.    Envio das Notificações (enviar_notificacao):
         7.    Para cada notificação não enviada, a função verifica se o representante associado à notificação possui tokens registrados (usando get_tokens()).
     	 8.    Se tokens forem encontrados, a notificação é enviada para cada token utilizando enviar_notificacao().
	 	 9.    Se o envio for bem-sucedido, a notificação é marcada como enviada no banco de dados (usando atualiza_notificacao_sent()).
     	 10.   Caso não haja tokens, é registrado um aviso no log de que o representante não possui tokens.

    Finalização:
    A função retorna "Executado" se todo o processo for completado sem erros. Se ocorrer algum erro durante o processo, ele é capturado e registrado nos logs.

    Execução:
           run_schedule(): A função run_schedule() mantém o agendamento contínuo da main_xfunc() a cada 10 segundos, garantindo que o processo de envio de notificações seja automatizado e contínuo.
           if __name__ == "__main__":: Quando o script é executado diretamente, ele inicializa o agendamento (run_schedule()) e inicia a API Flask na porta indicada, pronta para receber requisições externas.

2. Arquivo endpoints.py

**Este script contém a implementação de uma API Flask que permite operações CRUD (Create, Read, Update, Delete) sobre o banco de dados de tokens.**

Principais Endpoints:
   - /delete_db (GET): Deleta a tabela de tokens no banco de dados, essencialmente limpando todos os registros armazenados.
   - /delete_token (POST): Recebe um ID de representante no corpo da requisição e deleta todos os tokens associados a esse ID.
   - /return_all (GET): Retorna todos os tokens armazenados no banco de dados em formato JSON.
   - /register_token/<id_rep>/<token> (GET): Registra um novo token para um representante específico, identificados pelos parâmetros da URL.
   
   
   Execução:
   - run_schedule(): A função run_schedule() mantém o agendamento contínuo da main_xfunc() a cada 10 segundos, garantindo que o processo de envio de notificações seja automatizado e contínuo.
   - if __name__ == "__main__":: Quando o script é executado diretamente, ele inicializa o agendamento (run_schedule()) e inicia a API Flask na porta indicada, pronta para receber requisições externas.

    
3. Arquivo database_functions.py
    Este módulo gerencia a criação e manipulação de tabelas no banco de dados SQLite, responsável por armazenar tokens e notificações.

    Principais Funções:
    - create_db(): Cria as tabelas tokens e notifications no banco de dados se elas ainda não existirem. A tabela tokens armazena tokens FCM associados a representantes, enquanto a tabela notifications armazena notificações, seus conteúdos, e se foram enviadas ou não.
    - grava_notificacao(idnotificacao, idrepresentante, titulo, mensagem): Insere uma nova notificação na tabela notifications, evitando a duplicação de entradas.
    - atualiza_notificacao_sent(idnotificacao): Marca uma notificação como enviada atualizando o campo sent para 1.
    - retorna_ids_notificacoes_enviadas(): Retorna uma lista de IDs de notificações que já foram enviadas (onde sent = 1).
    - retorna_notificacoes_nao_enviadas(): Retorna uma lista de notificações que ainda não foram enviadas (sent = 0), para que possam ser processadas.
    - exclui_notificacoes_enviadas(): Remove do banco de dados as notificações que já foram enviadas.
    - grava_token(idrep, token): Insere um novo token na tabela tokens associado a um representante, verificando antes se o token já existe para evitar duplicação.
    - get_tokens(id_representante): Retorna todos os tokens associados a um representante específico, se a tabela tokens existir.
    - retorna_tudo_banco(): Retorna todos os registros na tabela tokens como uma lista de dicionários, facilitando a manipulação e exibição dos dados.
    - delete_token(id_representante): Remove todos os tokens associados a um representante específico da tabela tokens.
    - delete_db_query(): Exclui a tabela tokens do banco de dados, essencialmente resetando a base de dados.
    
---------------------------


*Arquitetura e Construção do Banco de Dados*
    O banco de dados utilizado neste sistema é um banco de dados SQLite, que é um sistema de gerenciamento de banco de dados leve e autônomo. SQLite é particularmente útil para aplicações que requerem um banco de dados embutido, com pouca complexidade, e sem a necessidade de um servidor de banco de dados separado. Este banco de dados é usado para armazenar tokens de dispositivos e informações sobre notificações push, facilitando o gerenciamento e o envio de notificações.

Estrutura das Tabelas
 O banco de dados SQLite é composto por duas tabelas principais:
   - Tabela tokens
>    Propósito: Armazenar os tokens do Firebase Cloud Messaging (FCM) associados aos representantes (usuários) da aplicação.

 Estrutura:
  -  id_token (INTEGER PRIMARY KEY AUTOINCREMENT): Chave primária, autoincremental, que identifica de forma única cada registro de token.
  - token (TEXT NOT NULL): Token FCM que será utilizado para enviar notificações push ao dispositivo específico.
- id_representante (INTEGER): Identificador do representante ao qual o token está associado. Isso permite que múltiplos tokens sejam associados a um único representante, suportando cenários onde o usuário pode estar logado em múltiplos dispositivos.

Tabela notifications:
> Propósito: Armazenar informações sobre as notificações push que devem ser enviadas ou já foram enviadas

Estrutura:
- idnotificacao (INTEGER PRIMARY KEY): Identificador único da notificação.
- idrepresentante (INTEGER): Identificador do representante que deve receber a notificação.
- titulo (TEXT): Título da notificação.
- mensagem (TEXT): Corpo da mensagem da notificação.
- sent (INTEGER): Indicador de status que mostra se a notificação foi enviada (0 para não enviada, 1 para enviada).
 
*Processo de Construção do Banco de Dados *

 A construção do banco de dados é realizada através da função create_db() no arquivo database_functions.py. Aqui está um detalhamento desse processo:
                
- Conexão com o Banco de Dados:

	A função create_db() inicia estabelecendo uma conexão com o banco de dados SQLite utilizando sqlite3.connect('tokens.db'). Se o banco de dados tokens.db não existir, ele será criado automaticamente.
 
 Um cursor (cursor) é então criado a partir da conexão. Esse cursor é utilizado para executar comandos SQL.

- Criação da Tabela tokens:
	Um comando SQL CREATE TABLE IF NOT EXISTS tokens é executado para criar a tabela tokens caso ela ainda não exista.
  - O comando define os campos id_token, token, e id_representante, conforme explicado acima. A cláusula PRIMARY KEY AUTOINCREMENT garante que cada registro tenha um identificador único e que este seja automaticamente incrementado.
   
   
   - Criação da Tabela notifications:
    Similarmente, um comando SQL CREATE TABLE IF NOT EXISTS notifications é executado para criar a tabela notifications se ela não existir.
  - Os campos idnotificacao, idrepresentante, titulo, mensagem, e sent são definidos, com idnotificacao sendo a chave primária.
    Finalização:
 - Após a execução dos comandos SQL, a função chama conn.commit() para confirmar as alterações no banco de dados, garantindo que as tabelas sejam efetivamente criadas.
 - Finalmente, a conexão com o banco de dados é encerrada com conn.close(), liberando os recursos.

Manipulação e Uso das Tabelas:
 Uma vez criadas, as tabelas tokens e notifications são manipuladas por várias funções dentro do sistema:
   - Inserção de Dados:
        Tokens são inseridos na tabela tokens através da função grava_token(idrep, token).
        Notificações são inseridas na tabela notifications através da função grava_notificacao(idnotificacao, idrepresentante, titulo, mensagem).
        - Consulta de Dados:
            - Tokens associados a um representante específico são recuperados usando a função get_tokens(id_representante).
            - Notificações que não foram enviadas são recuperadas usando a função retorna_notificacoes_nao_enviadas().
            - Notificações que já foram enviadas são recuperadas usando a função retorna_ids_notificacoes_enviadas().
        - Atualização de Dados:
            O status de uma notificação é atualizado para sent = 1 após o envio bem-sucedido usando a função atualiza_notificacao_sent(idnotificacao).
    - Exclusão de Dados:
       - Tokens podem ser excluídos usando a função delete_token(id_representante).
       - Tabelas inteiras podem ser excluídas (como a tabela tokens) usando a função delete_db_query().
       - Notificações enviadas podem ser excluídas com a função exclui_notificacoes_enviadas().

Considerações de Design
   - Chave Primária:  Ambas as tabelas utilizam chaves primárias (id_token e idnotificacao), que garantem a unicidade dos registros e facilitam consultas e operações de atualização/exclusão.
   - Associação entre Tabelas: A tabela notifications utiliza idreprsentante para associar notificações a representantes específicos. Este campo é crucial para o sistema, pois permite enviar notificações apenas para os representantes corretos.
        
Simplicidade e Eficiência: 
 O uso de SQLite é apropriado para este tipo de aplicação onde a simplicidade, baixo custo de setup e manutenção são críticos. SQLite oferece uma solução robusta sem a complexidade de sistemas de banco de dados maiores como MySQL ou PostgreSQL.

---------------------------

*Configurando projeto*

1) o arquivo main.py é o responsável pelo recebimento e envio das notificações. Como ele não escuta o mundo externo, ele pode rodar em uma porta secundária.
2) o arquivo endpoints.py, como o próprio nome sugere, contém os endpoints. Principalmente o endpointe que recebe os tokens FCM dos dispositvos junto com o id_representante. Por ter qe ficar escutando as requisições, ele deve rodar em uma porta que esteja com o acesso externo liberado.
3) o arquivo database_function.py, contém as funções com as querys que acessam, consomem e atualizam o banco de dados. Ele não tem que ser rodado, pois os outros dois arquivos importam as funções dele.

-----------------------------

*Comando para startar*

- uwsgi --http :5001 --wsgi-file main.py --callable app
- uwsgi --http :5000 --wsgi-file endpoints.py --callable app

