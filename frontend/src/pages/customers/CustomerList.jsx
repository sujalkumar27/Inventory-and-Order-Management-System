import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { customerApi } from "../../api/resources";
import { apiError } from "../../api/client";
import { EmptyState, Loading, Modal, Pagination } from "../../components/ui";
import useDebounce from "../../hooks/useDebounce";
import CustomerForm from "./CustomerForm";

export default function CustomerList() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const debouncedSearch = useDebounce(search);

  const load = useCallback(() => {
    setLoading(true);
    const params = { page, page_size: 10 };
    if (debouncedSearch) params.search = debouncedSearch;
    customerApi
      .list(params)
      .then((res) => setData(res.data))
      .catch((e) => toast.error(apiError(e)))
      .finally(() => setLoading(false));
  }, [page, debouncedSearch]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(values) {
    setSubmitting(true);
    try {
      if (modal.mode === "edit") {
        await customerApi.update(modal.customer.id, values);
        toast.success("Customer updated");
      } else {
        await customerApi.create(values);
        toast.success("Customer created");
      }
      setModal(null);
      load();
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(customer) {
    if (!confirm(`Delete ${customer.first_name} ${customer.last_name}?`)) return;
    try {
      await customerApi.remove(customer.id);
      toast.success("Customer deleted");
      load();
    } catch (e) {
      toast.error(apiError(e));
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-bold">Customers</h1>
        <button
          className="btn-primary"
          onClick={() => setModal({ mode: "create", customer: {} })}
        >
          + New Customer
        </button>
      </div>

      <input
        className="input max-w-xs"
        placeholder="Search by name or email..."
        value={search}
        onChange={(e) => {
          setPage(1);
          setSearch(e.target.value);
        }}
      />

      {loading ? (
        <Loading />
      ) : data.items.length === 0 ? (
        <EmptyState message="No customers yet." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-500 dark:bg-gray-700/50">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Phone</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((c) => (
                <tr key={c.id} className="border-t border-gray-100 dark:border-gray-700">
                  <td className="px-4 py-3">
                    {c.first_name} {c.last_name}
                  </td>
                  <td className="px-4 py-3">{c.email}</td>
                  <td className="px-4 py-3">{c.phone || "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      className="text-brand-600 hover:underline"
                      onClick={() => setModal({ mode: "edit", customer: c })}
                    >
                      Edit
                    </button>
                    <button
                      className="ml-3 text-red-600 hover:underline"
                      onClick={() => handleDelete(c)}
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
        title={modal?.mode === "edit" ? "Edit Customer" : "New Customer"}
      >
        {modal && (
          <CustomerForm
            initial={modal.customer}
            submitting={submitting}
            onSubmit={handleSubmit}
            onCancel={() => setModal(null)}
          />
        )}
      </Modal>
    </div>
  );
}
