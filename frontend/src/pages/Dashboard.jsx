import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import toast from "react-hot-toast";
import { dashboardApi } from "../api/resources";
import { apiError } from "../api/client";
import { Loading } from "../components/ui";

function StatCard({ label, value }) {
  return (
    <div className="card">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-brand-600">{value}</p>
    </div>
  );
}

const BAR_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi
      .stats()
      .then((res) => setData(res.data))
      .catch((e) => toast.error(apiError(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (!data) return null;

  const { stats, monthly_orders, top_products, low_stock } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Products" value={stats.total_products} />
        <StatCard label="Total Customers" value={stats.total_customers} />
        <StatCard label="Total Orders" value={stats.total_orders} />
        <StatCard
          label="Total Revenue"
          value={`$${Number(stats.total_revenue).toLocaleString()}`}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-4 font-semibold">Monthly Orders</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthly_orders}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="orders" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="mb-4 font-semibold">Revenue Trend</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={monthly_orders}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="mb-4 font-semibold">Top Selling Products</h2>
          {top_products.length === 0 ? (
            <p className="text-sm text-gray-500">No sales yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={top_products} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="name" width={120} />
                <Tooltip />
                <Bar dataKey="units_sold" radius={[0, 4, 4, 0]}>
                  {top_products.map((_, i) => (
                    <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h2 className="mb-4 font-semibold">Low Stock Products</h2>
          {low_stock.length === 0 ? (
            <p className="text-sm text-gray-500">All products well stocked.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-gray-500">
                <tr>
                  <th className="pb-2">SKU</th>
                  <th className="pb-2">Name</th>
                  <th className="pb-2 text-right">Stock</th>
                </tr>
              </thead>
              <tbody>
                {low_stock.map((p) => (
                  <tr key={p.product_id} className="border-t border-gray-100 dark:border-gray-700">
                    <td className="py-2">{p.sku}</td>
                    <td className="py-2">{p.name}</td>
                    <td className="py-2 text-right">
                      <span className="badge bg-red-100 text-red-800">{p.stock_quantity}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
