<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
const characters = ref([])
const monsters = ref([])
const selectedCharacterId = ref(null)
const selectedMonsterId = ref(null)
const characterHealth = ref(0)
const monsterHealth = ref(0)
const loading = ref(true)
const attacking = ref(false)
const usingDemoMonsters = ref(false)
const message = ref('')

const demoMonsters = [
  { id: 'demo-slime', name: '绿色史莱姆', level: 1, health: 45, attack: 4, reward_experience: 20, reward_gold: 8 },
  { id: 'demo-wolf', name: '森林恶狼', level: 2, health: 70, attack: 7, reward_experience: 35, reward_gold: 12 },
]

const selectedCharacter = computed(() => characters.value.find((item) => item.id === selectedCharacterId.value) ?? null)
const selectedMonster = computed(() => monsters.value.find((item) => item.id === selectedMonsterId.value) ?? null)
const characterHealthPercent = computed(() => selectedCharacter.value ? Math.max(0, characterHealth.value / selectedCharacter.value.health * 100) : 0)
const monsterHealthPercent = computed(() => selectedMonster.value ? Math.max(0, monsterHealth.value / selectedMonster.value.health * 100) : 0)
const battleOver = computed(() => characterHealth.value <= 0 || monsterHealth.value <= 0)

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.message || data.detail || '请求失败')
  return data
}

function resetBattle() {
  characterHealth.value = selectedCharacter.value?.health ?? 0
  monsterHealth.value = selectedMonster.value?.health ?? 0
  message.value = selectedCharacter.value && selectedMonster.value ? `野生的${selectedMonster.value.name}出现了！` : ''
}

async function loadPage() {
  loading.value = true
  try {
    const characterResponse = await fetch(`${apiBaseUrl}/api/characters/`, { credentials: 'include' })
    const characterData = await parseResponse(characterResponse)
    characters.value = Array.isArray(characterData) ? characterData : (characterData.characters ?? [])
    try {
      const monsterResponse = await fetch(`${apiBaseUrl}/api/monsters/`, { credentials: 'include' })
      const monsterData = await parseResponse(monsterResponse)
      monsters.value = Array.isArray(monsterData) ? monsterData : (monsterData.monsters ?? [])
    } catch {
      monsters.value = demoMonsters
      usingDemoMonsters.value = true
    }
    selectedCharacterId.value = characters.value[0]?.id ?? null
    selectedMonsterId.value = monsters.value[0]?.id ?? null
    resetBattle()
  } catch (error) {
    message.value = error.message || '加载失败，请确认已经登录。'
  } finally {
    loading.value = false
  }
}

function runDemoAttack() {
  const damageToMonster = Math.max(1, selectedCharacter.value.attack)
  monsterHealth.value = Math.max(0, monsterHealth.value - damageToMonster)
  if (monsterHealth.value === 0) {
    message.value = `胜利！你打败了${selectedMonster.value.name}。`
    return
  }
  const damageToCharacter = Math.max(1, selectedMonster.value.attack)
  characterHealth.value = Math.max(0, characterHealth.value - damageToCharacter)
  message.value = characterHealth.value === 0
    ? `挑战失败，${selectedCharacter.value.name}倒下了。`
    : `你造成 ${damageToMonster} 点伤害，同时受到 ${damageToCharacter} 点伤害。`
}

