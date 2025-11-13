import { useEffect, useState } from 'react';
import { subscriptionService, Subscription, SubscriptionPlan } from '../services/subscriptionService';
import { factoryService } from '../services/factoryService';
import toast from 'react-hot-toast';

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [factories, setFactories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [subsRes, plansRes, factoriesRes] = await Promise.all([
        subscriptionService.getSubscriptions(),
        subscriptionService.getPlans(),
        factoryService.getFactories(),
      ]);
      setSubscriptions(subsRes?.items || []);
      setPlans(plansRes?.plans || []);
      setFactories(factoriesRes?.items || []);
    } catch (error: any) {
      // Устанавливаем пустые массивы при ошибке
      setSubscriptions([]);
      setPlans([]);
      setFactories([]);
      // Показываем ошибку только если это не 404
      if (error.response?.status !== 404) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const getFactoryName = (factoryId: string) => {
    const factory = factories.find(f => f.id === factoryId);
    return factory?.name || factoryId;
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('ru-KZ', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return <div className="p-6">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Подписки и тарифы</h1>

      {/* Тарифные планы */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">Доступные тарифы</h2>
        {plans.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
            Нет доступных тарифных планов
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => (
            <div key={plan.code} className="border rounded-lg p-6 shadow-md">
              <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
              <div className="text-3xl font-bold mb-4 text-blue-600">
                {formatPrice(plan.price, plan.currency)}
                <span className="text-sm text-gray-500">/мес</span>
              </div>
              <div className="mb-4">
                <span className="text-gray-600">
                  Оборудование: {plan.equipment_limit ? `до ${plan.equipment_limit}` : 'неограниченно'}
                </span>
              </div>
              <ul className="space-y-2 mb-4">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            ))}
          </div>
        )}
      </div>

      {/* Активные подписки */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">Активные подписки</h2>
        {subscriptions.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg">
            Нет активных подписок
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Завод</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Тариф</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Период</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Оборудование</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Стоимость</th>
                  <th className="px-4 py-3 text-left text-gray-700 dark:text-gray-300">Статус</th>
                </tr>
              </thead>
              <tbody>
                {subscriptions.map((sub) => (
                <tr key={sub.id} className="border-t">
                  <td className="px-4 py-3">{getFactoryName(sub.factory_id)}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                      {sub.plan}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {new Date(sub.start_date).toLocaleDateString('ru-RU')} -{' '}
                    {sub.end_date ? new Date(sub.end_date).toLocaleDateString('ru-RU') : '∞'}
                  </td>
                  <td className="px-4 py-3">
                    {sub.equipment_count} / {sub.equipment_limit || '∞'}
                  </td>
                  <td className="px-4 py-3">
                    {formatPrice(sub.monthly_price, sub.currency)}
                  </td>
                  <td className="px-4 py-3">
                    {sub.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded">Активна</span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">Неактивна</span>
                    )}
                    {sub.is_trial && (
                      <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                        Пробный период
                      </span>
                    )}
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

