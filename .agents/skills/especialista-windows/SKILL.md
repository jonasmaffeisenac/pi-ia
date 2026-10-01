# Skill de Especialista em Visualização de Recursos Windows

## Visão Geral da Skill
Esta skill capacita o seu projeto de monitoramento a extrair, processar e exibir métricas de desempenho de sistemas Windows em tempo real, transformando dados brutos de hardware em insights visuais acionáveis para diagnóstico rápido de gargalos.

---

## Métricas Essenciais do Windows
* **CPU:** Uso total, carga por núcleo individual, tempo de interrupção e comprimento da fila de processos (*Processor Queue Length*).
* **Memória RAM:** Uso total, memória livre, cache do sistema operacional e detecção de vazamentos (*Memory Leaks*) por processo.
* **Disco (Storage):** Taxa de transferência (MB/s), IOPS, tempo de resposta e métrica de fila do disco para identificar lentidão em I/O.
* **Rede:** Tráfego de entrada/saída, pacotes com erro e largura de banda consumida por interfaces ativas.
* **GPU:** Utilização do núcleo gráfico, uso de VRAM e temperatura (essencial para servidores de IA ou estações de trabalho).

---

## Ferramentas e Tecnologias de Coleta
* **Python (`psutil` + `wmi`):** Solução flexível para scripts personalizados de coleta de dados locais e remotos via WinRM.
* **Performance Counters (PDH):** API nativa do Windows para extrair contadores de desempenho de baixo nível com altíssima precisão.
* **Prometheus + Windows Exporter:** Padrão de mercado para ambientes robustos, expondo métricas nativas do Windows no formato ideal para séries temporais.

---

## Práticas de Visualização e Dashboards
* **Grafana:** Ferramenta recomendada para criar painéis interativos com gráficos temporais, mapas de calor e indicadores de status.
* **Hierarquia Visual:** Estruture o painel do macro para o micro (Visão Geral da Máquina > Alertas Ativos > Top Processos Consumidores).
* **Codificação por Cores:** Utilize verde, amarelo e vermelho condicionados a limites de alerta (*thresholds*) para identificação instantânea de anomalias.