async function attack() {
  if (!selectedCharacter.value || !selectedMonster.value || battleOver.value) return
  attacking.value = true
  if (usingDemoMonsters.value) {
    runDemoAttack()
    attacking.value = false
    return
  }
  try {
    const response = await fetch(`${apiBaseUrl}/api/battles/attack/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ character_id: selectedCharacter.value.id, monster_id: selectedMonster.value.id }),
    })
    const data = await parseResponse(response)
    characterHealth.value = data.character.health
    monsterHealth.value = data.monster.health
    message.value = data.message ?? '攻击完成。'
  } catch (error) {
    message.value = error.message || '攻击失败。'
  } finally {
    attacking.value = false
  }
}

onMounted(loadPage)
</script>

<template>
  <main class="monster-page">
    <header class="topbar">
      <button class="brand" type="button" @click="router.push('/characters')">⚔ 怪兽养成</button>
      <nav aria-label="主要导航">
        <RouterLink class="nav-link" to="/characters">角色</RouterLink>
        <RouterLink class="nav-link active" to="/monsters">怪兽</RouterLink>
      </nav>
    </header>

    <section class="page-heading">
      <p class="eyebrow">BATTLE FIELD</p>
      <h1>挑战怪兽</h1>
      <p>选一名角色和怪兽，然后攻击。就这么简单。</p>
      <span v-if="usingDemoMonsters" class="demo-badge">演示怪兽</span>
    </section>

    <section v-if="loading" class="state-card">正在寻找怪兽……</section>
    <section v-else-if="characters.length === 0" class="state-card">
      <p>你还没有可出战的角色。</p>
      <button class="main-button" type="button" @click="router.push('/characters')">先去创建角色</button>
    </section>

    <section v-else class="battle-wrap">
      <div class="selectors">
        <label>出战角色
          <select v-model="selectedCharacterId" @change="resetBattle">
            <option v-for="character in characters" :key="character.id" :value="character.id">{{ character.name }} (Lv.{{ character.level }})</option>
          </select>
        </label>
        <label>挑战怪兽
          <select v-model="selectedMonsterId" @change="resetBattle">
            <option v-for="monster in monsters" :key="monster.id" :value="monster.id">{{ monster.name }} (Lv.{{ monster.level }})</option>
          </select>
        </label>
      </div>

      <div v-if="selectedCharacter && selectedMonster" class="arena">
        <article class="fighter character">
          <div class="avatar">⚔️</div><small>LV. {{ selectedCharacter.level }}</small><h2>{{ selectedCharacter.name }}</h2>
          <div class="health-row"><span>HP</span><strong>{{ characterHealth }} / {{ selectedCharacter.health }}</strong></div>
          <div class="health-track"><div :style="{ width: `${characterHealthPercent}%` }"></div></div>
          <p>攻击力 {{ selectedCharacter.attack }}</p>
        </article>
        <div class="versus">VS</div>
        <article class="fighter monster">
          <div class="avatar">👾</div><small>LV. {{ selectedMonster.level }}</small><h2>{{ selectedMonster.name }}</h2>
          <div class="health-row"><span>HP</span><strong>{{ monsterHealth }} / {{ selectedMonster.health }}</strong></div>
          <div class="health-track"><div :style="{ width: `${monsterHealthPercent}%` }"></div></div>
          <p>攻击力 {{ selectedMonster.attack }}</p>
        </article>
      </div>

      <div class="battle-controls">
        <p class="battle-message">{{ message }}</p>
        <button v-if="!battleOver" class="main-button" :disabled="attacking" type="button" @click="attack">{{ attacking ? '攻击中…' : '普通攻击' }}</button>
        <button v-else class="main-button" type="button" @click="resetBattle">再来一次</button>
      </div>
    </section>
  </main>
</template>

<style scoped>
:global(body) { margin: 0; background: #f8f4ec; }:global(*) { box-sizing: border-box; }:global(button), :global(select) { font: inherit; }
.monster-page { --ink: #271d30; --muted: #786e78; --wine: #74374f; --orange: #e07a45; min-height: 100vh; color: var(--ink); background: radial-gradient(circle at 8% 90%, #e98a5c25, transparent 28%), #f8f4ec; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
.topbar { height: 72px; padding: 0 clamp(24px, 6vw, 88px); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #dfd7ce; background: #fffcf7cc; }.brand { border: 0; color: var(--wine); background: transparent; font-size: 18px; font-weight: 800; cursor: pointer; }.topbar nav { display: flex; gap: 12px; }.nav-link { padding: 9px 15px; border-radius: 8px; color: var(--muted); text-decoration: none; font-weight: 700; }.nav-link:hover, .nav-link.active { color: var(--wine); background: #efe4dc; }
.page-heading { max-width: 1050px; margin: 0 auto; padding: 54px 24px 28px; position: relative; }.eyebrow { margin: 0 0 10px; color: var(--orange); font-size: 11px; font-weight: 900; letter-spacing: .16em; }.page-heading h1 { margin: 0 0 9px; font-family: Georgia, serif; font-size: clamp(38px, 6vw, 58px); }.page-heading > p:last-of-type { margin: 0; color: var(--muted); }.demo-badge { position: absolute; right: 24px; bottom: 30px; padding: 6px 10px; border-radius: 99px; color: #85532c; background: #f5dfbe; font-size: 12px; font-weight: 800; }
.state-card, .battle-wrap { max-width: 1002px; margin: 0 auto 60px; border: 1px solid #e0d5cb; border-radius: 18px; background: #fffcf7; box-shadow: 0 16px 44px #55362a0d; }.state-card { min-height: 320px; display: grid; place-content: center; justify-items: center; color: var(--muted); }.selectors { padding: 22px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; border-bottom: 1px solid #eadfd6; }.selectors label { color: var(--muted); font-size: 13px; font-weight: 700; }.selectors select { width: 100%; margin-top: 7px; padding: 11px; border: 1px solid #d7c7c3; border-radius: 9px; color: var(--ink); background: white; }
.arena { min-height: 340px; padding: 38px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 36px; }.fighter { text-align: center; }.fighter .avatar { width: 108px; height: 108px; margin: 0 auto 18px; border-radius: 50%; display: grid; place-items: center; background: #efe4dc; font-size: 52px; }.fighter.monster .avatar { background: #e5d9ed; }.fighter small { color: var(--orange); font-weight: 900; }.fighter h2 { margin: 6px 0 22px; font-family: Georgia, serif; font-size: 25px; }.fighter > p { color: var(--muted); }.health-row { margin-bottom: 7px; display: flex; justify-content: space-between; font-size: 12px; }.health-row span { color: #a9474f; font-weight: 900; }.health-track { height: 10px; overflow: hidden; border-radius: 99px; background: #eadfd7; }.health-track div { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #b93f4b, #eb7658); transition: width .25s; }.versus { width: 58px; height: 58px; border-radius: 50%; display: grid; place-items: center; color: white; background: var(--wine); font-family: Georgia, serif; font-weight: 900; }
.battle-controls { padding: 22px; border-top: 1px solid #eadfd6; text-align: center; }.battle-message { min-height: 24px; margin: 0 0 15px; color: var(--muted); }.main-button { border: 0; border-radius: 10px; padding: 12px 24px; color: white; background: var(--wine); box-shadow: 0 4px 0 #4f2437; font-weight: 800; cursor: pointer; }.main-button:disabled { opacity: .6; cursor: wait; }
@media (max-width: 650px) { .topbar { padding: 0 18px; }.page-heading { padding-top: 38px; }.demo-badge { position: static; display: inline-block; margin-top: 15px; }.state-card, .battle-wrap { margin-left: 18px; margin-right: 18px; }.selectors { grid-template-columns: 1fr; }.arena { padding: 28px 20px; grid-template-columns: 1fr; gap: 18px; }.fighter .avatar { width: 82px; height: 82px; font-size: 40px; }.versus { width: 44px; height: 44px; margin: 0 auto; }.fighter h2 { margin-bottom: 14px; } }
</style>
