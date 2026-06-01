import { useForm } from "react-hook-form";

export default function ProductForm({ initial, onSubmit, onCancel, submitting }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ defaultValues: initial });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="label">SKU</label>
        <input className="input" {...register("sku", { required: "SKU is required" })} />
        {errors.sku && <p className="mt-1 text-xs text-red-600">{errors.sku.message}</p>}
      </div>
      <div>
        <label className="label">Name</label>
        <input className="input" {...register("name", { required: "Name is required" })} />
        {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
      </div>
      <div>
        <label className="label">Description</label>
        <textarea className="input" rows={2} {...register("description")} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Price</label>
          <input
            className="input"
            type="number"
            step="0.01"
            {...register("price", {
              required: "Price is required",
              min: { value: 0, message: "Cannot be negative" },
            })}
          />
          {errors.price && <p className="mt-1 text-xs text-red-600">{errors.price.message}</p>}
        </div>
        <div>
          <label className="label">Stock quantity</label>
          <input
            className="input"
            type="number"
            {...register("stock_quantity", {
              required: "Stock is required",
              min: { value: 0, message: "Cannot be negative" },
            })}
          />
          {errors.stock_quantity && (
            <p className="mt-1 text-xs text-red-600">{errors.stock_quantity.message}</p>
          )}
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : "Save"}
        </button>
      </div>
    </form>
  );
}
