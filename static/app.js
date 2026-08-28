// ==========================================================================
// Agency Subagents Manager 2.0 — App Logic & Minimalist State Store
// ==========================================================================

// 全域狀態管理 (Single Source of Truth)
const state = {
  divisions: [],
  agents: [],
  destinations: [],
  selectedIds: new Set(),
  favorites: new Set(JSON.parse(localStorage.getItem('agency_favorites_v1') || '[]')),
  recentProjects: JSON.parse(localStorage.getItem('agency_recent_projects_v1') || '[]'),
  
  // 當前篩選與操作狀態
  currentDivision: 'all',
  currentStatusFilter: 'all', // 'all' | 'installed' | 'favorites'
  currentTagFilter: '',
  currentSort: 'favorite_first', // 'favorite_first' | 'installed_first' | 'name_asc' | 'division'
  searchQuery: '',
  targetType: 'antigravity_project',
  projectPath: '',
  customPath: '',
  
  // 視窗與彈窗狀態
  activeModalAgent: null,
  activeModalTab: 'overview',
  ruleStatus: { is_installed: false, file_path: '', content: '' }
};

// 預設專家推薦組合包 (Preset Packs)
const PRESET_PACKS = [
  {
    id: 'pack-fullstack',
    name: '🚀 極速全端開發組 (Full-Stack Squad)',
    desc: '涵蓋現代前端、後端 API、Python 系統工程、代碼審查與自動化測試專家。',
    emoji: '💻',
    tags: ['Engineering', 'Frontend', 'Backend', 'QA'],
    agentIds: [
      'engineering-frontend-developer',
      'engineering-backend-architect',
      'engineering-python-engineer',
      'engineering-code-reviewer',
      'testing-automation-engineer'
    ]
  },
  {
    id: 'pack-security',
    name: '🛡️ DevSecOps 與資安防禦組 (Security & Audit Squad)',
    desc: '程式碼安全審計、滲透測試、雲端合規、漏洞修復與 DevOps 自動化專家。',
    emoji: '🛡️',
    tags: ['Security', 'DevOps', 'Cloud', 'Audit'],
    agentIds: [
      'security-code-security-auditor',
      'security-penetration-tester',
      'security-cloud-security-architect',
      'engineering-devops-engineer'
    ]
  },
  {
    id: 'pack-ui-ux',
    name: '🎨 UI/UX 產品體驗研究組 (Design & Product Squad)',
    desc: '使用者行為研究、視覺系統與微互動、無障礙體驗與敏捷產品經理。',
    emoji: '🎨',
    tags: ['Design', 'UI/UX', 'Product', 'Accessibility'],
    agentIds: [
      'design-ui-designer',
      'design-ux-researcher',
      'design-ux-architect',
      'product-product-manager'
    ]
  },
  {
    id: 'pack-marketing-growth',
    name: '📈 增長黑客與數位行銷組 (Growth & Marketing Squad)',
    desc: 'SEO 關鍵字優化、內容行銷策略、社群推廣與付費媒體 ROAS 投放專家。',
    emoji: '📈',
    tags: ['Marketing', 'SEO', 'Paid Media', 'Growth'],
    agentIds: [
      'marketing-seo-specialist',
      'marketing-content-marketer',
      'marketing-growth-hacker',
      'paid-media-google-ads-specialist'
    ]
  }
];

// ==========================================================================
// 應用程式初始化 (App Initialization)
// ==========================================================================
document.addEventListener('DOMContentLoaded', async () => {
  // 載入偏好主題
  const savedTheme = localStorage.getItem('agency_theme_pref') || 'dark';
  if (savedTheme === 'light') {
    document.documentElement.classList.remove('dark');
    const icon = document.getElementById('theme-icon');
    if (icon) icon.setAttribute('data-lucide', 'moon');
  }

  // 初始化鍵盤快捷鍵
  setupKeyboardShortcuts();

  // 載入基礎資料
  await Promise.all([loadDivisions(), loadDestinations()]);
  await loadAgents();
  await checkRuleStatus();
  renderPresetPacks();
  lucide.createIcons();

  // 啟動 3 秒後非同步在背景檢查雲端更新 (雙向同步最新規範與專家庫)
  setTimeout(() => {
    silentSyncCheck();
  }, 3000);
});

// ==========================================================================
// 資料載入 API (Data Loading)
// ==========================================================================

// 載入部門資料
async function loadDivisions() {
  try {
    const res = await fetch('/api/divisions');
    const data = await res.json();
    if (data.success) {
      state.divisions = data.divisions;
      renderDivisions(data.divisions, data.total_agents);
    }
  } catch (err) {
    showToast('載入部門資料失敗', 'error');
  }
}

// 載入目標路徑
async function loadDestinations() {
  try {
    const params = new URLSearchParams();
    if (state.projectPath) {
      params.append('project_path', state.projectPath);
    }
    const res = await fetch(`/api/destinations?${params.toString()}`);
    const data = await res.json();
    if (data.success) {
      state.destinations = data.destinations;
      const projDest = data.destinations.find(d => d.id === 'antigravity_project');
      if (projDest && !state.projectPath) {
        state.projectPath = projDest.project_root;
        const inputEl = document.getElementById('input-project-path');
        if (inputEl) inputEl.value = state.projectPath;
        addRecentProject(state.projectPath);
      }
      updateDestPathHint();
      updateProjectNameDisplay();
    }
  } catch (err) {
    console.error('載入目標路徑失敗', err);
  }
}

// 載入專家清單並進行客戶端多維度處理
async function loadAgents() {
  try {
    const params = new URLSearchParams({
      query: '',
      division: 'all',
      target_type: state.targetType,
      filter_status: 'all'
    });

    if (state.projectPath) {
      params.append('project_path', state.projectPath);
    }
    if (state.targetType === 'custom' && state.customPath) {
      params.append('custom_path', state.customPath);
    }

    const res = await fetch(`/api/agents?${params.toString()}`);
    const data = await res.json();

    if (data.success) {
      state.agents = data.agents;
      
      // 更新統計數字
      const totalCount = data.total;
      const installedCount = data.installed_count;

      const totalBadge = document.getElementById('total-count-badge');
      if (totalBadge) totalBadge.textContent = totalCount;

      const installedBadge = document.getElementById('installed-count-badge');
      if (installedBadge) installedBadge.textContent = installedCount;

      const divAll = document.getElementById('div-count-all');
      if (divAll) divAll.textContent = totalCount;
      
      const pillAll = document.getElementById('pill-count-all');
      if (pillAll) pillAll.textContent = state.agents.length;
      
      const pillInst = document.getElementById('pill-count-installed');
      if (pillInst) pillInst.textContent = state.agents.filter(a => a.is_installed).length;
      
      const pillFav = document.getElementById('pill-count-favorites');
      if (pillFav) pillFav.textContent = state.agents.filter(a => state.favorites.has(a.id)).length;

      applyFilterAndRender();
      updateSelectedUI();
    }
  } catch (err) {
    showToast('載入專家清單失敗', 'error');
  }
}

