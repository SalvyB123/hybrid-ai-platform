// frontend/cypress/e2e/dashboard.cy.ts
describe("Dashboard", () => {
    it("shows sentiment dashboard after login", () => {
        cy.visit("/dashboard", {
            onBeforeLoad(win) {
                // Pre-auth so ProtectedRoute lets us in
                win.localStorage.setItem("auth_token", "dummy-jwt");

                // Keep a reference to the native fetch
                const originalFetch = win.fetch.bind(win);

                // Type-safe stub: use Parameters/ReturnType of fetch
                cy.stub(win, "fetch")
                    .callsFake(
                        (
                            ...args: Parameters<typeof originalFetch>
                        ): ReturnType<typeof originalFetch> => {
                            const [input, init] = args;
                            const url =
                                typeof input === "string"
                                    ? input
                                    : input.toString();

                            if (url.includes("/sentiment/summary")) {
                                const body = JSON.stringify({
                                    positive: 3,
                                    negative: 1,
                                    neutral: 0,
                                    total: 4,
                                });
                                return Promise.resolve(
                                    new Response(body, {
                                        status: 200,
                                        headers: {
                                            "Content-Type": "application/json",
                                        },
                                    }),
                                ) as ReturnType<typeof originalFetch>;
                            }

                            return originalFetch(input, init);
                        },
                    )
                    .as("fetch");
            },
        });

        cy.location("pathname").should("contain", "/dashboard");
        cy.contains(/Sentiment Dashboard/i).should("be.visible");
        cy.contains(/Total/i).should("be.visible");
        cy.contains(/Positive/i).should("be.visible");
        cy.contains(/Negative/i).should("be.visible");
    });
});
