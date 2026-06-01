import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { customerApi, orderApi, productApi } from "../../api/resources";
import { apiError } from "../../api/client";
import { Loading, StatusBadge } from "../../components/ui";

const STATUSES = ["pending", "processing", "completed", "cancelled"];

export default function OrderDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const { data } = await orderApi.get(id);
      setOrder(data);
      const cust = await customerApi.get(data.customer_id).catch(() => null);
      setCustomer(cust?.data || null);
      const entries = await Promise.all(
        data.items.map((it) =>
          productApi
            .get(it.product_id)
            .then((r) => [it.product_id, r.data])
            .catch(() => [it.product_id, null])
        )
      );
      setProducts(Object.fromEntries(entries));
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function changeStatus(status) {
    setUpdating(true);
    try {
      const { data } = await orderApi.updateStatus(id, status);
      setOrder(data);
      toast.success(`Status updated to ${status}`);
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setUpdating(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this order? Stock will be restored.")) return;
    try {
      await orderApi.remove(id);
      toast.success("Order deleted");
      navigate("/orders");
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  if (loading) return <Loading />;
  if (!order) return null;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Order Details</h1>
        <button className="btn-danger" onClick={handleDelete}>
          Delete
        </button>
      </div>

      <div className="card space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-500">Order ID</span>
          <span className="font-mono text-sm">{order.id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Customer</span>
          <span>
            {customer
              ? `${customer.first_name} ${customer.last_name}`
              : order.customer_id}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Date</span>
          <span>{new Date(order.order_date).toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Status</span>
          <StatusBadge status={order.status} />
        </div>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-500 dark:bg-gray-700/50">
            <tr>
              <th className="px-4 py-3">Product</th>
              <th className="px-4 py-3 text-right">Unit Price</th>
              <th className="px-4 py-3 text-right">Qty</th>
              <th className="px-4 py-3 text-right">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map((it) => (
              <tr key={it.id} className="border-t border-gray-100 dark:border-gray-700">
                <td className="px-4 py-3">
                  {products[it.product_id]?.name || it.product_id.slice(0, 8)}
                </td>
                <td className="px-4 py-3 text-right">${Number(it.unit_price).toFixed(2)}</td>
                <td className="px-4 py-3 text-right">{it.quantity}</td>
                <td className="px-4 py-3 text-right">
                  ${(Number(it.unit_price) * it.quantity).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t border-gray-200 font-semibold dark:border-gray-600">
              <td className="px-4 py-3" colSpan={3}>
                Total
              </td>
              <td className="px-4 py-3 text-right">
                ${Number(order.total_amount).toFixed(2)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div className="card">
        <label className="label">Update status</label>
        <div className="flex flex-wrap gap-2">
          {STATUSES.map((s) => (
            <button
              key={s}
              disabled={updating || order.status === s}
              onClick={() => changeStatus(s)}
              className={order.status === s ? "btn-primary" : "btn-secondary"}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