// ==========================================================================
// 篩選、搜尋與排序核心管道 (Filter, Search & Sort Pipeline)
// ==========================================================================
function applyFilterAndRender() {
  let list = [...state.agents];

  // 1. 部門過濾
  if (state.currentDivision !== 'all') {
    list = list.filter(a => a.division_id === state.currentDivision);
  }

  // 2. 狀態分段控制器過濾 (All / Installed / Favorites)
  if (state.currentStatusFilter === 'installed') {
    list = list.filter(a => a.is_installed);
  } else if (state.currentStatusFilter === 'favorites') {
    list = list.filter(a => state.favorites.has(a.id));
  }

  // 3. 熱門領域標籤晶片過濾
  if (state.currentTagFilter) {
    const tag = state.currentTagFilter.toLowerCase();
    list = list.filter(a => {
      const matchDivision = a.division_id.toLowerCase().includes(tag) || (a.division_name_en && a.division_name_en.toLowerCase().includes(tag));
      const matchTags = a.tags && a.tags.some(t => t.toLowerCase().includes(tag));
      const matchName = a.name_en.toLowerCase().includes(tag) || a.name_zh.includes(tag);
      return matchDivision || matchTags || matchName;
    });
  }

  // 4. 關鍵字搜尋 (中英文雙向匹配)
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(a => {
      return (
        (a.name_zh && a.name_zh.toLowerCase().includes(q)) ||
        (a.name_en && a.name_en.toLowerCase().includes(q)) ||
        (a.id && a.id.toLowerCase().includes(q)) ||
        (a.description && a.description.toLowerCase().includes(q)) ||
        (a.vibe && a.vibe.toLowerCase().includes(q)) ||
        (a.division_name_zh && a.division_name_zh.toLowerCase().includes(q)) ||
        (a.tags && a.tags.some(t => t.toLowerCase().includes(q)))
      );
    });
  }

  // 5. 多維度排序
  if (state.currentSort === 'favorite_first') {
    list.sort((a, b) => {
      const aFav = state.favorites.has(a.id) ? 1 : 0;
      const bFav = state.favorites.has(b.id) ? 1 : 0;
      if (aFav !== bFav) return bFav - aFav;
      const aInst = a.is_installed ? 1 : 0;
      const bInst = b.is_installed ? 1 : 0;
      if (aInst !== bInst) return bInst - aInst;
      return a.name_zh.localeCompare(b.name_zh, 'zh-TW');
    });
  } else if (state.currentSort === 'installed_first') {
    list.sort((a, b) => {
      const aInst = a.is_installed ? 1 : 0;
      const bInst = b.is_installed ? 1 : 0;
      if (aInst !== bInst) return bInst - aInst;
      return a.name_zh.localeCompare(b.name_zh, 'zh-TW');
    });
  } else if (state.currentSort === 'name_asc') {
    list.sort((a, b) => a.name_zh.localeCompare(b.name_zh, 'zh-TW'));
  } else if (state.currentSort === 'division') {
    list.sort((a, b) => a.division_id.localeCompare(b.division_id) || a.name_zh.localeCompare(b.name_zh, 'zh-TW'));
  }

  // 更新結果計數
  const filterCountBadge = document.getElementById('filtered-count-badge');
  if (filterCountBadge) filterCountBadge.textContent = list.length;

  renderAgentsGrid(list);
}

// 關鍵字高亮工具函式
function highlightText(text, query) {
  if (!text) return '';
  if (!query) return escapeHtml(text);
  const escaped = escapeHtml(text);
  const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
  return escaped.replace(regex, '<mark class="search-highlight">$1</mark>');
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[m]));
}

function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ==========================================================================
// 渲染視圖 (Render Functions)
// ==========================================================================

// 渲染部門選單
function renderDivisions(divisions, totalAgents) {
  const container = document.getElementById('divisions-list');
  const allBtn = document.getElementById('div-btn-all');
  
  container.innerHTML = '';
  container.appendChild(allBtn);

  divisions.forEach(div => {
    const btn = document.createElement('button');
    btn.onclick = () => selectDivision(div.id);
    btn.id = `div-btn-${div.id}`;
    btn.className = `div-tab w-full flex items-center justify-between px-2.5 py-1.5 text-xs font-medium transition ${state.currentDivision === div.id ? 'active-div-tab' : ''}`;
    
    btn.innerHTML = `
      <span class="flex items-center gap-2 truncate pr-1">
        <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" style="background-color: ${div.color}"></span>
        <span class="truncate">${div.name_zh}</span>
      </span>
      <span class="px-1.5 py-0.2 rounded-full bg-white/[0.06] text-[10px] text-zinc-400 font-mono">${div.count}</span>
    `;
    container.appendChild(btn);
  });
}

