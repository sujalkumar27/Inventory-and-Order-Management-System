import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { orderApi } from "../../api/resources";
import { apiError } from "../../api/client";
import { EmptyState, Loading, Pagination, StatusBadge } from "../../components/ui";

const STATUSES = ["", "pending", "processing", "completed", "cancelled"];

export default function OrderList() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    const params = { page, page_size: 10 };
    if (status) params.status = status;
    orderApi
      .list(params)
      .then((res) => setData(res.data))
      .catch((e) => toast.error(apiError(e)))
      .finally(() => setLoading(false));
  }, [page, status]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-bold">Orders</h1>
        <Link to="/orders/new" className="btn-primary">
          + New Order
        </Link>
      </div>

      <select
        className="input max-w-[180px]"
        value={status}
        onChange={(e) => {
          setPage(1);
          setStatus(e.target.value);
        }}
      >
        {STATUSES.map((s) => (
          <option key={s} value={s}>
            {s ? s[0].toUpperCase() + s.slice(1) : "All statuses"}
          </option>
        ))}
      </select>

      {loading ? (
        <Loading />
      ) : data.items.length === 0 ? (
        <EmptyState message="No orders yet." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-500 dark:bg-gray-700/50">
              <tr>
                <th className="px-4 py-3">Order ID</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Items</th>
                <th className="px-4 py-3 text-right">Total</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((o) => (
                <tr key={o.id} className="border-t border-gray-100 dark:border-gray-700">
                  <td className="px-4 py-3 font-mono text-xs">{o.id.slice(0, 8)}</td>
                  <td className="px-4 py-3">
                    {new Date(o.order_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">{o.items.length}</td>
                  <td className="px-4 py-3 text-right">
                    ${Number(o.total_amount).toFixed(2)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={o.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link to={`/orders/${o.id}`} className="text-brand-600 hover:underline">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={data.page} pages={data.pages} onChange={setPage} />
    </div>
  );
}
