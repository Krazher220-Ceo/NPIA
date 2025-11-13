import { useEffect, useState } from 'react';
import { applicationService, Application, ApproveApplicationRequest, ApproveApplicationResponse } from '../services/applicationService';
import { factoryService } from '../services/factoryService';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

export default function AdminApplications() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [factories, setFactories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [approveData, setApproveData] = useState<ApproveApplicationRequest>({
    username: '',
    factory_id: undefined,
  });
  const navigate = useNavigate();

  useEffect(() => {
    // Проверка прав доступа
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
      const [appsRes, factoriesRes] = await Promise.all([
        applicationService.getApplications(),
        factoryService.getFactories(),
      ]);
      setApplications(appsRes || []);
      setFactories(factoriesRes?.items || []);
    } catch (error: any) {
      // Устанавливаем пустые массивы при ошибке
      setApplications([]);
      setFactories([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = (application: Application) => {
    setSelectedApp(application);
    setApproveData({
      username: application.email.split('@')[0],
      factory_id: undefined,
    });
    setShowApproveModal(true);
  };

  const handleApproveSubmit = async () => {
    if (!selectedApp || !approveData.username) {
      toast.error('Заполните все поля');
      return;
    }

    try {
      const response = await applicationService.approveApplication(
        selectedApp.id,
        approveData
      );
      toast.success('Аккаунт успешно создан!');
      await loadData();
      setShowApproveModal(false);
      
      // Показываем модальное окно с данными для PDF
      showPasswordModal(response);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка при создании аккаунта');
    }
  };

  const handleReject = async (id: string) => {
    const reason = prompt('Укажите причину отклонения:');
    if (!reason) return;

    try {
      await applicationService.rejectApplication(id, reason);
      toast.success('Заявка отклонена');
      await loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка при отклонении заявки');
    }
  };

  const showPasswordModal = (data: ApproveApplicationResponse) => {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Данные для входа</h3>
        <div class="space-y-3 mb-4">
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">ЛОГИН:</label>
            <p class="text-lg font-mono text-gray-900 dark:text-white">${data.username}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">ПАРОЛЬ:</label>
            <p class="text-lg font-mono text-gray-900 dark:text-white">${data.password}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">EMAIL:</label>
            <p class="text-lg font-mono text-gray-900 dark:text-white">${data.email}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button id="copy-btn" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Копировать
          </button>
          <button id="download-pdf-btn" class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Скачать PDF
          </button>
          <button id="close-btn" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
            Закрыть
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    const copyBtn = modal.querySelector('#copy-btn');
    const downloadBtn = modal.querySelector('#download-pdf-btn');
    const closeBtn = modal.querySelector('#close-btn');

    copyBtn?.addEventListener('click', () => {
      const text = `ЛОГИН: ${data.username}\nПАРОЛЬ: ${data.password}\nEMAIL: ${data.email}`;
      navigator.clipboard.writeText(text);
      toast.success('Скопировано в буфер обмена');
    });

    downloadBtn?.addEventListener('click', () => {
      generatePDF(data);
    });

    closeBtn?.addEventListener('click', () => {
      document.body.removeChild(modal);
    });
  };

  const generatePDF = (data: ApproveApplicationResponse) => {
    // Используем jsPDF для генерации PDF
    import('jspdf').then((jsPDF) => {
      const doc = new jsPDF.default();
      
      doc.setFontSize(18);
      doc.text('Данные для входа в систему', 20, 20);
      
      doc.setFontSize(12);
      doc.text(`ЛОГИН: ${data.username}`, 20, 40);
      doc.text(`ПАРОЛЬ: ${data.password}`, 20, 50);
      doc.text(`EMAIL: ${data.email}`, 20, 60);
      
      doc.text('Сохраните эти данные в безопасном месте!', 20, 80);
      
      doc.save(`credentials_${data.username}.pdf`);
      toast.success('PDF скачан');
    }).catch(() => {
      toast.error('Ошибка при генерации PDF. Установите библиотеку jspdf.');
    });
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      new: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    const labels = {
      new: 'Новая',
      approved: 'Одобрена',
      rejected: 'Отклонена',
    };
    return (
      <span className={`px-2 py-1 rounded text-sm font-medium ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Заявки на доступ к платформе
        </h1>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                ФИО
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Телефон
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Тариф
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Дата
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Контакты
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {applications.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                  Нет заявок
                </td>
              </tr>
            ) : (
              applications.map((app) => (
              <tr key={app.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {app.full_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {app.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {app.phone}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {app.plan_code === 'basic' && 'Базовый'}
                  {app.plan_code === 'analytics' && 'Аналитический'}
                  {app.plan_code === 'ip' && 'ИП тариф'}
                  {!app.plan_code && '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(app.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                  {new Date(app.created_at).toLocaleDateString('ru-RU')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex gap-2">
                    <a
                      href={`mailto:${app.email}`}
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                      title="Написать на email"
                    >
                      📧
                    </a>
                    <a
                      href={`tel:${app.phone}`}
                      className="text-green-600 hover:text-green-900 dark:text-green-400"
                      title="Позвонить"
                    >
                      📞
                    </a>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {app.status === 'new' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApprove(app)}
                        className="text-green-600 hover:text-green-900 dark:text-green-400"
                      >
                        Одобрить
                      </button>
                      <button
                        onClick={() => handleReject(app.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400"
                      >
                        Отклонить
                      </button>
                    </div>
                  )}
                  {app.status === 'approved' && app.created_username && (
                    <span className="text-gray-500 dark:text-gray-400">
                      Аккаунт: {app.created_username}
                    </span>
                  )}
                </td>
              </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Модальное окно одобрения */}
      {showApproveModal && selectedApp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
              Одобрить заявку
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Логин *
                </label>
                <input
                  type="text"
                  value={approveData.username}
                  onChange={(e) => setApproveData({ ...approveData, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Завод (опционально)
                </label>
                <select
                  value={approveData.factory_id || ''}
                  onChange={(e) => setApproveData({ ...approveData, factory_id: e.target.value || undefined })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Не выбран</option>
                  {factories.map((factory) => (
                    <option key={factory.id} value={factory.id}>
                      {factory.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleApproveSubmit}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Создать аккаунт
                </button>
                <button
                  onClick={() => setShowApproveModal(false)}
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