// 渲染極簡、通透且防截斷的專家卡片網格 (Minimalist Agent Card Grid)
function renderAgentsGrid(agents) {
  const grid = document.getElementById('agents-grid');
  const empty = document.getElementById('empty-state');

  grid.innerHTML = '';

  if (!agents || agents.length === 0) {
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');

  agents.forEach(agent => {
    const isSelected = state.selectedIds.has(agent.id);
    const isFav = state.favorites.has(agent.id);
    const card = document.createElement('div');
    
    card.className = `agent-card group ${isSelected ? 'selected' : ''}`;
    card.setAttribute('data-agent-id', agent.id);

    // 操作按鈕
    const actionBtn = agent.is_installed
      ? `<button onclick="event.stopPropagation(); uninstallSingleAgent('${agent.id}')" class="px-2.5 py-1 rounded-lg bg-rose-600/10 hover:bg-rose-600/20 text-rose-300 border border-rose-600/20 text-xs font-medium transition flex items-center gap-1">
           <i data-lucide="trash-2" class="w-3 h-3"></i>
           <span>卸載</span>
         </button>`
      : `<button onclick="event.stopPropagation(); installSingleAgent('${agent.id}')" class="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm flex items-center gap-1">
           <i data-lucide="download" class="w-3 h-3"></i>
           <span>安裝</span>
         </button>`;

    // 標籤 Chips
    const tagsHtml = (agent.tags || []).slice(0, 3).map(tag => 
      `<span onclick="event.stopPropagation(); setTagFilter('${tag}')" class="px-2 py-0.5 rounded-md bg-white/[0.03] hover:bg-white/[0.08] hover:text-zinc-200 border border-white/[0.05] text-[10px] text-zinc-400 font-medium cursor-pointer transition">#${tag}</span>`
    ).join('');

    card.innerHTML = `
      <div class="p-4 sm:p-5 flex flex-col gap-3 flex-1 min-w-0">
        
        <!-- 卡片頂部：選取 Checkbox + Emoji + 名稱 (彈性換行防截斷) + 收藏星標 -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-start gap-2.5 min-w-0 flex-1">
            <input 
              type="checkbox" 
              ${isSelected ? 'checked' : ''} 
              onchange="event.stopPropagation(); toggleSelectAgent('${agent.id}', this.checked)"
              class="rounded bg-zinc-900 border-zinc-700 text-indigo-500 focus:ring-0 w-3.5 h-3.5 mt-1 cursor-pointer flex-shrink-0"
            >
            <div class="w-9 h-9 rounded-xl bg-zinc-800/80 border border-white/[0.06] flex items-center justify-center text-xl flex-shrink-0">
              ${agent.emoji || '🤖'}
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 flex-wrap">
                <h3 class="font-semibold text-sm text-zinc-100 group-hover:text-indigo-300 transition break-words">
                  ${highlightText(agent.name_zh, state.searchQuery)}
                </h3>
                ${agent.is_installed ? '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" title="已安裝"></span>' : ''}
              </div>
              <!-- 英文 Slug：加入 break-all 防截斷 -->
              <p class="agent-slug mt-0.5 break-all select-all">@${highlightText(agent.id, state.searchQuery)}</p>
            </div>
          </div>

          <!-- 星標收藏按鈕 -->
          <button 
            onclick="event.stopPropagation(); toggleFavorite('${agent.id}', this)" 
            class="p-1 rounded-lg text-zinc-500 hover:text-amber-400 hover:bg-zinc-800/50 transition flex-shrink-0"
            title="${isFav ? '移除收藏' : '加入常用收藏'}"
          >
            <i data-lucide="star" class="w-4 h-4 ${isFav ? 'text-amber-400 fill-amber-400' : ''}"></i>
          </button>
        </div>

        <!-- 職責描述 (保持清爽排版) -->
        <p class="text-xs text-zinc-400 leading-relaxed line-clamp-2 min-w-0">
          ${highlightText(agent.description || '無描述', state.searchQuery)}
        </p>

        <!-- 標籤 Chips -->
        ${tagsHtml ? `<div class="flex flex-wrap gap-1 pt-0.5">${tagsHtml}</div>` : ''}

      </div>

      <!-- 底部動作工具列 -->
      <div class="px-4 py-2.5 border-t border-white/[0.04] flex items-center justify-between gap-2 bg-zinc-950/30">
        <button 
          onclick="openDetailModal('${agent.id}')" 
          class="text-xs text-zinc-400 hover:text-zinc-200 flex items-center gap-1 transition font-medium"
        >
          <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
          <span>詳情</span>
        </button>

        <div class="flex items-center gap-1.5">
          <button 
            onclick="event.stopPropagation(); copyAgentCallCommand('${agent.id}', this)" 
            class="text-[11px] font-mono text-zinc-400 hover:text-indigo-300 px-2 py-1 rounded bg-zinc-900 border border-white/[0.06] hover:border-white/[0.12] transition"
            title="複製 @${agent.id}"
          >
            複製 @
          </button>
          ${actionBtn}
        </div>
      </div>
    `;

    grid.appendChild(card);
  });

  lucide.createIcons();
}

// ==========================================================================
// 互動操作事件 (Interactions & Event Handlers)
// ==========================================================================

// 部門切換
function selectDivision(divId) {
  state.currentDivision = divId;
  document.querySelectorAll('.div-tab').forEach(el => el.classList.remove('active-div-tab'));
  const activeBtn = document.getElementById(`div-btn-${divId}`);
  if (activeBtn) activeBtn.classList.add('active-div-tab');
  applyFilterAndRender();
}

// 狀態分段控制器切換
function setStatusFilter(status) {
  state.currentStatusFilter = status;
  document.querySelectorAll('.segmented-item').forEach(el => el.classList.remove('active'));
  const activeBtn = document.getElementById(`status-filter-${status}`);
  if (activeBtn) activeBtn.classList.add('active');
  applyFilterAndRender();
}

// 標籤過濾切換
function setTagFilter(tag) {
  state.currentTagFilter = tag;
  document.querySelectorAll('.tag-chip').forEach(el => el.classList.remove('active-tag-chip'));
  const activeBtn = document.getElementById(`tag-chip-${tag || 'all'}`);
  if (activeBtn) activeBtn.classList.add('active-tag-chip');
  applyFilterAndRender();
}

// 排序切換
function onSortChange(sortVal) {
  state.currentSort = sortVal;
  applyFilterAndRender();
}

// 搜尋防抖
let searchTimeout = null;
function debounceSearch() {
  clearTimeout(searchTimeout);
  const input = document.getElementById('search-input');
  const clearBtn = document.getElementById('btn-clear-search');
  
  if (input.value.trim()) {
    clearBtn.classList.remove('hidden');
  } else {
    clearBtn.classList.add('hidden');
  }

  searchTimeout = setTimeout(() => {
    state.searchQuery = input.value.trim();
    applyFilterAndRender();
  }, 150);
}

function clearSearch() {
  const input = document.getElementById('search-input');
  input.value = '';
  document.getElementById('btn-clear-search').classList.add('hidden');
  state.searchQuery = '';
  applyFilterAndRender();
  input.focus();
}

function resetAllFilters() {
  state.currentDivision = 'all';
  state.currentStatusFilter = 'all';
  state.currentTagFilter = '';
  state.searchQuery = '';
  state.currentSort = 'favorite_first';

  document.getElementById('search-input').value = '';
  document.getElementById('btn-clear-search').classList.add('hidden');
  document.getElementById('sort-select').value = 'favorite_first';

  document.querySelectorAll('.div-tab').forEach(el => el.classList.remove('active-div-tab'));
  const divAll = document.getElementById('div-btn-all');
  if (divAll) divAll.classList.add('active-div-tab');

  document.querySelectorAll('.segmented-item').forEach(el => el.classList.remove('active'));
  const statusAll = document.getElementById('status-filter-all');
  if (statusAll) statusAll.classList.add('active');

  document.querySelectorAll('.tag-chip').forEach(el => el.classList.remove('active-tag-chip'));
  const tagAll = document.getElementById('tag-chip-all');
  if (tagAll) tagAll.classList.add('active-tag-chip');

  applyFilterAndRender();
  showToast('已重設所有篩選條件', 'info');
}

// 收藏星標切換
function toggleFavorite(agentId, btnEl) {
  if (state.favorites.has(agentId)) {
    state.favorites.delete(agentId);
    showToast('已從我的收藏移除', 'info');
  } else {
    state.favorites.add(agentId);
    showToast('已加入我的收藏 ⭐', 'success');
  }
  localStorage.setItem('agency_favorites_v1', JSON.stringify(Array.from(state.favorites)));
  
  if (btnEl) {
    btnEl.classList.add('star-popping');
    setTimeout(() => btnEl.classList.remove('star-popping'), 300);
  }

  document.getElementById('favorites-count-badge').textContent = state.favorites.size;
  const pillFav = document.getElementById('pill-count-favorites');
  if (pillFav) pillFav.textContent = state.agents.filter(a => state.favorites.has(a.id)).length;

  applyFilterAndRender();
}

// 快速複製 @指令
async function copyAgentCallCommand(agentId, btnEl) {
  const cmd = `@${agentId}`;
  try {
    await navigator.clipboard.writeText(cmd);
    showToast(`已複製指令：${cmd}`, 'success');
    if (btnEl) {
      const originalHtml = btnEl.innerHTML;
      btnEl.innerHTML = `<i data-lucide="check" class="w-3 h-3 text-emerald-400"></i>`;
      lucide.createIcons();
      setTimeout(() => {
        btnEl.innerHTML = originalHtml;
        lucide.createIcons();
      }, 1500);
    }
  } catch (err) {
    showToast('複製指令失敗', 'error');
  }
}

// ==========================================================================
// 專案切換與 MRU 歷史 (Project Management & MRU)
// ==========================================================================
function updateProjectNameDisplay() {
  const nameEl = document.getElementById('current-project-name');
  if (!nameEl) return;
  if (!state.projectPath) {
    nameEl.textContent = '(未設定專案)';
    return;
  }
  const folderName = state.projectPath.split(/[\\/]/).filter(Boolean).pop() || state.projectPath;
  nameEl.textContent = folderName;
}

function addRecentProject(projPath) {
  if (!projPath) return;
  const folderName = projPath.split(/[\\/]/).filter(Boolean).pop() || projPath;
  let list = state.recentProjects.filter(p => p.path !== projPath);
  list.unshift({
    path: projPath,
    name: folderName,
    lastAccessed: Date.now()
  });
  list = list.slice(0, 8);
  state.recentProjects = list;
  localStorage.setItem('agency_recent_projects_v1', JSON.stringify(list));
  renderRecentProjects();
}

function renderRecentProjects() {
  const listEl = document.getElementById('recent-projects-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  if (state.recentProjects.length === 0) {
    listEl.innerHTML = `<div class="p-2 text-xs text-zinc-500 text-center">尚無專案歷史紀錄</div>`;
    return;
  }

  state.recentProjects.forEach(proj => {
    const isCurrent = proj.path === state.projectPath;
    const btn = document.createElement('button');
    btn.className = `w-full text-left p-2 rounded-lg text-xs transition flex items-center justify-between gap-2 ${isCurrent ? 'bg-indigo-600/15 text-indigo-300 font-semibold' : 'hover:bg-zinc-800 text-zinc-300'}`;
    btn.onclick = () => selectRecentProject(proj.path);
    btn.innerHTML = `
      <div class="truncate flex items-center gap-1.5">
        <i data-lucide="folder" class="w-3.5 h-3.5 text-zinc-500 flex-shrink-0"></i>
        <span class="truncate">${proj.name}</span>
      </div>
      ${isCurrent ? '<span class="text-[10px] text-indigo-400 flex-shrink-0 font-mono font-bold">目前</span>' : ''}
    `;
    listEl.appendChild(btn);
  });
  lucide.createIcons();
}

function toggleProjectDropdown() {
  const menu = document.getElementById('project-dropdown-menu');
  if (menu) {
    menu.classList.toggle('hidden');
    renderRecentProjects();
  }
}

document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('project-picker-wrapper');
  const menu = document.getElementById('project-dropdown-menu');
  if (wrapper && menu && !wrapper.contains(e.target)) {
    menu.classList.add('hidden');
  }
});

