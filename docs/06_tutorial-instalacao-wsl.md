# 🐧 Guia Completo de Instalação e Configuração do WSL no Windows 10 e 11

Este tutorial guia passo a passo a instalação do **WSL 2 (Windows Subsystem for Linux)** no Windows 10 e Windows 11, preparando o ambiente para execução de distribuições Linux (como Ubuntu) com suporte a contêineres e aceleração por hardware/GPU.

---

## 📋 Pré-requisitos do Sistema

| Requisito | Windows 10 | Windows 11 |
| :--- | :--- | :--- |
| **Edição** | Home, Pro, Enterprise ou Education | Home, Pro, Enterprise ou Education |
| **Versão/Build** | Versão 2004 ou superior (Build 19041+) | Todas as versões e builds suportadas |
| **Arquitetura** | x64 ou ARM64 | x64 ou ARM64 |
| **Virtualização** | Habilitada na BIOS/UEFI (Intel VT-x / AMD-V) | Habilitada na BIOS/UEFI (Intel VT-x / AMD-V) |

> 💡 **Como verificar a versão do Windows:** Pressione `Win + R`, digite `winver` e pressione **Enter**.

---

## 🛠️ 1. Verificação da Virtualização na BIOS/UEFI

Antes de iniciar os comandos no Windows, a virtualização de hardware deve estar ativa:
1. Abra o **Gerenciador de Tarefas** (`Ctrl + Shift + Esc`).
2. Vá até a aba **Desempenho** ➔ **CPU**.
3. Verifique o campo **Virtualização**: deve constar como **Habilitado**.
   * *Caso esteja "Desabilitado", acesse a BIOS/UEFI do computador e ative "Intel VT-x", "Intel Virtualization Technology" ou "AMD-V / SVM Mode".*

---

## 🚀 2. Método Rápido (Recomendado para Windows 10 e 11)

Nos sistemas operacionais atualizados, a instalação do WSL 2 pode ser feita com um único comando.

### Passo 1: Abrir o Terminal como Administrador
* Clique com o botão direito no menu **Iniciar** e selecione:
  * No **Windows 11**: **Terminal (Administrador)** ou **PowerShell (Administrador)**.
  * No **Windows 10**: **Windows PowerShell (Administrador)**.

### Passo 2: Executar o Comando de Instalação
No PowerShell, digite o comando abaixo:

```powershell
wsl --install
```

Este comando automatizado realiza as seguintes ações:
1. Habilita as funcionalidades de plataforma de máquina virtual e WSL no Windows.
2. Baixa e instala o kernel Linux mais recente.
3. Define o **WSL 2** como versão padrão.
4. Baixa e instala a distribuição **Ubuntu** padrão.

### Passo 3: Reiniciar o Computador
Após a conclusão do comando, **reinicie a máquina**:

```powershell
shutdown /r /t 0
```

---

## 🛠️ 3. Método Manual (Para Builds Antigas ou Solução de Problemas)

Caso o comando `wsl --install` apresente erros ou esteja em uma versão mais antiga do Windows 10 (Builds anteriores a 19041), siga os passos manuais:

### Passo 1: Habilitar o Subsistema Windows para Linux
Abra o PowerShell como Administrador e execute:

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

### Passo 2: Habilitar a Plataforma de Máquina Virtual
Ainda no PowerShell Administrador, execute:

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### Passo 3: Reiniciar o Sistema
Reinicie o computador para aplicar os recursos habilitados.

### Passo 4: Baixar e Instalar o Pacote de Atualização do Kernel do WSL 2
1. Baixe o instalador oficial do kernel Linux para máquinas x64:
   * [Pacote de atualização do kernel do WSL 2 (MSI)](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)
2. Execute o arquivo `.msi` baixado e siga o assistente de instalação.

### Passo 5: Definir o WSL 2 como Versão Padrão
No PowerShell, defina a versão 2 como padrão para novas distribuições:

```powershell
wsl --set-default-version 2
```

---

## 📦 4. Instalação e Primeira Configuração do Ubuntu

1. Abra a **Microsoft Store** e pesquise por **Ubuntu** (ou escolha uma versão específica como **Ubuntu 24.04 LTS**).
2. Clique em **Obter** / **Instalar**.
3. Após a instalação, abra a aplicação **Ubuntu** pelo Menu Iniciar ou digite `wsl` no PowerShell/Terminal.
4. Aguarde a inicialização inicial (pode levar alguns minutos).
5. Defina um **Nome de Usuário (UNIX username)** e uma **Senha (password)** para a sua distribuição Linux.
   > ⚠️ **Atenção:** Ao digitar a senha no terminal Linux, nenhum caractere será exibido na tela por questões de segurança. Digite a senha e pressione **Enter**.

---

## 🔍 5. Comandos Úteis do WSL

| Ação | Comando (PowerShell / CMD) |
| :--- | :--- |
| **Listar distros e versões ativas** | `wsl --list --verbose` ou `wsl -l -v` |
| **Entrar na distribuição padrão** | `wsl` |
| **Entrar como usuário root** | `wsl -u root` |
| **Desligar todas as instâncias do WSL** | `wsl --shutdown` |
| **Definir distro para usar WSL 2** | `wsl --set-version <NomeDistro> 2` |
| **Exportar backup de uma distro** | `wsl --export <NomeDistro> backup.tar` |
| **Importar backup de uma distro** | `wsl --import <NomeDistro> <CaminhoDestino> backup.tar` |
| **Atualizar o Kernel do WSL** | `wsl --update` |

---

## 🚀 6. Atualizando o Ubuntu (Dentro do WSL)

Ao entrar no terminal Ubuntu, recomenda-se atualizar os repositórios e pacotes do sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

Pronto! Seu ambiente **WSL 2 com Ubuntu** está instalado, configurado e pronto para a instalação de ferramentas de desenvolvimento como **Docker Engine**, **Python**, **Git** e suporte a **NVIDIA CUDA**.
