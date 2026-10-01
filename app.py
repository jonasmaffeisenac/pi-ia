import subprocess
import time
from typing import Any, Dict, List, Optional
from flask import Flask, jsonify, render_template_string, request
import psutil

app = Flask(__name__)

# Cache para taxas de transferência
_prev_net_io: Optional[Any] = None
_prev_disk_io: Optional[Any] = None
_prev_io_time: Optional[float] = None


def get_amd_gpu_metrics() -> Dict[str, Any]:
    """Coleta métricas de utilização da GPU AMD via PowerShell PDH ou rocm-smi."""
    usage: Any = "N/A"
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            '(((Get-Counter "\\GPU Engine(*engtype_3D)\\Utilization Percentage" -ErrorAction SilentlyContinue).CounterSamples | Measure-Object -Property CookedValue -Sum).Sum)'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        val = res.stdout.strip()
        if val:
            usage = round(float(val.replace(',', '.')), 1)
    except Exception:
        pass

    if usage == "N/A":
        try:
            res = subprocess.run(["rocm-smi", "--showuse"], capture_output=True, text=True, timeout=2)
            for line in res.stdout.splitlines():
                if "%" in line:
                    for token in line.split():
                        if "%" in token:
                            usage = float(token.replace('%', '').strip())
                            break
        except Exception:
            pass

    return {"usage": usage}


def get_system_uptime() -> str:
    """Calcula o tempo de atividade do sistema."""
    try:
        boot_seconds = time.time() - psutil.boot_time()
        hours, remainder = divmod(int(boot_seconds), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"
    except Exception:
        return "N/A"


def get_all_disks() -> List[Dict[str, Any]]:
    """Obtém uso de todas as partições de disco ativas."""
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device.replace('\\', ''),
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "percent": usage.percent
            })
        except (PermissionError, OSError):
            continue
    return disks


def get_io_rates() -> Dict[str, str]:
    """Calcula taxas de transferência por segundo para Rede e Disco."""
    global _prev_net_io, _prev_disk_io, _prev_io_time

    current_time = time.time()
    try:
        curr_net = psutil.net_io_counters()
        curr_disk = psutil.disk_io_counters()
    except Exception:
        return {"net_down": "0.0 KB/s", "net_up": "0.0 KB/s", "disk_read": "0.0 MB/s", "disk_write": "0.0 MB/s"}

    rates = {
        "net_down": "0.0 KB/s",
        "net_up": "0.0 KB/s",
        "disk_read": "0.0 MB/s",
        "disk_write": "0.0 MB/s"
    }

    if _prev_io_time and _prev_net_io and _prev_disk_io:
        dt = current_time - _prev_io_time
        if dt > 0:
            rx_sec = (curr_net.bytes_recv - _prev_net_io.bytes_recv) / dt
            tx_sec = (curr_net.bytes_sent - _prev_net_io.bytes_sent) / dt
            rates["net_down"] = f"{rx_sec / 1024:.1f} KB/s" if rx_sec < 1048576 else f"{rx_sec / 1048576:.2f} MB/s"
            rates["net_up"] = f"{tx_sec / 1024:.1f} KB/s" if tx_sec < 1048576 else f"{tx_sec / 1048576:.2f} MB/s"

            r_sec = (curr_disk.read_bytes - _prev_disk_io.read_bytes) / dt
            w_sec = (curr_disk.write_bytes - _prev_disk_io.write_bytes) / dt
            rates["disk_read"] = f"{r_sec / 1048576:.1f} MB/s"
            rates["disk_write"] = f"{w_sec / 1048576:.1f} MB/s"

    _prev_net_io = curr_net
    _prev_disk_io = curr_disk
    _prev_io_time = current_time
    return rates