function selectRecentProject(projPath) {
  state.projectPath = projPath;
  document.getElementById('input-project-path').value = projPath;
  toggleProjectDropdown();
  updateDestPathHint();
  updateProjectNameDisplay();
  addRecentProject(projPath);
  loadAgents();
  checkRuleStatus();
  showToast(`已切換至專案：${projPath}`, 'info');
}

// 瀏覽選擇專案資料夾
async function browseProjectFolder() {
  try {
    const res = await fetch('/api/browse-folder');
    const data = await res.json();
    if (data.success && data.path) {
      state.projectPath = data.path;
      document.getElementById('input-project-path').value = data.path;
      addRecentProject(data.path);
      updateDestPathHint();
      updateProjectNameDisplay();
      await loadAgents();
      await checkRuleStatus();
      showToast(`已切換至專案：${data.path}`, 'success');
    }
  } catch (err) {
    showToast('開啟資料夾選擇失敗', 'error');
  }
}

// 瀏覽自訂資料夾
async function browseCustomFolder() {
  try {
    const res = await fetch('/api/browse-folder');
    const data = await res.json();
    if (data.success && data.path) {
      state.customPath = data.path;
      document.getElementById('input-custom-path').value = data.path;
      updateDestPathHint();
      loadAgents();
      checkRuleStatus();
    }
  } catch (err) {
    showToast('開啟資料夾選擇失敗', 'error');
  }
}

function onManualProjectPathChange() {
  const val = document.getElementById('input-project-path').value.trim();
  if (val) {
    state.projectPath = val;
    addRecentProject(val);
    updateDestPathHint();
    updateProjectNameDisplay();
    loadAgents();
    checkRuleStatus();
  }
}

function applyCustomPath() {
  const path = document.getElementById('input-custom-path').value.trim();
  if (!path) {
    showToast('請輸入自訂目錄路徑', 'error');
    return;
  }
  state.customPath = path;
  updateDestPathHint();
  loadAgents();
  checkRuleStatus();
}

