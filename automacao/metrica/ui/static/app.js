async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data;
}

const el = {
  status: document.getElementById('status'),
  runReal: document.getElementById('run-real'),
  runDry: document.getElementById('run-dry'),
  stop: document.getElementById('stop'),
  configPath: document.getElementById('config-path'),
  output: document.getElementById('job-output'),
  logsList: document.getElementById('logs-list'),
  logContent: document.getElementById('log-content'),
  checklistStats: document.getElementById('checklist-stats'),
  checklistBox: document.getElementById('checklist-content'),
  refreshChecklist: document.getElementById('refresh-checklist'),
  refreshLogs: document.getElementById('refresh-logs'),
  jobMeta: document.getElementById('job-meta'),

  batchProjects: document.getElementById('batch-projects'),
  batchRunReal: document.getElementById('batch-run-real'),
  batchRunDry: document.getElementById('batch-run-dry'),
  batchStop: document.getElementById('batch-stop'),
  batchStatus: document.getElementById('batch-status'),
  batchMeta: document.getElementById('batch-meta'),
  batchItems: document.getElementById('batch-items'),
};

let selectedLogName = null;

function setBadge(node, status) {
  const label = status || 'idle';
  node.className = `badge ${label}`;
  node.textContent = label.toUpperCase();
}

function showError(err) {
  alert(err.message || String(err));
}

function renderOutput(lines) {
  el.output.textContent = (lines || []).join('\n');
  el.output.scrollTop = el.output.scrollHeight;
}

function renderLogs(logsPayload) {
  const files = logsPayload.files || [];
  const selected = logsPayload.selected;
  if (!selectedLogName && selected) {
    selectedLogName = selected.name;
  }

  el.logsList.innerHTML = '';
  files.forEach((f) => {
    const item = document.createElement('div');
    item.className = 'list-item' + (selectedLogName === f.name ? ' active' : '');
    item.innerHTML = `<strong>${f.name}</strong><div class="small">${f.modified} | ${f.size} bytes</div>`;
    item.onclick = async () => {
      selectedLogName = f.name;
      await loadLogs();
    };
    el.logsList.appendChild(item);
  });

  el.logContent.textContent = logsPayload.content || '';
}

function renderChecklist(data) {
  const done = data.stats?.done || 0;
  const total = data.stats?.total || 0;
  el.checklistStats.textContent = `${done}/${total} concluido`;
  el.checklistBox.textContent = data.content || '';
}

function renderBatch(batch) {
  if (!batch) {
    setBadge(el.batchStatus, 'idle');
    el.batchMeta.textContent = 'Nenhum lote em execucao.';
    el.batchItems.innerHTML = '';
    el.batchStop.disabled = true;
    return;
  }

  setBadge(el.batchStatus, batch.status || 'idle');
  const doneCount = (batch.items || []).filter((i) => i.status === 'completed').length;
  const failCount = (batch.items || []).filter((i) => i.status === 'failed').length;
  const stopCount = (batch.items || []).filter((i) => i.status === 'stopped' || i.status === 'skipped').length;
  el.batchMeta.textContent = `Lote ${batch.id} | ${batch.current_index}/${batch.total} | ok=${doneCount} falhas=${failCount} parados=${stopCount}`;

  el.batchItems.innerHTML = '';
  (batch.items || []).forEach((item) => {
    const row = document.createElement('div');
    row.className = 'list-item';
    const statusClass = `status-${item.status || 'pending'}`;
    const err = item.error ? `<div class="small" style="color:#b42318;">${item.error}</div>` : '';
    row.innerHTML = `
      <div>
        <strong>#${item.index}</strong>
        <span class="item-status ${statusClass}">${(item.status || 'pending').toUpperCase()}</span>
      </div>
      <div class="small">${item.project_path || ''}</div>
      <div class="small">rc: ${item.return_code ?? '-'} | inicio: ${item.started_at || '-'} | fim: ${item.ended_at || '-'}</div>
      ${err}
    `;
    el.batchItems.appendChild(row);
  });

  const running = batch.status === 'running';
  el.batchStop.disabled = !running;
}

async function loadStatus() {
  const data = await api('/api/status');
  const current = data.current;
  const batch = data.batch_current;

  setBadge(el.status, current?.status || 'idle');
  renderBatch(batch);

  if (current) {
    el.jobMeta.textContent = `id: ${current.id} | inicio: ${current.started_at} | fim: ${current.ended_at || '-'} | rc: ${current.return_code ?? '-'}`;
    renderOutput(current.output_tail || []);
  } else {
    el.jobMeta.textContent = 'Nenhuma execucao iniciada.';
    renderOutput([]);
  }

  const jobRunning = current && current.status === 'running';
  const batchRunning = batch && batch.status === 'running';

  el.runReal.disabled = jobRunning || batchRunning;
  el.runDry.disabled = jobRunning || batchRunning;
  el.stop.disabled = !jobRunning;
  el.batchRunReal.disabled = jobRunning || batchRunning;
  el.batchRunDry.disabled = jobRunning || batchRunning;

  const cstats = data.checklist_stats || { done: 0, total: 0 };
  el.checklistStats.textContent = `${cstats.done}/${cstats.total} concluido`;
}

async function loadChecklist() {
  const data = await api('/api/checklist');
  renderChecklist(data);
}

async function loadLogs() {
  const qs = selectedLogName ? `?name=${encodeURIComponent(selectedLogName)}&lines=300` : '?lines=300';
  const data = await api('/api/logs' + qs);
  if (data.selected) {
    selectedLogName = data.selected.name;
  }
  renderLogs(data);
}

async function runJob(dryRun) {
  try {
    await api('/api/run', {
      method: 'POST',
      body: JSON.stringify({
        dry_run: dryRun,
        config_path: el.configPath.value.trim(),
      }),
    });
    await refreshAll();
  } catch (err) {
    showError(err);
  }
}

function getBatchProjects() {
  return (el.batchProjects.value || '')
    .split(/\r?\n/)
    .map((s) => s.trim())
    .filter((s) => s && !s.startsWith('#') && !s.startsWith(';'));
}

async function runBatch(dryRun) {
  try {
    const projects = getBatchProjects();
    if (!projects.length) {
      throw new Error('Informe ao menos um projeto no campo de lotes.');
    }

    await api('/api/batch/start', {
      method: 'POST',
      body: JSON.stringify({
        dry_run: dryRun,
        config_path: el.configPath.value.trim(),
        projects,
      }),
    });
    await refreshAll();
  } catch (err) {
    showError(err);
  }
}

async function stopBatch() {
  try {
    await api('/api/batch/stop', { method: 'POST', body: '{}' });
    await refreshAll();
  } catch (err) {
    showError(err);
  }
}

async function stopJob() {
  try {
    await api('/api/stop', { method: 'POST', body: '{}' });
    await refreshAll();
  } catch (err) {
    showError(err);
  }
}

async function refreshAll() {
  try {
    await Promise.all([loadStatus(), loadLogs(), loadChecklist()]);
  } catch (err) {
    console.error(err);
  }
}

el.runReal.onclick = () => runJob(false);
el.runDry.onclick = () => runJob(true);
el.stop.onclick = () => stopJob();
el.batchRunReal.onclick = () => runBatch(false);
el.batchRunDry.onclick = () => runBatch(true);
el.batchStop.onclick = () => stopBatch();
el.refreshChecklist.onclick = () => loadChecklist();
el.refreshLogs.onclick = () => loadLogs();

refreshAll();
setInterval(refreshAll, 2500);
