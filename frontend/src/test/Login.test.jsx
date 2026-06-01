import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import Login from "../pages/Login";
import { AuthProvider } from "../context/AuthContext";

vi.mock("../api/resources", () => ({
  authApi: {
    login: vi.fn(() =>
      Promise.resolve({ data: { access_token: "a", refresh_token: "r" } })
    ),
    me: vi.fn(() =>
      Promise.resolve({ data: { id: "1", full_name: "T", email: "t@x.com", role: "user" } })
    ),
    register: vi.fn(),
  },
}));

function renderLogin() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Login page", () => {
  it("renders email and password fields", async () => {
    const { container } = renderLogin();
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Sign in" })).toBeInTheDocument()
    );
    expect(container.querySelector('input[type="email"]')).toBeInTheDocument();
    expect(container.querySelector('input[type="password"]')).toBeInTheDocument();
  });

  it("shows validation errors when submitting empty form", async () => {
    renderLogin();
    await waitFor(() => screen.getByRole("heading", { name: "Sign in" }));
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
  });
});
