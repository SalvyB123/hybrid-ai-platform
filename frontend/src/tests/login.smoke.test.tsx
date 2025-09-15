// src/tests/login.smoke.test.tsx
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import Login from "@/pages/Login";

// A super simple dashboard stub we can assert against
function DashboardStub() {
    return <h1>Dashboard</h1>;
}

describe("Login smoke test", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it("logs in with dummy JWT and redirects to /dashboard", async () => {
        const user = userEvent.setup();

        render(
            <MemoryRouter initialEntries={["/login"]}>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/dashboard" element={<DashboardStub />} />
                </Routes>
            </MemoryRouter>,
        );

        // Fill in the form
        await user.type(screen.getByLabelText(/email/i), "test@example.com");
        await user.type(screen.getByLabelText(/password/i), "password123");

        // Submit (button text is "Sign in" in your component)
        await user.click(screen.getByRole("button", { name: /sign in/i }));

        // Assert token persisted
        expect(localStorage.getItem("jwt")).toBe("dummy-jwt");

        // Assert redirect by checking the dashboard UI is rendered
        expect(
            await screen.findByRole("heading", { name: /dashboard/i }),
        ).toBeInTheDocument();
    });
});