def get_top_processes(limit: int = 40) -> List[Dict[str, Any]]:
    """Extrai top processos consumidores de CPU e Memória."""
    procs: List[Dict[str, Any]] = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            procs.append({
                'pid': info['pid'],
                'name': info['name'] or 'N/A',
                'cpu': round(info['cpu_percent'] or 0.0, 1),
                'mem': round(info['memory_percent'] or 0.0, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    procs.sort(key=lambda x: (x['cpu'], x['mem']), reverse=True)
    return procs[:limit]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Monitor de Desempenho Windows Pro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
        h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; }
        .meta-tags { display: flex; gap: 10px; }
        .badge { background: #1e293b; border: 1px solid #334155; font-size: 12px; padding: 6px 12px; border-radius: 6px; color: #94a3b8; }
        
        /* Barra de Alerta/Status Geral */
        #health-banner {
            padding: 10px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #14532d;
            color: #86efac;
            border: 1px solid #166534;
        }

        .section-title { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin: 20px 0 10px 0; font-weight: 700; }
        
        /* Grid Principal */
        .grid-main { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 20px; }
        .card { background: #1e293b; border-radius: 10px; padding: 18px; border: 1px solid #334155; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .card-title { font-size: 13px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
        .value { font-size: 28px; font-weight: 700; margin-bottom: 12px; color: #38bdf8; }
        .progress-bg { background: #334155; border-radius: 999px; height: 8px; overflow: hidden; }
        .progress-bar { height: 100%; width: 0%; background: #22c55e; transition: width 0.3s ease, background 0.3s ease; }
        
        /* CPU por Núcleos */
        .cores-panel { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; margin-bottom: 20px; }
        .cores-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; margin-top: 10px; }
        .core-box { background: #0f172a; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #334155; }
        .core-lbl { font-size: 10px; color: #94a3b8; margin-bottom: 4px; }
        .core-val { font-size: 12px; font-weight: 700; margin-bottom: 4px; }
        .core-bar-bg { background: #1e293b; height: 4px; border-radius: 2px; overflow: hidden; }
        .core-bar { height: 100%; width: 0%; background: #38bdf8; }

        /* Discos Múltiplos */
        .disks-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .disk-card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; }
        .disk-header { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: #94a3b8; }
        .disk-stats { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }

        /* Subcard de Taxas de I/O */
        .grid-io { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }
        .io-item { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px; }
        .io-label { font-size: 12px; color: #94a3b8; margin-bottom: 4px; }
        .io-val { font-size: 18px; font-weight: 600; color: #e2e8f0; }

        /* Gráfico Canvas */
        .chart-panel { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 18px; margin-bottom: 24px; }
        .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .legend { display: flex; gap: 14px; font-size: 12px; }
        .dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px; }
        canvas { width: 100%; height: 110px; background: #0f172a; border-radius: 6px; display: block; }

        /* Tabela e Busca de Processos */
        .panel { background: #1e293b; border-radius: 10px; padding: 18px; border: 1px solid #334155; }
        .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px; }
        .search-box {
            background: #0f172a;
            border: 1px solid #334155;
            color: #f8fafc;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
            width: 250px;
        }
        .search-box:focus { border-color: #38bdf8; }
        .table-wrapper { overflow-x: auto; max-height: 400px; overflow-y: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        th { background: #0f172a; color: #94a3b8; padding: 10px 12px; position: sticky; top: 0; font-weight: 600; border-bottom: 1px solid #334155; }
        td { padding: 8px 12px; border-bottom: 1px solid #334155; color: #cbd5e1; vertical-align: middle; }
        tr:hover { background: #243248; }
        .num { text-align: right; font-variant-numeric: tabular-nums; }
        .btn-kill {
            background: #450a0a;
            border: 1px solid #991b1b;
            color: #fca5a5;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-kill:hover { background: #dc2626; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Monitor de Desempenho Windows</h1>
                <p style="color: #64748b; font-size: 13px; margin-top: 4px;">Painel de Controle e Diagnóstico em Tempo Real</p>
            </div>
            <div class="meta-tags">
                <div class="badge" id="badge-uptime">Uptime: --</div>
                <div class="badge" id="badge-cores">Núcleos: --</div>
            </div>
        </header>

        <!-- 3. Status de Saúde Geral -->
        <div id="health-banner">
            <span id="health-text">Carregando status do sistema...</span>
            <span id="health-time" style="font-size: 11px; opacity: 0.8;"></span>
        </div>

        <div class="section-title">Componentes Primários</div>
        <div class="grid-main">
            <div class="card">
                <div class="card-header"><span class="card-title">CPU Total</span></div>
                <div class="value" id="val-cpu">-</div>
                <div class="progress-bg"><div class="progress-bar" id="bar-cpu"></div></div>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">Memória RAM</span></div>
                <div class="value" id="val-ram">-</div>
                <div class="progress-bg"><div class="progress-bar" id="bar-ram"></div></div>
            </div>
            <div class="card">
                <div class="card-header"><span class="card-title">GPU AMD</span></div>
                <div class="value" id="val-gpu">-</div>
                <div class="progress-bg"><div class="progress-bar" id="bar-gpu"></div></div>
            </div>
        </div>

        <!-- 1. Carga por Núcleo de CPU -->
        <div class="cores-panel">
            <span class="card-title">Carga por Núcleo Lógico</span>
            <div class="cores-grid" id="cores-container"></div>
        </div>

        <!-- 4. Todas as Unidades de Armazenamento -->
        <div class="section-title">Armazenamento & Partições</div>
        <div class="disks-grid" id="disks-container"></div>

        <div class="section-title">Taxas de Transferência I/O</div>
        <div class="grid-io">
            <div class="io-item">
                <div class="io-label">Download de Rede</div>
                <div class="io-val" id="val-net-down">0.0 KB/s</div>
            </div>
            <div class="io-item">
                <div class="io-label">Upload de Rede</div>
                <div class="io-val" id="val-net-up">0.0 KB/s</div>
            </div>
            <div class="io-item">
                <div class="io-label">Leitura em Disco</div>
                <div class="io-val" id="val-disk-r">0.0 MB/s</div>
            </div>
            <div class="io-item">
                <div class="io-label">Escrita em Disco</div>
                <div class="io-val" id="val-disk-w">0.0 MB/s</div>
            </div>
        </div>

        <div class="chart-panel">
            <div class="chart-header">
                <span class="card-title">Tendência Temporal (Últimos 60s)</span>
                <div class="legend">
                    <div><span class="dot" style="background: #38bdf8;"></span>CPU</div>
                    <div><span class="dot" style="background: #a855f7;"></span>RAM</div>
                </div>
            </div>
            <canvas id="timelineChart" width="1160" height="110"></canvas>
        </div>

        <!-- 2. Processos com Filtro de Busca e 5. Botão de Finalizar -->
        <div class="panel">
            <div class="panel-header">
                <span class="card-title" style="margin: 0;">Processos Ativos</span>
                <input type="text" id="proc-search" class="search-box" placeholder="Filtrar por nome ou PID...">
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 80px;">PID</th>
                            <th>Nome do Processo</th>
                            <th class="num" style="width: 100px;">CPU (%)</th>
                            <th class="num" style="width: 100px;">Memória (%)</th>
                            <th style="width: 80px; text-align: center;">Ação</th>
                        </tr>
                    </thead>
                    <tbody id="proc-list">
                        <tr><td colspan="5" style="text-align: center; color: #64748b;">Carregando...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const cpuHistory = new Array(30).fill(0);
        const ramHistory = new Array(30).fill(0);
        let rawProcessList = [];

        function getColor(pct) {
            if (pct >= 85) return '#ef4444';
            if (pct >= 70) return '#f59e0b';
            return '#22c55e';
        }

        function setMetric(name, val) {
            const valEl = document.getElementById('val-' + name);
            const barEl = document.getElementById('bar-' + name);

            if (val === 'N/A' || isNaN(val)) {
                valEl.innerText = 'N/A';
                barEl.style.width = '0%';
                return;
            }

            const pct = Math.min(Math.max(val, 0), 100);
            valEl.innerText = pct.toFixed(1) + '%';
            barEl.style.width = pct + '%';
            barEl.style.background = getColor(pct);
        }

        function updateHealthStatus(cpu, ram) {
            const banner = document.getElementById('health-banner');
            const text = document.getElementById('health-text');
            document.getElementById('health-time').innerText = new Date().toLocaleTimeString();

            if (cpu >= 90 || ram >= 90) {
                banner.style.background = '#450a0a';
                banner.style.color = '#fca5a5';
                banner.style.borderColor = '#991b1b';
                text.innerText = '⚠️ CRÍTICO: Uso extremo de recursos detectado (' + (cpu >= 90 ? 'CPU ' : '') + (ram >= 90 ? 'RAM' : '') + ')';
            } else if (cpu >= 75 || ram >= 80) {
                banner.style.background = '#451a03';
                banner.style.color = '#fdba74';
                banner.style.borderColor = '#9a3412';
                text.innerText = '⚡ ALERTA: Consumo elevado de recursos em execução.';
            } else {
                banner.style.background = '#14532d';
                banner.style.color = '#86efac';
                banner.style.borderColor = '#166534';
                text.innerText = '✓ Sistema Saudável - Operação Nominal';
            }
        }

        function renderCores(cores) {
            const container = document.getElementById('cores-container');
            container.innerHTML = cores.map((val, idx) => `
                <div class="core-box">
                    <div class="core-lbl">C${idx}</div>
                    <div class="core-val" style="color: ${getColor(val)}">${val.toFixed(0)}%</div>
                    <div class="core-bar-bg">
                        <div class="core-bar" style="width: ${val}%; background: ${getColor(val)};"></div>
                    </div>
                </div>
            `).join('');
        }

        function renderDisks(disks) {
            const container = document.getElementById('disks-container');
            container.innerHTML = disks.map(d => `
                <div class="disk-card">
                    <div class="disk-header">
                        <span>${d.device} (${d.mountpoint})</span>
                        <span>${d.percent}%</span>
                    </div>
                    <div class="disk-stats">${d.used_gb} / ${d.total_gb} GB</div>
                    <div class="progress-bg">
                        <div class="progress-bar" style="width: ${d.percent}%; background: ${getColor(d.percent)};"></div>
                    </div>
                </div>
            `).join('');
        }

        function renderProcesses() {
            const filter = document.getElementById('proc-search').value.toLowerCase();
            const tbody = document.getElementById('proc-list');
            
            const filtered = rawProcessList.filter(p => 
                p.name.toLowerCase().includes(filter) || String(p.pid).includes(filter)
            );

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #64748b;">Nenhum processo correspondente.</td></tr>';
                return;
            }

            tbody.innerHTML = filtered.map(p => `
                <tr>
                    <td>${p.pid}</td>
                    <td>${p.name}</td>
                    <td class="num">${p.cpu.toFixed(1)}%</td>
                    <td class="num">${p.mem.toFixed(1)}%</td>
                    <td style="text-align: center;">
                        <button class="btn-kill" onclick="killProcess(${p.pid}, '${p.name}')">Encerrar</button>
                    </td>
                </tr>
            `).join('');
        }

        async function killProcess(pid, name) {
            if (!confirm(`Deseja realmente encerrar o processo ${name} (PID: ${pid})?`)) return;
            try {
                const res = await fetch(`/api/kill/${pid}`, { method: 'POST' });
                const json = await res.json();
                alert(json.message);
                updateDashboard();
            } catch (e) {
                alert('Erro ao enviar comando de encerramento.');
            }
        }

        document.getElementById('proc-search').addEventListener('input', renderProcesses);

        function drawChart() {
            const canvas = document.getElementById('timelineChart');
            if (!canvas.getContext) return;
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;

            ctx.clearRect(0, 0, w, h);
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            for (let y = 0; y <= h; y += 28) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }

            function drawLine(data, color) {
                ctx.beginPath();
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                const step = w / (data.length - 1);
                data.forEach((val, i) => {
                    const x = i * step;
                    const y = h - (val / 100 * (h - 10)) - 5;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
            }

            drawLine(cpuHistory, '#38bdf8');
            drawLine(ramHistory, '#a855f7');
        }

        async function updateDashboard() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                setMetric('cpu', data.cpu);
                setMetric('ram', data.ram);
                setMetric('gpu', data.gpu.usage);

                updateHealthStatus(data.cpu, data.ram);
                renderCores(data.cpu_cores || []);
                renderDisks(data.disks || []);

                document.getElementById('badge-uptime').innerText = 'Uptime: ' + data.uptime;
                document.getElementById('badge-cores').innerText = 'Núcleos: ' + data.cores;

                document.getElementById('val-net-down').innerText = data.io.net_down;
                document.getElementById('val-net-up').innerText = data.io.net_up;
                document.getElementById('val-disk-r').innerText = data.io.disk_read;
                document.getElementById('val-disk-w').innerText = data.io.disk_write;

                cpuHistory.shift();
                cpuHistory.push(isNaN(data.cpu) ? 0 : data.cpu);
                ramHistory.shift();
                ramHistory.push(isNaN(data.ram) ? 0 : data.ram);
                drawChart();

                rawProcessList = data.processes || [];
                renderProcesses();
            } catch (e) {}
        }

        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def stats():
    return jsonify({
        'cpu': psutil.cpu_percent(interval=None),
        'cpu_cores': psutil.cpu_percent(interval=None, percpu=True),
        'ram': psutil.virtual_memory().percent,
        'disks': get_all_disks(),
        'gpu': get_amd_gpu_metrics(),
        'uptime': get_system_uptime(),
        'cores': psutil.cpu_count(logical=True),
        'io': get_io_rates(),
        'processes': get_top_processes()
    })

@app.route('/api/kill/<int:pid>', methods=['POST'])
def kill_process(pid: int):
    """Encerra um processo específico por PID."""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()
        return jsonify({'success': True, 'message': f"Processo '{proc_name}' (PID: {pid}) encerrado."}), 200
    except psutil.NoSuchProcess:
        return jsonify({'success': False, 'message': "Processo já encerrado ou inexistente."}), 404
    except psutil.AccessDenied:
        return jsonify({'success': False, 'message': "Acesso negado: requer privilégios de Administrador."}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': f"Falha ao encerrar: {str(e)}"}), 500

if __name__ == '__main__':
    for p in psutil.process_iter(['cpu_percent']):
        pass
    psutil.cpu_percent(interval=None, percpu=True)
    get_io_rates()
    app.run(host='0.0.0.0', port=5000, debug=False)
