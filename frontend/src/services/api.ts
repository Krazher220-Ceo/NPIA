import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем токен из localStorage при инициализации
const token = localStorage.getItem('access_token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек или неверный
      localStorage.removeItem('access_token')
      delete api.defaults.headers.common['Authorization']
      // Редирект на внешний лендинг для входа
      window.location.href = 'http://localhost:5173/login.html'
    }
    return Promise.reject(error)
  }
)

export default api