function onDestinationChange() {
  const select = document.getElementById('select-destination');
  state.targetType = select.value;

  const projContainer = document.getElementById('project-path-container');
  const customContainer = document.getElementById('custom-path-container');

  const isProjectMode = ['antigravity_project', 'cursor', 'opencode'].includes(state.targetType);

  if (isProjectMode) {
    projContainer.classList.remove('hidden');
    projContainer.classList.add('flex');
    customContainer.classList.add('hidden');
    customContainer.classList.remove('flex');
  } else if (state.targetType === 'custom') {
    projContainer.classList.add('hidden');
    projContainer.classList.remove('flex');
    customContainer.classList.remove('hidden');
    customContainer.classList.add('flex');
  } else {
    projContainer.classList.add('hidden');
    projContainer.classList.remove('flex');
    customContainer.classList.add('hidden');
    customContainer.classList.remove('flex');
  }

  updateDestPathHint();
  loadAgents();
  checkRuleStatus();
}

function updateDestPathHint() {
  const hintEl = document.getElementById('dest-path-hint');
  const proj = state.projectPath || '(當前專案)';
  if (state.targetType === 'antigravity_project') {
    hintEl.textContent = `${proj}\\.agents\\agents\\`;
  } else if (state.targetType === 'cursor') {
    hintEl.textContent = `${proj}\\.cursor\\rules\\`;
  } else if (state.targetType === 'opencode') {
    hintEl.textContent = `${proj}\\.opencode\\agents\\`;
  } else if (state.targetType === 'custom') {
    hintEl.textContent = state.customPath || '(未設定自訂路徑)';
  } else {
    const dest = state.destinations.find(d => d.id === state.targetType);
    hintEl.textContent = dest ? dest.path : '';
  }
}

// ==========================================================================
// Subagent 協作工作流規範 (Rule) 控制模組
// ==========================================================================
async function checkRuleStatus() {
  try {
    const params = new URLSearchParams({
      target_type: state.targetType
    });
    if (state.projectPath) {
      params.append('project_path', state.projectPath);
    }
    const res = await fetch(`/api/rule/status?${params.toString()}`);
    const data = await res.json();
    if (data.success) {
      state.ruleStatus = data;
      updateRuleStatusUI(data.is_installed);
    }
  } catch (err) {
    console.error('檢查協作 Rule 失敗', err);
  }
}

function updateRuleStatusUI(isInstalled) {
  // 頂部 Indicator
  const topIndicator = document.getElementById('top-rule-indicator');
  if (topIndicator) {
    if (isInstalled) {
      topIndicator.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
    } else {
      topIndicator.className = 'w-2 h-2 rounded-full bg-zinc-500';
    }
  }

  // 側邊欄 Badge 與按鈕
  const sidebarBadge = document.getElementById('sidebar-rule-badge');
  const btnRuleAction = document.getElementById('btn-sidebar-rule-action');
  const btnRuleText = document.getElementById('btn-sidebar-rule-text');

  if (sidebarBadge && btnRuleAction && btnRuleText) {
    if (isInstalled) {
      sidebarBadge.className = 'text-[10px] text-emerald-400 font-mono font-semibold';
      sidebarBadge.textContent = '🟢 已啟用';
      btnRuleAction.className = 'flex-1 py-1 px-2.5 rounded-lg bg-rose-600/15 hover:bg-rose-600/25 text-rose-300 border border-rose-600/30 text-xs font-medium transition flex items-center justify-center gap-1';
      btnRuleText.textContent = '停用協作 Rule';
    } else {
      sidebarBadge.className = 'text-[10px] text-zinc-500 font-mono';
      sidebarBadge.textContent = '⚪ 未啟用';
      btnRuleAction.className = 'flex-1 py-1 px-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition flex items-center justify-center gap-1 shadow-sm';
      btnRuleText.textContent = '一鍵啟用 Rule';
    }
  }
}

async function toggleQuickRuleInstall() {
  if (state.ruleStatus.is_installed) {
    await uninstallCollaborationRule();
  } else {
    await installCollaborationRule();
  }
}

async function installCollaborationRule(customContent = null) {
  try {
    const res = await fetch('/api/rule/install', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_type: state.targetType,
        project_path: state.projectPath,
        custom_content: customContent,
        install_essential_agents: true
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || 'Loop Engineering 協作規範與核心子代理已配置！', 'success');
      await checkRuleStatus();
      await loadAgents();
      if (!document.getElementById('rule-modal').classList.contains('hidden')) {
        openRuleModal();
      }
    } else {
      showToast(data.message || '啟用失敗', 'error');
    }
  } catch (err) {
    showToast('連線異常，啟用失敗', 'error');
  }
}

async function uninstallCollaborationRule() {
  try {
    const res = await fetch('/api/rule/uninstall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_type: state.targetType,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || '已停用協作規範', 'info');
      await checkRuleStatus();
      if (!document.getElementById('rule-modal').classList.contains('hidden')) {
        openRuleModal();
      }
    } else {
      showToast(data.message || '停用失敗', 'error');
    }
  } catch (err) {
    showToast('連線異常，停用失敗', 'error');
  }
}

async function openRuleModal() {
  try {
    await checkRuleStatus();
    const res = await fetch(`/api/rule/preview?target_type=${state.targetType}`);
    const data = await res.json();

    const previewEl = document.getElementById('rule-preview-content');
    const pathBadge = document.getElementById('rule-file-path-badge');
    const statusEl = document.getElementById('modal-rule-status');
    const actionBtn = document.getElementById('modal-rule-action-btn');

    pathBadge.textContent = state.ruleStatus.file_path || '.agents/rules/subagent-collaboration.md';
    const content = state.ruleStatus.content || data.content;
    previewEl.innerHTML = marked.parse(content);

    if (state.ruleStatus.is_installed) {
      statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> <span class="text-emerald-300 font-medium">Loop Engineering 規範已啟用</span>`;
      actionBtn.className = 'flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-600/30 text-xs font-medium transition';
      actionBtn.innerHTML = `<i data-lucide="trash-2" class="w-3.5 h-3.5"></i> <span>移除協作 Rule</span>`;
    } else {
      statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-zinc-500"></span> <span class="text-zinc-400 font-medium">尚未安裝</span>`;
      actionBtn.className = 'flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm';
      actionBtn.innerHTML = `<i data-lucide="download" class="w-3.5 h-3.5"></i> <span>一鍵安裝協作 Rule</span>`;
    }

    document.getElementById('rule-modal').classList.remove('hidden');
    lucide.createIcons();
  } catch (err) {
    showToast('載入 Rule 預覽失敗', 'error');
  }
}

function closeRuleModal() {
  document.getElementById('rule-modal').classList.add('hidden');
}

function toggleModalRuleInstall() {
  if (state.ruleStatus.is_installed) {
    uninstallCollaborationRule();
  } else {
    installCollaborationRule();
  }
}

