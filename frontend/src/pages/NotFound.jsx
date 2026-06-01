import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-5xl font-bold text-brand-600">404</h1>
      <p className="text-gray-500">Page not found.</p>
      <Link to="/" className="btn-primary">
        Go home
      </Link>
    </div>
  );
}
