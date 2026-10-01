# Manual de Execução - Monitor de Recursos Windows

Manual de instalação e inicialização do monitor de desempenho em tempo real desenvolvido em Python/Flask.

---

## 1. Pré-requisitos

- **Sistema Operacional:** Windows 10/11 ou Windows Server
- **Python:** Versão 3.10 ou superior instalada e configurada no `PATH`
- **Privilégios:** Recomenda-se executar o terminal como **Administrador** caso queira utilizar a funcionalidade de encerramento de processos do sistema operacional.

---

## 2. Instalação das Dependências

Abra o terminal (PowerShell ou CMD) na pasta do projeto e instale as bibliotecas necessárias:

```powershell
pip install flask psutil
```

---

## 3. Executando a Aplicação

Inicie o servidor Flask:

```powershell
python app.py
```

Você verá a confirmação do Flask indicando que o servidor está rodando:

```text
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://<seu-ip-local>:5000
```

---

## 4. Acessando a Interface

Abra qualquer navegador web e acesse:

- **Acesso local:** [http://localhost:5000](http://localhost:5000)
- **Acesso na rede local:** `http://<IP-DO-SEU-COMPUTADOR>:5000`

---

## 5. Funcionalidades do Painel

1. **Visão Geral:** Métricas consolidadas de CPU, Memória RAM e GPU AMD com alertas semafóricos.
2. **Carga por Núcleo:** Visualização detalhada do consumo individual de cada núcleo lógico de processamento.
3. **Armazenamento:** Monitoramento de espaço usado e total de todas as partições ativas (`C:`, `D:`, etc.).
4. **Taxas de I/O em Tempo Real:** Velocidade atual de Download/Upload de rede e Leitura/Escrita em disco.
5. **Tendência Temporal (Últimos 60s):** Gráfico em linha nativo mostrando o comportamento de CPU e Memória ao longo do tempo.
6. **Gerenciador de Processos:**
   - Campo de busca instantâneo por Nome ou PID.
   - Botão **Encerrar** para finalizar processos diretamente pelo navegador (requer confirmação).

---

## 6. Encerrando o Servidor

Para parar a execução do monitor, pressione `Ctrl + C` no terminal onde o script está em execução.
