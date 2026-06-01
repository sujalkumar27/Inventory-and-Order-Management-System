import { useForm } from "react-hook-form";

export default function CustomerForm({ initial, onSubmit, onCancel, submitting }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ defaultValues: initial });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">First name</label>
          <input className="input" {...register("first_name", { required: "Required" })} />
          {errors.first_name && (
            <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>
          )}
        </div>
        <div>
          <label className="label">Last name</label>
          <input className="input" {...register("last_name", { required: "Required" })} />
          {errors.last_name && (
            <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>
          )}
        </div>
      </div>
      <div>
        <label className="label">Email</label>
        <input
          className="input"
          type="email"
          {...register("email", { required: "Email is required" })}
        />
        {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
      </div>
      <div>
        <label className="label">Phone</label>
        <input className="input" {...register("phone")} />
      </div>
      <div>
        <label className="label">Address</label>
        <textarea className="input" rows={2} {...register("address")} />
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
