# 🐳 Guia de Instalação e Configuração do Docker Engine no WSL 2 (Ubuntu)

Este tutorial descreve o processo de instalação do **Docker Engine (nativo via CLI)** diretamente dentro da distribuição **Ubuntu no WSL 2**, dispensando a dependência obrigatória do Docker Desktop e garantindo alta performance e leveza.

---

## 🎯 Por que instalar o Docker Engine nativo no WSL 2?

* **Desempenho Elevado:** Execução direta no kernel Linux do WSL 2 sem overhead de interface gráfica.
* **Leveza de Recursos:** Consumo reduzido de memória RAM e CPU no Windows.
* **Ambiente de Produção:** Simula exatamente a infraestrutura de servidores Linux/Cloud.

---

## 🛠️ 1. Preparação do Ambiente Ubuntu

Abra o terminal do Ubuntu (no WSL 2) e certifique-se de remover versões antigas ou conflitantes do Docker:

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

Atualize o índice de pacotes e instale as dependências necessárias para download via HTTPS e suporte a chaves GPG:

```bash
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

---

## 🔑 2. Adicionar o Repositório Oficial do Docker

1. Crie o diretório para armazenar as chaves de segurança do APT:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

2. Baixe a chave GPG oficial do Docker:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

3. Adicione o repositório oficial do Docker às fontes do `apt`:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

## 📦 3. Instalação do Docker Engine e Componentes

Atualize novamente o repositório `apt` para reconhecer o Docker e instale os pacotes principais (Docker Engine, CLI, Containerd e Docker Compose):

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## 👤 4. Configuração de Permissões de Usuário (Sem necessidade de `sudo`)

Por padrão, o comando `docker` exige permissões de superusuário (`sudo`). Para permitir que seu usuário comum execute comandos do Docker:

1. Crie o grupo `docker` (caso não tenha sido criado automaticamente):

```bash
sudo groupadd docker
```

2. Adicione seu usuário atual (`$USER`) ao grupo `docker`:

```bash
sudo usermod -aG docker $USER
```

3. Aplique as novas permissões do grupo à sessão atual sem precisar deslogar:

```bash
newgrp docker
```

---

## 🚀 5. Inicialização e Teste do Serviço Docker

### Passo 1: Iniciar o Serviço do Docker
No WSL 2, o serviço do Docker deve ser iniciado via comando `service` ou `systemctl` (em distribuições com systemd habilitado):

```bash
sudo service docker start
```

*(Opcional - Habilitar `systemd` no WSL 2 para início automático)*:
Se o seu WSL tiver o `systemd` ativo em `/etc/wsl.conf`, você pode usar:
```bash
sudo systemctl enable --now docker
```

### Passo 2: Testar a Instalação com o Container Hello-World
Execute o contêiner oficial de teste para validar se o Docker está baixando e executando imagens corretamente:

```bash
docker run hello-world
```

Se a instalação foi bem-sucedida, você verá a mensagem:
```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## 🛠️ 6. Comandos Essenciais do Docker no WSL

| Comando | Descrição |
| :--- | :--- |
| **Verificar status do serviço** | `sudo service docker status` |
| **Iniciar o serviço Docker** | `sudo service docker start` |
| **Listar contêineres em execução** | `docker ps` |
| **Listar todos os contêineres** | `docker ps -a` |
| **Listar imagens baixadas** | `docker images` |
| **Executar um container interativo Ubuntu** | `docker run -it ubuntu bash` |
| **Executar Nginx em segundo plano** | `docker run -d -p 8080:80 nginx` |
| **Verificar versão do Docker e Compose** | `docker --version` e `docker compose version` |

---

## 🧠 7. Teste Prático de Serviço Web (Nginx)

Para testar a integração entre o Docker no WSL 2 e o navegador do Windows:

1. Suba um servidor web Nginx na porta `8080`:

```bash
docker run -d -p 8080:80 --name meu-nginx nginx
```

2. Abra o navegador no Windows (Chrome/Edge/Firefox) e acesse:
   * **`http://localhost:8080`**

Você verá a página de boas-vindas do Nginx rodando dentro do seu contêiner Docker no WSL 2!

3. Para parar e remover o contêiner de teste:

```bash
docker stop meu-nginx
docker rm meu-nginx
```
