import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { productApi, dashboardApi } from "../../api/resources";
import { apiError } from "../../api/client";
import { EmptyState, Loading, Modal, Pagination } from "../../components/ui";
import useDebounce from "../../hooks/useDebounce";
import ProductForm from "./ProductForm";

export default function ProductList() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [order, setOrder] = useState("asc");
  const [inStock, setInStock] = useState("");
  const [modal, setModal] = useState(null); // { mode, product }
  const [submitting, setSubmitting] = useState(false);

  const debouncedSearch = useDebounce(search);

  const load = useCallback(() => {
    setLoading(true);
    const params = { page, page_size: 10, sort_by: sortBy, order };
    if (debouncedSearch) params.search = debouncedSearch;
    if (inStock !== "") params.in_stock = inStock;
    productApi
      .list(params)
      .then((res) => setData(res.data))
      .catch((e) => toast.error(apiError(e)))
      .finally(() => setLoading(false));
  }, [page, sortBy, order, debouncedSearch, inStock]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(values) {
    setSubmitting(true);
    const payload = {
      ...values,
      price: String(values.price),
      stock_quantity: Number(values.stock_quantity),
    };
    try {
      if (modal.mode === "edit") {
        await productApi.update(modal.product.id, payload);
        toast.success("Product updated");
      } else {
        await productApi.create(payload);
        toast.success("Product created");
      }
      setModal(null);
      load();
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(product) {
    if (!confirm(`Delete "${product.name}"?`)) return;
    try {
      await productApi.remove(product.id);
      toast.success("Product deleted");
      load();
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  async function handleExport() {
    try {
      const res = await dashboardApi.exportProducts();
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "products.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-bold">Products</h1>
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={handleExport}>
            Export CSV
          </button>
          <button
            className="btn-primary"
            onClick={() => setModal({ mode: "create", product: {} })}
          >
            + New Product
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          className="input max-w-xs"
          placeholder="Search by name or SKU..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
        />
        <select className="input max-w-[150px]" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="name">Sort: Name</option>
          <option value="price">Sort: Price</option>
          <option value="stock_quantity">Sort: Stock</option>
        </select>
        <select className="input max-w-[120px]" value={order} onChange={(e) => setOrder(e.target.value)}>
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
        <select
          className="input max-w-[160px]"
          value={inStock}
          onChange={(e) => {
            setPage(1);
            setInStock(e.target.value);
          }}
        >
          <option value="">All stock</option>
          <option value="true">In stock</option>
          <option value="false">Out of stock</option>
        </select>
      </div>

      {loading ? (
        <Loading />
      ) : data.items.length === 0 ? (
        <EmptyState message="No products yet." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-500 dark:bg-gray-700/50">
              <tr>
                <th className="px-4 py-3">SKU</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Stock</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p.id} className="border-t border-gray-100 dark:border-gray-700">
                  <td className="px-4 py-3 font-mono text-xs">{p.sku}</td>
                  <td className="px-4 py-3">{p.name}</td>
                  <td className="px-4 py-3 text-right">${Number(p.price).toFixed(2)}</td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`badge ${
                        p.stock_quantity > 0
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {p.stock_quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      className="text-brand-600 hover:underline"
                      onClick={() => setModal({ mode: "edit", product: p })}
                    >
                      Edit
                    </button>
                    <button
                      className="ml-3 text-red-600 hover:underline"
                      onClick={() => handleDelete(p)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={data.page} pages={data.pages} onChange={setPage} />

      <Modal
        open={!!modal}
        onClose={() => setModal(null)}
        title={modal?.mode === "edit" ? "Edit Product" : "New Product"}
      >
        {modal && (
          <ProductForm
            initial={modal.product}
            submitting={submitting}
            onSubmit={handleSubmit}
            onCancel={() => setModal(null)}
          />
        )}
      </Modal>
    </div>
  );
}
