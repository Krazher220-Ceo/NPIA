import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function Apply() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    plan_code: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    if (!formData.full_name.trim()) {
      toast.error('Введите ФИО');
      return false;
    }
    if (!formData.email.trim() || !formData.email.includes('@')) {
      toast.error('Введите корректный email');
      return false;
    }
    if (!formData.phone.trim()) {
      toast.error('Введите телефон');
      return false;
    }
    if (!formData.plan_code.trim()) {
      toast.error('Выберите тарифный план');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);

    try {
      await api.post('/api/v1/applications/', formData);
      toast.success('Заявка отправлена успешно!');
      setSubmitted(true);
      setFormData({ full_name: '', email: '', phone: '', plan_code: '', description: '' });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка при отправке заявки');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 dark:bg-green-900 mb-4">
              <svg className="h-8 w-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Заявка отправлена
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Ожидайте подтверждения на email. Мы свяжемся с вами в ближайшее время.
            </p>
            <button
              onClick={() => {
                setSubmitted(false);
                navigate('/');
              }}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Вернуться на главную
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Подать заявку на доступ к платформе
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Заполните форму ниже и выберите тарифный план. Мы рассмотрим вашу заявку и свяжемся с вами.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                ФИО *
              </label>
              <input
                id="full_name"
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Иванов Иван Иванович"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email *
              </label>
              <input
                id="email"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="example@mail.com"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Телефон *
              </label>
              <input
                id="phone"
                type="tel"
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="+7 (XXX) XXX-XX-XX"
              />
            </div>

            <div>
              <label htmlFor="plan_code" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Тарифный план *
              </label>
              <select
                id="plan_code"
                required
                value={formData.plan_code}
                onChange={(e) => setFormData({ ...formData, plan_code: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Выберите тариф</option>
                <option value="basic">Базовый - 150,000 тг/месяц (до 10 единиц оборудования)</option>
                <option value="analytics">Аналитический - 450,000 тг/месяц (до 50 единиц оборудования, ИИ-анализ)</option>
                <option value="ip">ИП тариф - по запросу (несколько заводов, общая аналитика)</option>
              </select>
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Дополнительная информация (опционально)
              </label>
              <textarea
                id="description"
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Опишите ваше предприятие, количество оборудования или другие детали..."
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                {loading ? 'Отправка...' : 'Подать заявку'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

