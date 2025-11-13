import { useEffect, useState } from 'react';
import { integrationService, ExternalSystem } from '../services/integrationService';
import toast from 'react-hot-toast';

export default function Integrations() {
  const [systems, setSystems] = useState<ExternalSystem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await integrationService.getSystems();
      setSystems(response?.items || []);
    } catch (error: any) {
      // Устанавливаем пустой массив при ошибке
      setSystems([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const getSystemTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      erp: 'ERP система',
      mes: 'MES система',
      scada: 'SCADA',
      '1c': '1С:Предприятие',
      sap: 'SAP',
    };
    return labels[type] || type;
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Интеграции</h1>

      {systems.length === 0 ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
          Нет настроенных интеграций
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systems.map((system) => (
          <div key={system.id} className="border rounded-lg p-6 shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">{system.name}</h3>
              <span className={`px-2 py-1 rounded text-sm ${
                system.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {system.is_active ? 'Активна' : 'Неактивна'}
              </span>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <span className="font-semibold text-gray-600">Тип системы:</span>
                <div className="mt-1">{getSystemTypeLabel(system.system_type)}</div>
              </div>

              <div>
                <span className="font-semibold text-gray-600">Тип подключения:</span>
                <div className="mt-1">{system.connection_type}</div>
              </div>

              <div>
                <span className="font-semibold text-gray-600">Частота синхронизации:</span>
                <div className="mt-1">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {system.sync_frequency}
                  </span>
                </div>
              </div>

              {system.last_sync_at && (
                <div>
                  <span className="font-semibold text-gray-600">Последняя синхронизация:</span>
                  <div className="mt-1 text-xs text-gray-500">
                    {new Date(system.last_sync_at).toLocaleString('ru-RU')}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 flex gap-2">
              <button className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Настроить
              </button>
              <button className="px-4 py-2 border rounded hover:bg-gray-50">
                Тест
              </button>
            </div>
          </div>
          ))}
        </div>
      )}
    </div>
  );
}

