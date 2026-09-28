<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const characters = ref([])
const selectedId = ref(null)
const loading = ref(true)
const saving = ref(false)
const upgrading = ref(false)
const showCreateForm = ref(false)
const message = ref('')
const messageType = ref('')
const createForm = reactive({ name: '' })

const selectedCharacter = computed(() => (
  characters.value.find((character) => character.id === selectedId.value) ?? null
))

const experiencePercent = computed(() => {
  if (!selectedCharacter.value) return 0
  const requiredExperience = selectedCharacter.value.level * 100
  return Math.min((selectedCharacter.value.experience / requiredExperience) * 100, 100)
})

function showMessage(text, type = 'error') {
  message.value = text
  messageType.value = type
}

async function parseResponse(response) {
  // 和其他的async函数不同的一个点在于，这个函数并不主动发送请求，而是接收一个response对象，然后解析它的JSON数据。
  // 主要是一个工具函数，因为接收response这个工作实际是fetch函数的工作，所以这个函数不需要知道请求的url和method，
  // 它的任务是解析response，只需要知道response对象就可以了。

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.message || data.detail || '请求失败，请稍后重试。')
  }
  return data
}

async function loadCharacters() {
  loading.value = true
  message.value = ''
  try {
    const response = await fetch(`${apiBaseUrl}/api/characters/`, {
      credentials: 'include',
    })
    const data = await parseResponse(response)
    characters.value = Array.isArray(data) ? data : (data.characters ?? [])
    selectedId.value = characters.value[0]?.id ?? null
  } catch (error) {
    showMessage(error.message || '无法读取角色数据。')
  } finally {
    loading.value = false
  }
}

