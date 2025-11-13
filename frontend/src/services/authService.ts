import api from './api'

export interface LoginCredentials {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserInfo {
  id: string
  email: string
  full_name: string | null
  role: string | null
  factory_id: string | null
}

export interface User {
  id: string
  email: string
  role: string
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    // Сохраняем токен
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      // Устанавливаем токен для всех последующих запросов
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
    }

    return response.data
  },

  async getCurrentUser(): Promise<UserInfo> {
    const token = localStorage.getItem('access_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }

    const response = await api.get<UserInfo>('/auth/me')
    return response.data
  },

  logout(): void {
    localStorage.removeItem('access_token')
    delete api.defaults.headers.common['Authorization']
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },

  getCurrentUserSync(): User | null {
    const token = localStorage.getItem('access_token')
    if (!token) return null
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return {
        id: payload.sub,
        email: payload.email || '',
        role: payload.role || 'viewer',
      }
    } catch {
      return null
    }
  },
}

