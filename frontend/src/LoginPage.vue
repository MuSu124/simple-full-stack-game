<script setup>
import { reactive, ref } from 'vue'

const mode = ref('login')
const loading = ref(false)
const message = ref('')
const messageType = ref('')
const form = reactive({ username: '', password: '', passwordConfirm: '' })

// 这行代码没有什么新的东西，只是因为fetch中需要经常写后端地址，所以把后端地址存入一个变量中
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
// 每个vue文件都需要给后端发请求，既然这样，为什么不在app.vue中写一个全局的apiBaseUrl呢？
// 因为app.vue是整个应用的根组件，里面没有任何逻辑，放在这里不合适。
// 放在main.js中也不合适，因为main.js是整个应用的入口文件，里面也没有任何逻辑。
// 放在loginPage.vue中也不合适，因为loginPage.vue只是登录页面，其他页面也需要发请求。最后决定放在一个单独的文件中，这样既方便管理，又不会影响其他文件。

function switchMode(nextMode) {
  mode.value = nextMode
  message.value = ''
  messageType.value = ''
}

async function submitForm() {
  message.value = ''
  if (mode.value === 'register' && form.password !== form.passwordConfirm) {
    messageType.value = 'error'
    message.value = '两次输入的密码不一致。'
    return
  }

  loading.value = true
  const endpoint = mode.value === 'login' ? '/api/auth/login/' : '/api/auth/register/'
  try {
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: form.username, password: form.password }),
    }) // 发出一个请求，向后端发送用户名和密码，后端会返回一个响应，这个响应存在于response变量中
    const data = await response.json().catch(() => ({})) // 解析响应的JSON数据，如果解析失败，就返回一个空对象
    if (!response.ok) throw new Error(data.detail || data.message || '请求失败，请稍后重试。')

    messageType.value = 'success'
    message.value = data.message || (mode.value === 'login' ? '登录成功！' : '注册成功，请登录。')
    if (mode.value === 'register') {
      form.password = ''
      form.passwordConfirm = ''
      mode.value = 'login'
    }
  } catch (error) {
    messageType.value = 'error'
    message.value = error.message || '无法连接后端服务，请确认 Django 已启动。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <p class="game-name">⚔ 怪兽养成</p>
      <h1>{{ mode === 'login' ? '欢迎回来' : '创建账号' }}</h1> 
      <p class="hint">{{ mode === 'login' ? '登录后继续你的冒险。' : '创建你的账号，开始第一场战斗。' }}</p>
      <div class="tabs">
        <button :class="{ active: mode === 'login' }" type="button" @click="switchMode('login')">登录</button>
        <button :class="{ active: mode === 'register' }" type="button" @click="switchMode('register')">注册</button>
      </div>
      <form @submit.prevent="submitForm">
        <label for="username">用户名</label>
        <input id="username" v-model.trim="form.username" autocomplete="username" minlength="3" maxlength="30" placeholder="输入用户名" required />
        <label for="password">密码</label>
        <input id="password" v-model="form.password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" minlength="6" type="password" placeholder="至少 6 个字符" required />
        <template v-if="mode === 'register'">
          <label for="password-confirm">确认密码</label>
          <input id="password-confirm" v-model="form.passwordConfirm" autocomplete="new-password" minlength="6" type="password" placeholder="再次输入密码" required />
        </template>
        <p v-if="message" class="message" :class="messageType">{{ message }}</p>
        <button class="submit-button" :disabled="loading" type="submit">{{ loading ? '处理中…' : mode === 'login' ? '登录' : '注册' }}</button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.login-page { align-items: center; background: linear-gradient(135deg, #26183d, #6a2f52); display: flex; justify-content: center; min-height: 100vh; padding: 24px; }
.login-card { background: #fffaf3; border-radius: 18px; box-shadow: 0 18px 45px #160d264d; max-width: 420px; padding: 38px; width: 100%; }
.game-name { color: #8c4653; font-weight: 700; margin: 0 0 28px; }.hint { color: #70646a; margin: 0 0 24px; }.login-card h1 { margin: 0 0 8px; }
.tabs { background: #efe5dc; border-radius: 10px; display: grid; grid-template-columns: 1fr 1fr; margin-bottom: 24px; padding: 4px; }.tabs button { background: transparent; border: 0; border-radius: 7px; color: #75666d; cursor: pointer; padding: 9px; }.tabs .active { background: white; color: #6d3451; font-weight: 700; }
form { display: flex; flex-direction: column; } label { font-size: 14px; font-weight: 700; margin: 0 0 7px; } input { border: 1px solid #d9cdd0; border-radius: 8px; font-size: 16px; margin: 0 0 18px; padding: 11px 12px; } input:focus { border-color: #9a4a59; outline: 2px solid #e7b4a566; }.message { font-size: 14px; margin: -4px 0 16px; }.error { color: #b43342; }.success { color: #307347; }
.submit-button { background: #783950; border: 0; border-radius: 8px; color: white; cursor: pointer; font-weight: 700; padding: 12px; }.submit-button:disabled { cursor: wait; opacity: .65; }
</style>