// ==========================================================================
// 勾選與浮動 Dock 批次操作 (Batch Management & Floating Dock)
// ==========================================================================
function toggleSelectAgent(id, checked) {
  if (checked) {
    state.selectedIds.add(id);
  } else {
    state.selectedIds.delete(id);
  }
  updateSelectedUI();
}

function toggleSelectAll(checked) {
  if (checked) {
    state.agents.forEach(a => state.selectedIds.add(a.id));
  } else {
    state.selectedIds.clear();
  }
  applyFilterAndRender();
  updateSelectedUI();
}

function updateSelectedUI() {
  const count = state.selectedIds.size;
  const dock = document.getElementById('floating-batch-dock');
  const dockCount = document.getElementById('dock-selected-count');
  
  if (dock && dockCount) {
    dockCount.textContent = count;
    if (count > 0) {
      dock.classList.add('visible');
    } else {
      dock.classList.remove('visible');
    }
  }

  // 更新卡片選取視覺
  document.querySelectorAll('.agent-card').forEach(card => {
    const aid = card.getAttribute('data-agent-id');
    if (state.selectedIds.has(aid)) {
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  });
}

// 安裝單個 Agent
async function installSingleAgent(agentId) {
  try {
    const res = await fetch('/api/install', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: agentId,
        target_type: state.targetType,
        custom_path: state.customPath,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || '安裝成功', 'success');
      await loadAgents();
      if (state.activeModalAgent && state.activeModalAgent.id === agentId) {
        openDetailModal(agentId);
      }
    } else {
      showToast(data.message || '安裝失敗', 'error');
    }
  } catch (err) {
    showToast('連線異常，安裝失敗', 'error');
  }
}

// 卸載單個 Agent
async function uninstallSingleAgent(agentId) {
  try {
    const res = await fetch('/api/uninstall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: agentId,
        target_type: state.targetType,
        custom_path: state.customPath,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || '已解除安裝', 'info');
      await loadAgents();
      if (state.activeModalAgent && state.activeModalAgent.id === agentId) {
        openDetailModal(agentId);
      }
    } else {
      showToast(data.message || '卸載失敗', 'error');
    }
  } catch (err) {
    showToast('連線異常，卸載失敗', 'error');
  }
}

