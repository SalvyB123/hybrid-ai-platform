// frontend/cypress/e2e/dashboard.cy.ts
describe("Dashboard", () => {
    it("shows sentiment dashboard after login", () => {
        // Robust intercept: any origin + optional querystring
        cy.intercept(
            { method: "GET", url: /\/sentiment\/summary(?:\?.*)?$/ },
            {
                statusCode: 200,
                body: { positive: 3, negative: 1, neutral: 0, total: 4 },
            },
        ).as("getSummary");

        cy.visit("/login");
        cy.get("#email").type("user@example.com");
        cy.get("#password").type("password");
        cy.contains("button", /sign in/i).click();

        cy.location("pathname", { timeout: 10000 }).should(
            "contain",
            "/dashboard",
        );

        // Allow a little extra time in CI
        cy.wait("@getSummary", { timeout: 10000 });

        cy.contains(/Sentiment Dashboard/i).should("be.visible");
        cy.contains(/Total/i).should("be.visible");
        cy.contains(/Positive/i).should("be.visible");
        cy.contains(/Negative/i).should("be.visible");
    });
});