async function createCharacter() {
  if (!createForm.name.trim()) return

  saving.value = true
  message.value = ''
  try {
    const response = await fetch(`${apiBaseUrl}/api/characters/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ name: createForm.name.trim() }),
    })
    const data = await parseResponse(response)
    const character = data.character ?? data
    characters.value.push(character)
    selectedId.value = character.id
    createForm.name = ''
    showCreateForm.value = false
    showMessage('角色创建成功！', 'success')
  } catch (error) {
    showMessage(error.message || '创建角色失败。')
  } finally {
    saving.value = false
  }
}

async function upgradeCharacter() {
  if (!selectedCharacter.value) return

  upgrading.value = true
  message.value = ''
  try {
    const response = await fetch(
      `${apiBaseUrl}/api/characters/${selectedCharacter.value.id}/upgrade/`,
      { method: 'POST', credentials: 'include' },
    )
    const data = await parseResponse(response)
    const updatedCharacter = data.character ?? data
    const index = characters.value.findIndex((character) => character.id === updatedCharacter.id)
    characters.value[index] = updatedCharacter
    showMessage('强化成功，角色变得更强了！', 'success')
  } catch (error) {
    showMessage(error.message || '强化角色失败。')
  } finally {
    upgrading.value = false
  }
}

onMounted(loadCharacters)
</script>

<template>
  <main class="character-page">
    <header class="topbar">
      <button class="brand" type="button" @click="router.push('/characters')">
        <span class="brand-mark">⚔</span>
        怪兽养成
      </button>
      <nav aria-label="主要导航">
        <RouterLink class="nav-link active" to="/characters">角色</RouterLink>
        <RouterLink class="nav-link" to="/monsters">怪兽</RouterLink>
      </nav>
    </header>

    <section class="page-heading">
      <div>
        <p class="eyebrow">CHARACTER CAMP</p>
        <h1>我的角色</h1>
        <p>挑选你的冒险者，强化属性，然后迎接下一场战斗。</p>
      </div>
      <button class="primary-button" type="button" @click="showCreateForm = true">
        <span>＋</span> 创建角色
      </button>
    </section>

    <p v-if="message" class="message" :class="messageType" role="status">
      {{ message }}
    </p>

    <section v-if="loading" class="state-card">
      <div class="spinner"></div>
      <p>正在召集你的角色……</p>
    </section>

    <section v-else-if="characters.length === 0" class="state-card empty-state">
      <div class="empty-icon">🛡️</div>
      <h2>队伍还是空的</h2>
      <p>创建你的第一位角色，冒险才能正式开始。</p>
      <button class="primary-button" type="button" @click="showCreateForm = true">创建第一个角色</button>
    </section>

    <section v-else class="character-layout">
      <aside class="character-list" aria-label="角色列表">
        <p class="section-label">冒险队伍 · {{ characters.length }}</p>
        <button
          v-for="character in characters"
          :key="character.id"
          class="character-list-item"
          :class="{ selected: character.id === selectedId }"
          type="button"
          @click="selectedId = character.id"
        >
          <span class="mini-avatar">{{ character.name.slice(0, 1).toUpperCase() }}</span>
          <span class="list-copy">
            <strong>{{ character.name }}</strong>
            <small>等级 {{ character.level }}</small>
          </span>
          <span class="chevron">›</span>
        </button>
      </aside>

      <article v-if="selectedCharacter" class="character-detail">
        <div class="hero-panel">
          <div class="hero-avatar">{{ selectedCharacter.name.slice(0, 1).toUpperCase() }}</div>
          <div class="hero-copy">
            <span class="level-badge">LV. {{ selectedCharacter.level }}</span>
            <h2>{{ selectedCharacter.name }}</h2>
            <p>准备好接受新的挑战</p>
          </div>
          <div class="gold"><span>●</span> {{ selectedCharacter.gold }}</div>
        </div>

        <div class="experience-block">
          <div class="experience-copy">
            <span>当前经验</span>
            <strong>{{ selectedCharacter.experience }} / {{ selectedCharacter.level * 100 }}</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${experiencePercent}%` }"></div>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card health-stat">
            <span class="stat-icon">♥</span>
            <div><small>生命值</small><strong>{{ selectedCharacter.health }}</strong></div>
          </div>
          <div class="stat-card attack-stat">
            <span class="stat-icon">⚡</span>
            <div><small>攻击力</small><strong>{{ selectedCharacter.attack }}</strong></div>
          </div>
          <div class="stat-card level-stat">
            <span class="stat-icon">★</span>
            <div><small>当前等级</small><strong>{{ selectedCharacter.level }}</strong></div>
          </div>
        </div>

        <div class="actions">
          <button class="upgrade-button" :disabled="upgrading" type="button" @click="upgradeCharacter">
            {{ upgrading ? '强化中…' : '强化角色' }}
          </button>
          <button class="battle-button" type="button" @click="router.push('/monsters')">前往挑战 →</button>
        </div>
      </article>
    </section>

    <div v-if="showCreateForm" class="modal-backdrop" @click.self="showCreateForm = false">
      <form class="create-dialog" @submit.prevent="createCharacter">
        <button class="close-button" type="button" aria-label="关闭" @click="showCreateForm = false">×</button>
        <p class="eyebrow">NEW ADVENTURER</p>
        <h2>创建新角色</h2>
        <p>为你的冒险者取一个响亮的名字。</p>
        <label for="character-name">角色名称</label>
        <input
          id="character-name"
          v-model.trim="createForm.name"
          maxlength="50"
          minlength="1"
          placeholder="例如：暗影骑士"
          required
          autofocus
        />
        <button class="primary-button full-width" :disabled="saving" type="submit">
          {{ saving ? '创建中…' : '确认创建' }}
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
:global(body) { margin: 0; background: #f8f4ec; }
:global(*) { box-sizing: border-box; }
:global(button), :global(input) { font: inherit; }
.character-page { --ink: #271d30; --muted: #786e78; --wine: #74374f; --orange: #e07a45; min-height: 100vh; color: var(--ink); background: radial-gradient(circle at 90% 3%, #f4c67e40, transparent 26%), #f8f4ec; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.topbar { height: 72px; padding: 0 clamp(24px, 6vw, 88px); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #dfd7ce; background: #fffcf7cc; backdrop-filter: blur(12px); }
.brand { border: 0; background: transparent; color: var(--wine); font-size: 18px; font-weight: 800; cursor: pointer; }.brand-mark { color: var(--orange); margin-right: 7px; }.topbar nav { display: flex; gap: 12px; }.nav-link { padding: 9px 15px; border-radius: 8px; color: var(--muted); text-decoration: none; font-weight: 700; }.nav-link:hover, .nav-link.active { color: var(--wine); background: #efe4dc; }
.page-heading { max-width: 1180px; margin: 0 auto; padding: 64px 28px 32px; display: flex; align-items: flex-end; justify-content: space-between; gap: 28px; }.eyebrow { margin: 0 0 12px; color: var(--orange); font-size: 11px; font-weight: 900; letter-spacing: .16em; }.page-heading h1 { margin: 0 0 10px; font-family: Georgia, serif; font-size: clamp(38px, 6vw, 62px); line-height: 1; }.page-heading p:not(.eyebrow) { margin: 0; color: var(--muted); }
.primary-button, .upgrade-button, .battle-button { border: 0; border-radius: 10px; padding: 13px 19px; cursor: pointer; font-weight: 800; transition: transform .16s, box-shadow .16s; }.primary-button { color: white; background: var(--wine); box-shadow: 0 5px 0 #4f2437; }.primary-button:hover:not(:disabled), .upgrade-button:hover:not(:disabled), .battle-button:hover { transform: translateY(-2px); }.primary-button:disabled, .upgrade-button:disabled { opacity: .6; cursor: wait; }
.message { max-width: 1124px; margin: 0 auto 20px; padding: 12px 16px; border-radius: 9px; }.message.error { color: #8e2934; background: #f8dfe0; }.message.success { color: #24653c; background: #dff1e3; }
.state-card { max-width: 1124px; min-height: 360px; margin: 0 auto; border: 1px dashed #cfbeb3; border-radius: 18px; display: grid; place-content: center; justify-items: center; color: var(--muted); background: #fffcf7; }.spinner { width: 34px; height: 34px; border: 4px solid #eaded3; border-top-color: var(--wine); border-radius: 50%; animation: spin .8s linear infinite; }.empty-state h2 { margin: 10px 0 5px; color: var(--ink); }.empty-state p { margin: 0 0 24px; }.empty-icon { font-size: 55px; }@keyframes spin { to { transform: rotate(360deg); } }
.character-layout { max-width: 1124px; margin: 0 auto; padding-bottom: 70px; display: grid; grid-template-columns: 280px 1fr; gap: 24px; }.character-list, .character-detail { border: 1px solid #e0d5cb; border-radius: 18px; background: #fffcf7; box-shadow: 0 16px 44px #55362a0d; }.character-list { padding: 17px; align-self: start; }.section-label { margin: 2px 5px 14px; color: #94858b; font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }.character-list-item { width: 100%; margin-top: 7px; padding: 11px; border: 1px solid transparent; border-radius: 12px; display: flex; align-items: center; gap: 11px; color: var(--ink); background: transparent; text-align: left; cursor: pointer; }.character-list-item:hover { background: #f6eee7; }.character-list-item.selected { border-color: #c99782; background: #f3e4da; }.mini-avatar { width: 41px; height: 41px; border-radius: 10px; display: grid; place-items: center; color: white; background: linear-gradient(145deg, #864762, #d46d4a); font-family: Georgia, serif; font-size: 20px; font-weight: 800; }.list-copy { min-width: 0; display: flex; flex: 1; flex-direction: column; }.list-copy strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.list-copy small { margin-top: 3px; color: var(--muted); }.chevron { color: #9b8a8c; font-size: 24px; }
.character-detail { overflow: hidden; }.hero-panel { padding: 32px; display: flex; align-items: center; gap: 22px; color: white; background: radial-gradient(circle at 83% 20%, #eb995c, transparent 22%), linear-gradient(135deg, #302141, #70394f); }.hero-avatar { width: 92px; height: 92px; border: 3px solid #ffffff52; border-radius: 24px; display: grid; place-items: center; background: #ffffff17; font-family: Georgia, serif; font-size: 48px; font-weight: 800; }.hero-copy { flex: 1; }.hero-copy h2 { margin: 7px 0 5px; font-family: Georgia, serif; font-size: 34px; }.hero-copy p { margin: 0; color: #eadbe1; }.level-badge { padding: 4px 8px; border-radius: 5px; color: #311e31; background: #f3bd65; font-size: 11px; font-weight: 900; }.gold { align-self: flex-start; padding: 8px 12px; border-radius: 999px; background: #20122966; font-weight: 800; }.gold span { color: #f2bb51; }
.experience-block { padding: 27px 32px 10px; }.experience-copy { margin-bottom: 9px; display: flex; justify-content: space-between; color: var(--muted); font-size: 13px; }.experience-copy strong { color: var(--ink); }.progress-track { height: 10px; border-radius: 999px; overflow: hidden; background: #e9dfd6; }.progress-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #d96848, #edab55); transition: width .4s; }
.stats-grid { padding: 20px 32px 27px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 13px; }.stat-card { min-height: 91px; padding: 17px; border: 1px solid #eadfd6; border-radius: 13px; display: flex; align-items: center; gap: 14px; background: #fff; }.stat-icon { width: 39px; height: 39px; border-radius: 10px; display: grid; place-items: center; font-size: 18px; }.health-stat .stat-icon { color: #b43f4c; background: #fae4e4; }.attack-stat .stat-icon { color: #b26725; background: #f9ead7; }.level-stat .stat-icon { color: #6751a1; background: #ece7f7; }.stat-card div { display: flex; flex-direction: column; }.stat-card small { color: var(--muted); }.stat-card strong { margin-top: 3px; font-size: 22px; }
.actions { padding: 0 32px 32px; display: flex; gap: 12px; }.upgrade-button { flex: 1; color: white; background: var(--orange); box-shadow: 0 4px 0 #aa4f2f; }.battle-button { flex: 1; color: var(--wine); border: 1px solid #c9a89b; background: white; }
.modal-backdrop { position: fixed; inset: 0; z-index: 10; padding: 24px; display: grid; place-items: center; background: #201527b8; backdrop-filter: blur(4px); }.create-dialog { width: min(100%, 430px); padding: 36px; position: relative; border-radius: 18px; background: #fffaf3; box-shadow: 0 24px 80px #120c1b80; }.create-dialog h2 { margin: 0 0 8px; font-family: Georgia, serif; font-size: 30px; }.create-dialog > p:not(.eyebrow) { margin: 0 0 24px; color: var(--muted); }.create-dialog label { display: block; margin-bottom: 7px; font-size: 14px; font-weight: 800; }.create-dialog input { width: 100%; margin-bottom: 18px; padding: 12px; border: 1px solid #d7c7c3; border-radius: 9px; outline: none; }.create-dialog input:focus { border-color: var(--wine); box-shadow: 0 0 0 3px #73364f1c; }.close-button { position: absolute; top: 15px; right: 17px; border: 0; color: #8c7c82; background: transparent; font-size: 27px; cursor: pointer; }.full-width { width: 100%; }
@media (max-width: 760px) { .topbar { padding: 0 18px; }.page-heading { padding-top: 38px; align-items: flex-start; flex-direction: column; }.character-layout { padding: 0 18px 50px; grid-template-columns: 1fr; }.character-list { display: flex; overflow-x: auto; }.section-label { display: none; }.character-list-item { min-width: 180px; }.hero-panel { padding: 24px; flex-wrap: wrap; }.hero-avatar { width: 72px; height: 72px; }.gold { margin-left: auto; }.stats-grid { padding: 18px 22px; grid-template-columns: 1fr; }.actions { padding: 0 22px 25px; flex-direction: column; }.message, .state-card { margin-left: 18px; margin-right: 18px; }.state-card { padding: 30px; text-align: center; } }
</style>
