import { useEffect, useState } from 'react';
import { reportService, ReportTemplate, GeneratedReport } from '../services/reportService';
import toast from 'react-hot-toast';

export default function Reports() {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [activeTab, setActiveTab] = useState<'templates' | 'generated'>('generated');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [templatesRes, reportsRes] = await Promise.all([
        reportService.getTemplates(),
        reportService.getGeneratedReports({ limit: 20 }),
      ]);
      setTemplates(templatesRes?.items || []);
      setReports(reportsRes?.items || []);
    } catch (error: any) {
      // Устанавливаем пустые массивы при ошибке
      setTemplates([]);
      setReports([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return '-';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    if (mb >= 1) return `${mb.toFixed(2)} MB`;
    return `${kb.toFixed(2)} KB`;
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Отчеты</h1>

      {/* Табы */}
      <div className="mb-6 border-b dark:border-gray-700">
        <button
          onClick={() => setActiveTab('generated')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'generated'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Сгенерированные отчеты
        </button>
        <button
          onClick={() => setActiveTab('templates')}
          className={`px-4 py-2 font-semibold ${
            activeTab === 'templates'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Шаблоны отчетов
        </button>
      </div>

      {/* Сгенерированные отчеты */}
      {activeTab === 'generated' && (
        <div className="overflow-x-auto">
          {reports.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
              Нет сгенерированных отчетов
            </div>
          ) : (
            <table className="min-w-full bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Период</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Файл</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Размер</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Создан</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Действия</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                <tr key={report.id} className="border-t">
                  <td className="px-4 py-3 text-sm">
                    {report.period_start && report.period_end ? (
                      <>
                        {new Date(report.period_start).toLocaleDateString('ru-RU')} -{' '}
                        {new Date(report.period_end).toLocaleDateString('ru-RU')}
                      </>
                    ) : '-'}
                  </td>
                  <td className="px-4 py-3">
                    {report.file_url ? (
                      <a href={report.file_url} className="text-blue-600 hover:underline">
                        {report.file_url.split('/').pop()}
                      </a>
                    ) : '-'}
                  </td>
                  <td className="px-4 py-3">{formatFileSize(report.file_size_bytes)}</td>
                  <td className="px-4 py-3 text-sm">
                    {new Date(report.generated_at).toLocaleString('ru-RU')}
                  </td>
                  <td className="px-4 py-3">
                    {report.file_url && (
                      <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Скачать
                      </button>
                    )}
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Шаблоны */}
      {activeTab === 'templates' && (
        <>
          {templates.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
              Нет доступных шаблонов отчетов
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates.map((template) => (
            <div key={template.id} className="border rounded-lg p-4 shadow-md">
              <h3 className="text-lg font-semibold mb-2">{template.name}</h3>
              <p className="text-sm text-gray-600 mb-4">{template.description || '-'}</p>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-semibold">Тип:</span> {template.report_type}
                </div>
                <div>
                  <span className="font-semibold">Формат:</span> {template.format}
                </div>
                <div>
                  <span className="font-semibold">Расписание:</span> {template.schedule}
                </div>
                <div>
                  <span className={`px-2 py-1 rounded ${
                    template.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {template.is_public ? 'Публичный' : 'Приватный'}
                  </span>
                </div>
              </div>
              <button className="mt-4 w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Создать отчет
              </button>
            </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

