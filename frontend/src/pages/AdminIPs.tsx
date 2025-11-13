import { useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { factoryService } from '../services/factoryService';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface IP {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  bin?: string;
  plan_code: string;
  factory_limit?: string;
  is_active: boolean;
  user_id?: string;
  factory_ids: string[];
  created_at: string;
}

interface IPCreate {
  full_name: string;
  email: string;
  phone: string;
  bin?: string;
  plan_code: string;
  factory_ids?: string[];
}

export default function AdminIPs() {
  const [ips, setIPs] = useState<IP[]>([]);
  const [factories, setFactories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState<IPCreate>({
    full_name: '',
    email: '',
    phone: '',
    bin: '',
    plan_code: 'basic',
    factory_ids: [],
  });
  const navigate = useNavigate();

  useEffect(() => {
    const user = authService.getCurrentUserSync();
    if (!user || user.role !== 'admin') {
      toast.error('Доступ запрещен');
      navigate('/');
      return;
    }

    loadData();
  }, [navigate]);

  const loadData = async () => {
    try {
      const [ipsRes, factoriesRes] = await Promise.all([
        api.get<IP[]>('/api/v1/individual-entrepreneurs/'),
        factoryService.getFactories(),
      ]);
      setIPs(ipsRes.data || []);
      setFactories(factoriesRes?.items || []);
    } catch (error: any) {
      // Устанавливаем пустые массивы при ошибке
      setIPs([]);
      setFactories([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.full_name || !formData.email || !formData.phone || !formData.plan_code) {
      toast.error('Заполните все обязательные поля');
      return;
    }

    try {
      await api.post('/api/v1/individual-entrepreneurs/', formData);
      toast.success('ИП успешно создан!');
      setShowCreateModal(false);
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        bin: '',
        plan_code: 'basic',
        factory_ids: [],
      });
      await loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка при создании ИП');
    }
  };

  const handleToggleActive = async (ip: IP) => {
    try {
      await api.put(`/api/v1/individual-entrepreneurs/${ip.id}`, {
        is_active: !ip.is_active,
      });
      toast.success('Статус обновлен');
      await loadData();
    } catch (error: any) {
      toast.error('Ошибка при обновлении статуса');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Вы уверены, что хотите удалить этого ИП?')) return;

    try {
      await api.delete(`/api/v1/individual-entrepreneurs/${id}`);
      toast.success('ИП удален');
      await loadData();
    } catch (error: any) {
      toast.error('Ошибка при удалении ИП');
    }
  };

  const getPlanName = (code: string) => {
    const plans: { [key: string]: string } = {
      basic: 'Базовый',
      analytics: 'Аналитический',
      ip: 'ИП тариф',
    };
    return plans[code] || code;
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Управление индивидуальными предпринимателями
        </h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Добавить ИП
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                ФИО
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Телефон
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Тариф
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Заводы
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {ips.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                  Нет зарегистрированных ИП
                </td>
              </tr>
            ) : (
              ips.map((ip) => (
              <tr key={ip.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {ip.full_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {ip.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {ip.phone}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {getPlanName(ip.plan_code)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-300">
                  {ip.factory_ids.length > 0
                    ? factories
                        .filter((f) => ip.factory_ids.includes(f.id))
                        .map((f) => f.name)
                        .join(', ')
                    : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 py-1 rounded text-sm font-medium ${
                      ip.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}
                  >
                    {ip.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggleActive(ip)}
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    >
                      {ip.is_active ? 'Деактивировать' : 'Активировать'}
                    </button>
                    <button
                      onClick={() => handleDelete(ip.id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400"
                    >
                      Удалить
                    </button>
                  </div>
                </td>
              </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Модальное окно создания ИП */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
              Добавить ИП
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ФИО *
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Телефон *
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  БИН (опционально)
                </label>
                <input
                  type="text"
                  value={formData.bin}
                  onChange={(e) => setFormData({ ...formData, bin: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Тарифный план *
                </label>
                <select
                  value={formData.plan_code}
                  onChange={(e) => setFormData({ ...formData, plan_code: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="basic">Базовый (1 завод)</option>
                  <option value="analytics">Аналитический (1 завод)</option>
                  <option value="ip">ИП тариф (несколько заводов)</option>
                </select>
              </div>
              {formData.plan_code === 'ip' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Заводы (для ИП тарифа)
                  </label>
                  <div className="max-h-40 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-2">
                    {factories.map((factory) => (
                      <label key={factory.id} className="flex items-center gap-2 mb-2">
                        <input
                          type="checkbox"
                          checked={formData.factory_ids?.includes(factory.id)}
                          onChange={(e) => {
                            const ids = formData.factory_ids || [];
                            if (e.target.checked) {
                              setFormData({ ...formData, factory_ids: [...ids, factory.id] });
                            } else {
                              setFormData({
                                ...formData,
                                factory_ids: ids.filter((id) => id !== factory.id),
                              });
                            }
                          }}
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {factory.name}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <button
                  onClick={handleCreate}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Создать
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                >
                  Отмена
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

