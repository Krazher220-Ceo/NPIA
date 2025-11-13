import { useEffect, useState } from 'react';
import { productionService, ProductionCycle, MaintenanceLog } from '../services/productionService';
import toast from 'react-hot-toast';

export default function Production() {
  const [cycles, setCycles] = useState<ProductionCycle[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceLog[]>([]);
  const [activeTab, setActiveTab] = useState<'cycles' | 'maintenance'>('cycles');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [cyclesRes, maintenanceRes] = await Promise.all([
        productionService.getCycles({ limit: 20 }),
        productionService.getMaintenanceLogs({ limit: 20 }),
      ]);
      setCycles(cyclesRes?.items || []);
      setMaintenance(maintenanceRes?.items || []);
    } catch (error: any) {
      // Устанавливаем пустые массивы при ошибке
      setCycles([]);
      setMaintenance([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Производство и обслуживание</h1>

      {/* Табы */}
      <div className="mb-6 border-b dark:border-gray-700">
        <button
          onClick={() => setActiveTab('cycles')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'cycles'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Производственные циклы
        </button>
        <button
          onClick={() => setActiveTab('maintenance')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'maintenance'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Обслуживание
        </button>
      </div>

      {/* Производственные циклы */}
      {activeTab === 'cycles' && (
        <div className="overflow-x-auto">
          {cycles.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
              Нет данных о производственных циклах
            </div>
          ) : (
            <table className="min-w-full bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Продукт</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Начало</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Окончание</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">План</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Факт</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">OEE</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Статус</th>
                </tr>
              </thead>
              <tbody>
                {cycles.map((cycle) => (
                <tr key={cycle.id} className="border-t">
                  <td className="px-4 py-3">{cycle.product_name || '-'}</td>
                  <td className="px-4 py-3 text-sm">
                    {new Date(cycle.start_time).toLocaleString('ru-RU')}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {cycle.end_time ? new Date(cycle.end_time).toLocaleString('ru-RU') : '-'}
                  </td>
                  <td className="px-4 py-3">{cycle.planned_quantity || '-'}</td>
                  <td className="px-4 py-3">{cycle.actual_quantity || '-'}</td>
                  <td className="px-4 py-3">
                    {cycle.oee_score ? `${cycle.oee_score.toFixed(1)}%` : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded ${
                      cycle.status === 'completed' ? 'bg-green-100 text-green-800' :
                      cycle.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {cycle.status}
                    </span>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Обслуживание */}
      {activeTab === 'maintenance' && (
        <div className="overflow-x-auto">
          {maintenance.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
              Нет данных об обслуживании
            </div>
          ) : (
            <table className="min-w-full bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Тип</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Название</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Дата</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Длительность</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Стоимость</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Статус</th>
                </tr>
              </thead>
              <tbody>
                {maintenance.map((log) => (
                <tr key={log.id} className="border-t">
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-gray-100 rounded text-sm">
                      {log.type}
                    </span>
                  </td>
                  <td className="px-4 py-3">{log.title}</td>
                  <td className="px-4 py-3 text-sm">
                    {log.scheduled_date ? new Date(log.scheduled_date).toLocaleDateString('ru-RU') : '-'}
                  </td>
                  <td className="px-4 py-3">
                    {log.duration_minutes ? `${log.duration_minutes} мин` : '-'}
                  </td>
                  <td className="px-4 py-3">
                    {log.cost ? new Intl.NumberFormat('ru-KZ', {
                      style: 'currency',
                      currency: 'KZT',
                    }).format(log.cost) : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded ${
                      log.status === 'completed' ? 'bg-green-100 text-green-800' :
                      log.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