// 批次安裝
async function installSelected() {
  const ids = Array.from(state.selectedIds);
  if (ids.length === 0) return;

  showToast(`正在安裝選取的 ${ids.length} 位專家...`, 'info');
  try {
    const res = await fetch('/api/install-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_ids: ids,
        target_type: state.targetType,
        custom_path: state.customPath,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    showToast(data.message, data.success ? 'success' : 'warning');
    state.selectedIds.clear();
    await loadAgents();
  } catch (err) {
    showToast('批次安裝發生錯誤', 'error');
  }
}

// 批次卸載
async function uninstallSelected() {
  const ids = Array.from(state.selectedIds);
  if (ids.length === 0) return;

  if (!confirm(`確定要卸載已選取的 ${ids.length} 位 Subagent 嗎？`)) return;

  try {
    const res = await fetch('/api/uninstall-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_ids: ids,
        target_type: state.targetType,
        custom_path: state.customPath,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    showToast(data.message, data.success ? 'success' : 'warning');
    state.selectedIds.clear();
    await loadAgents();
  } catch (err) {
    showToast('批次卸載發生錯誤', 'error');
  }
}

// ==========================================================================
// 專家詳情 Modal 邏輯 (3-Tab Detail Modal)
// ==========================================================================
async function openDetailModal(agentId) {
  try {
    const params = new URLSearchParams({
      target_type: state.targetType
    });
    if (state.projectPath) {
      params.append('project_path', state.projectPath);
    }
    if (state.targetType === 'custom' && state.customPath) {
      params.append('custom_path', state.customPath);
    }

    const res = await fetch(`/api/agents/${agentId}?${params.toString()}`);
    const data = await res.json();
    if (!data.success) return;

    const agent = data.agent;
    state.activeModalAgent = agent;

    document.getElementById('modal-emoji').textContent = agent.emoji || '🤖';
    document.getElementById('modal-name-zh').textContent = agent.name_zh;
    document.getElementById('modal-name-en').textContent = agent.id;
    document.getElementById('modal-division-badge').textContent = agent.division_name_zh;
    document.getElementById('modal-vibe').textContent = agent.vibe || '無特殊 Vibe 設定';
    document.getElementById('modal-description').textContent = agent.description || '無描述';
    
    // 渲染標籤
    const tagsContainer = document.getElementById('modal-tags-container');
    tagsContainer.innerHTML = (agent.tags || []).map(t => 
      `<span class="px-2.5 py-0.5 rounded-lg bg-zinc-900 border border-white/[0.06] text-xs text-indigo-300 font-medium">#${t}</span>`
    ).join('') || '<span class="text-xs text-zinc-500">無標籤</span>';

    // Markdown 渲染
    const mdBody = agent.body_markdown || agent.raw_markdown || '';
    document.getElementById('modal-markdown-content').innerHTML = marked.parse(mdBody);

    // 呼叫範例程式碼更新
    document.getElementById('usage-code-agy').textContent = `@${agent.id} 請協助分析並完成此任務，完成後請進行嚴格測試驗證。`;
    document.getElementById('usage-code-claude').textContent = `/subagent ${agent.id} Please implement this requirement with rigorous tests.`;

    // 收藏星標按鈕狀態
    const favBtn = document.getElementById('modal-favorite-btn');
    const isFav = state.favorites.has(agent.id);
    favBtn.innerHTML = `<i data-lucide="star" class="w-4 h-4 ${isFav ? 'text-amber-400 fill-amber-400' : 'text-zinc-400'}"></i>`;

    // 狀態與動作按鈕
    const statusEl = document.getElementById('modal-status-badge');
    const actionBtn = document.getElementById('modal-action-btn');

    if (agent.is_installed) {
      statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> <span class="text-emerald-300 font-medium">已安裝為 Subagent</span>`;
      actionBtn.className = 'flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-rose-600/15 hover:bg-rose-600/25 text-rose-300 border border-rose-600/25 text-xs font-medium transition';
      actionBtn.innerHTML = `<i data-lucide="trash-2" class="w-3.5 h-3.5"></i> <span>解除安裝</span>`;
    } else {
      statusEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-zinc-500"></span> <span class="text-zinc-400 font-medium">尚未安裝</span>`;
      actionBtn.className = 'flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm';
      actionBtn.innerHTML = `<i data-lucide="download" class="w-3.5 h-3.5"></i> <span>一鍵安裝</span>`;
    }

    switchModalTab('overview');
    document.getElementById('detail-modal').classList.remove('hidden');
    lucide.createIcons();
  } catch (err) {
    showToast('無法取得專家詳細資料', 'error');
  }
}

function closeDetailModal() {
  document.getElementById('detail-modal').classList.add('hidden');
  state.activeModalAgent = null;
}

function switchModalTab(tabKey) {
  state.activeModalTab = tabKey;
  ['overview', 'prompt', 'usage'].forEach(key => {
    const tabBtn = document.getElementById(`modal-tab-${key}`);
    const content = document.getElementById(`tab-content-${key}`);
    if (key === tabKey) {
      tabBtn.classList.add('active-modal-tab');
      content.classList.remove('hidden');
    } else {
      tabBtn.classList.remove('active-modal-tab');
      content.classList.add('hidden');
    }
  });
}

function toggleModalFavorite() {
  if (!state.activeModalAgent) return;
  toggleFavorite(state.activeModalAgent.id);
  const favBtn = document.getElementById('modal-favorite-btn');
  const isFav = state.favorites.has(state.activeModalAgent.id);
  favBtn.innerHTML = `<i data-lucide="star" class="w-4 h-4 ${isFav ? 'text-amber-400 fill-amber-400' : 'text-zinc-400'}"></i>`;
  lucide.createIcons();
}

function toggleModalAgentInstall() {
  if (!state.activeModalAgent) return;
  if (state.activeModalAgent.is_installed) {
    uninstallSingleAgent(state.activeModalAgent.id);
  } else {
    installSingleAgent(state.activeModalAgent.id);
  }
}

function copyCurrentModalSlug() {
  if (!state.activeModalAgent) return;
  copyAgentCallCommand(state.activeModalAgent.id);
}

async function copyFullPrompt() {
  if (!state.activeModalAgent) return;
  const promptText = state.activeModalAgent.body_markdown || state.activeModalAgent.raw_markdown || '';
  try {
    await navigator.clipboard.writeText(promptText);
    showToast('已複製完整系統提示詞！', 'success');
  } catch (err) {
    showToast('複製提示詞失敗', 'error');
  }
}

async function copyUsageSnippet(elemId) {
  const el = document.getElementById(elemId);
  if (!el) return;
  try {
    await navigator.clipboard.writeText(el.textContent.trim());
    showToast('已複製呼叫指令！', 'success');
  } catch (err) {
    showToast('複製失敗', 'error');
  }
}

// ==========================================================================
// 推薦專家組合包 (Preset Packs Modal)
// ==========================================================================
function renderPresetPacks() {
  const container = document.getElementById('preset-packs-container');
  if (!container) return;
  container.innerHTML = '';

  PRESET_PACKS.forEach(pack => {
    const card = document.createElement('div');
    card.className = 'p-4 rounded-xl bg-zinc-950 border border-white/[0.06] flex flex-col justify-between gap-3 shadow-sm';
    
    const tagsHtml = pack.tags.map(t => 
      `<span class="px-2 py-0.5 rounded-md bg-indigo-950/40 text-indigo-300 border border-indigo-900/40 text-[10px] font-semibold">#${t}</span>`
    ).join(' ');

    const agentListPreview = pack.agentIds.map(aid => 
      `<span class="font-mono text-zinc-300 bg-zinc-900 px-2 py-0.5 rounded border border-white/[0.04] text-[11px]">${aid}</span>`
    ).join(' ');

    card.innerHTML = `
      <div class="flex flex-col gap-2">
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl">${pack.emoji}</span>
            <div>
              <h3 class="font-semibold text-sm text-white">${pack.name}</h3>
              <div class="flex gap-1 mt-0.5">${tagsHtml}</div>
            </div>
          </div>
          <span class="text-xs font-mono text-indigo-400 font-bold px-2 py-0.5 rounded-full bg-zinc-900 border border-white/[0.06]">
            ${pack.agentIds.length} 位專家
          </span>
        </div>
        <p class="text-xs text-zinc-400 leading-relaxed">${pack.desc}</p>
        <div class="flex flex-wrap gap-1.5 pt-1">${agentListPreview}</div>
      </div>

      <div class="pt-3 border-t border-white/[0.04] flex items-center justify-end">
        <button onclick="installPresetPack('${pack.id}')" class="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-sm">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>一鍵安裝此組合</span>
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function openPresetModal() {
  renderPresetPacks();
  document.getElementById('preset-modal').classList.remove('hidden');
  lucide.createIcons();
}

function closePresetModal() {
  document.getElementById('preset-modal').classList.add('hidden');
}

async function installPresetPack(packId) {
  const pack = PRESET_PACKS.find(p => p.id === packId);
  if (!pack) return;

  showToast(`正在安裝【${pack.name}】...`, 'info');
  try {
    const res = await fetch('/api/install-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_ids: pack.agentIds,
        target_type: state.targetType,
        custom_path: state.customPath,
        project_path: state.projectPath
      })
    });
    const data = await res.json();
    showToast(data.message || '組合套裝安裝完成！', 'success');
    closePresetModal();
    await loadAgents();
  } catch (err) {
    showToast('安裝組合套裝失敗', 'error');
  }
}

// ==========================================================================
// 專案配置匯出 / 匯入 (Bundle Modal)
// ==========================================================================
function openBundleModal() {
  document.getElementById('bundle-modal').classList.remove('hidden');
}

function closeBundleModal() {
  document.getElementById('bundle-modal').classList.add('hidden');
}

function exportProjectBundle() {
  const installedAgents = state.agents.filter(a => a.is_installed);
  if (installedAgents.length === 0) {
    showToast('目前專案尚未安裝任何 Subagent，無法匯出', 'warning');
    return;
  }

  const folderName = (state.projectPath ? state.projectPath.split(/[\\/]/).filter(Boolean).pop() : 'project') || 'project';
  const bundleData = {
    appName: "Agency Subagents Manager",
    version: "2.0.0",
    projectName: folderName,
    exportedAt: new Date().toISOString(),
    totalCount: installedAgents.length,
    installedAgentIds: installedAgents.map(a => a.id)
  };

  const blob = new Blob([JSON.stringify(bundleData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${folderName}-subagents-bundle.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast(`已匯出 ${installedAgents.length} 位 Subagent 設定檔！`, 'success');
}

function handleBundleFileImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const data = JSON.parse(e.target.result);
      const agentIds = data.installedAgentIds || [];
      if (!Array.isArray(agentIds) || agentIds.length === 0) {
        showToast('設定檔中無有效的 Subagent 清單', 'error');
        return;
      }

      showToast(`正在匯入並批次安裝 ${agentIds.length} 位專家...`, 'info');
      const res = await fetch('/api/install-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_ids: agentIds,
          target_type: state.targetType,
          custom_path: state.customPath,
          project_path: state.projectPath
        })
      });
      const resData = await res.json();
      showToast(resData.message || '匯入安裝完成！', 'success');
      closeBundleModal();
      await loadAgents();
    } catch (err) {
      showToast('解析 JSON 設定檔失敗', 'error');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ==========================================================================
// 新手教學與指南 (Guide Modal)
// ==========================================================================
function openGuideModal() {
  document.getElementById('guide-modal').classList.remove('hidden');
}

function closeGuideModal() {
  document.getElementById('guide-modal').classList.add('hidden');
}

// ==========================================================================
// 雙向雲端同步 (Dual-Source Cloud Sync)
// 1. 協作規範與翻譯：自使用者 GitHub 倉庫 (zhanallen/agency-subagents-manager) 更新
// 2. 專家內容與提示詞：自原作者 GitHub 倉庫 (msitarzewski/agency-agents) 更新
// ==========================================================================
async function syncGithub() {
  const btn = document.getElementById('btn-sync-github');
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i>`;
  lucide.createIcons();

  showToast('正在執行雲端雙向同步 (規範/翻譯: 您的倉庫 · 專家庫: 原作者倉庫)...', 'info');

  try {
    const res = await fetch('/api/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_repo: 'zhanallen/agency-subagents-manager',
        author_repo_url: 'https://github.com/msitarzewski/agency-agents.git',
        update_project_rule: true,
        project_path: state.projectPath,
        target_type: state.targetType
      })
    });
    const data = await res.json();
    if (data.success) {
      if (data.rule_updated_in_project) {
        showToast('✅ 雙向同步完成！當前專案的協作規範已自動升級為最新版！', 'success');
      } else {
        showToast(data.message || '✅ 雲端雙向同步完成！', 'success');
      }
      await loadDivisions();
      await loadAgents();
      await checkRuleStatus();
    } else {
      showToast(data.message || '同步過程中發生問題', 'warning');
    }
  } catch (err) {
    showToast('同步連線失敗，已自動使用本機離線快取資料', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="refresh-cw" class="w-4 h-4"></i>`;
    lucide.createIcons();
  }
}

// 背景靜默更新檢查
async function silentSyncCheck() {
  try {
    const res = await fetch('/api/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_repo: 'zhanallen/agency-subagents-manager',
        author_repo_url: 'https://github.com/msitarzewski/agency-agents.git',
        update_project_rule: false
      })
    });
    const data = await res.json();
    if (data.success) {
      console.log('背景雲端同步完成', data);
      // 若拉取到新資料則無干擾刷新清單
      await loadDivisions();
      await loadAgents();
    }
  } catch (e) {
    console.log('背景檢查更新跳過 (離線或網路不通)');
  }
}

// ==========================================================================
// 全域鍵盤快捷鍵系統 (Keyboard Shortcuts)
// ==========================================================================
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl + K 或 Cmd + K: 聚焦搜尋框
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const input = document.getElementById('search-input');
      if (input) {
        input.focus();
        input.select();
      }
      return;
    }

    // ESC: 關閉彈窗或清除搜尋
    if (e.key === 'Escape') {
      const detailModal = document.getElementById('detail-modal');
      const ruleModal = document.getElementById('rule-modal');
      const presetModal = document.getElementById('preset-modal');
      const bundleModal = document.getElementById('bundle-modal');
      const guideModal = document.getElementById('guide-modal');

      if (detailModal && !detailModal.classList.contains('hidden')) {
        closeDetailModal();
      } else if (ruleModal && !ruleModal.classList.contains('hidden')) {
        closeRuleModal();
      } else if (presetModal && !presetModal.classList.contains('hidden')) {
        closePresetModal();
      } else if (bundleModal && !bundleModal.classList.contains('hidden')) {
        closeBundleModal();
      } else if (guideModal && !guideModal.classList.contains('hidden')) {
        closeGuideModal();
      } else {
        const input = document.getElementById('search-input');
        if (input && input.value) {
          clearSearch();
        }
      }
    }
  });
}

// ==========================================================================
// Toast 訊息通知 (With Countdown Progress Bar)
// ==========================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  
  const bgClass = type === 'success' ? 'bg-zinc-900 border-emerald-500/40 text-emerald-100 shadow-emerald-950/40'
                : type === 'error' ? 'bg-zinc-900 border-rose-500/40 text-rose-100 shadow-rose-950/40'
                : type === 'warning' ? 'bg-zinc-900 border-amber-500/40 text-amber-100 shadow-amber-950/40'
                : 'bg-zinc-900 border-white/[0.08] text-zinc-100 shadow-black/60';

  const iconColor = type === 'success' ? 'text-emerald-400'
                  : type === 'error' ? 'text-rose-400'
                  : type === 'warning' ? 'text-amber-400'
                  : 'text-indigo-400';

  const iconName = type === 'success' ? 'check-circle'
                 : type === 'error' ? 'alert-circle'
                 : type === 'warning' ? 'alert-triangle'
                 : 'info';

  const progressBg = type === 'success' ? 'bg-emerald-400'
                   : type === 'error' ? 'bg-rose-400'
                   : type === 'warning' ? 'bg-amber-400'
                   : 'bg-indigo-400';

  toast.className = `relative flex items-center gap-3 px-4 py-3 rounded-2xl border ${bgClass} backdrop-blur-md text-xs shadow-2xl transition-all duration-300 transform translate-y-3 opacity-0 pointer-events-auto overflow-hidden min-w-[280px] max-w-md`;
  
  toast.innerHTML = `
    <i data-lucide="${iconName}" class="w-4 h-4 ${iconColor} flex-shrink-0"></i>
    <span class="font-medium flex-1 pr-2 leading-relaxed">${message}</span>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white p-1 rounded-lg transition">
      <i data-lucide="x" class="w-3.5 h-3.5"></i>
    </button>
    <div class="absolute bottom-0 left-0 h-[2.5px] ${progressBg} toast-progress"></div>
  `;

  container.appendChild(toast);
  lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-3', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-3');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// 主題切換 (Dark / Light)
function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById('theme-icon');
  if (html.classList.contains('dark')) {
    html.classList.remove('dark');
    icon.setAttribute('data-lucide', 'moon');
    localStorage.setItem('agency_theme_pref', 'light');
  } else {
    html.classList.add('dark');
    icon.setAttribute('data-lucide', 'sun');
    localStorage.setItem('agency_theme_pref', 'dark');
  }
  lucide.createIcons();
}
