import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { customerApi, orderApi, productApi } from "../../api/resources";
import { apiError } from "../../api/client";
import { Loading } from "../../components/ui";

export default function OrderCreate() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [customerId, setCustomerId] = useState("");
  const [lines, setLines] = useState([{ product_id: "", quantity: 1 }]);

  useEffect(() => {
    Promise.all([
      customerApi.list({ page_size: 100 }),
      productApi.list({ page_size: 100, in_stock: true }),
    ])
      .then(([c, p]) => {
        setCustomers(c.data.items);
        setProducts(p.data.items);
      })
      .catch((e) => toast.error(apiError(e)))
      .finally(() => setLoading(false));
  }, []);

  const productMap = Object.fromEntries(products.map((p) => [p.id, p]));

  const total = lines.reduce((sum, l) => {
    const p = productMap[l.product_id];
    return sum + (p ? Number(p.price) * Number(l.quantity || 0) : 0);
  }, 0);

  function updateLine(index, patch) {
    setLines((prev) => prev.map((l, i) => (i === index ? { ...l, ...patch } : l)));
  }
  function addLine() {
    setLines((prev) => [...prev, { product_id: "", quantity: 1 }]);
  }
  function removeLine(index) {
    setLines((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!customerId) return toast.error("Select a customer");
    const items = lines
      .filter((l) => l.product_id && Number(l.quantity) > 0)
      .map((l) => ({ product_id: l.product_id, quantity: Number(l.quantity) }));
    if (items.length === 0) return toast.error("Add at least one product");

    setSubmitting(true);
    try {
      const { data } = await orderApi.create({ customer_id: customerId, items });
      toast.success("Order created");
      navigate(`/orders/${data.id}`);
    } catch (e) {
      toast.error(apiError(e, "Could not create order"));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Loading />;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-bold">New Order</h1>
      <form onSubmit={handleSubmit} className="card space-y-5">
        <div>
          <label className="label">Customer</label>
          <select
            className="input"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
          >
            <option value="">Select a customer…</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.first_name} {c.last_name} ({c.email})
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-3">
          <label className="label">Items</label>
          {lines.map((line, i) => {
            const p = productMap[line.product_id];
            return (
              <div key={i} className="flex items-end gap-2">
                <div className="flex-1">
                  <select
                    className="input"
                    value={line.product_id}
                    onChange={(e) => updateLine(i, { product_id: e.target.value })}
                  >
                    <option value="">Select product…</option>
                    {products.map((prod) => (
                      <option key={prod.id} value={prod.id}>
                        {prod.name} — ${Number(prod.price).toFixed(2)} (stock {prod.stock_quantity})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="w-24">
                  <input
                    className="input"
                    type="number"
                    min="1"
                    max={p?.stock_quantity || undefined}
                    value={line.quantity}
                    onChange={(e) => updateLine(i, { quantity: e.target.value })}
                  />
                </div>
                <button
                  type="button"
                  className="btn-danger"
                  onClick={() => removeLine(i)}
                  disabled={lines.length === 1}
                >
                  ✕
                </button>
              </div>
            );
          })}
          <button type="button" className="btn-secondary" onClick={addLine}>
            + Add item
          </button>
        </div>

        <div className="flex items-center justify-between border-t border-gray-100 pt-4 dark:border-gray-700">
          <span className="text-lg font-semibold">Total: ${total.toFixed(2)}</span>
          <button className="btn-primary" disabled={submitting}>
            {submitting ? "Creating..." : "Create Order"}
          </button>
        </div>
      </form>
    </div>
  );
}
