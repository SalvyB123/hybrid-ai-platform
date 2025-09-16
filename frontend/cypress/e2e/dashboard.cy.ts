// frontend/cypress/e2e/dashboard.cy.ts
describe("Dashboard", () => {
    it("shows sentiment dashboard after login", () => {
        // Stub the backend summary call so test is deterministic
        cy.intercept("GET", "**/sentiment/summary", {
            statusCode: 200,
            body: { positive: 3, negative: 1, neutral: 0, total: 4 },
        }).as("getSummary");

        // Go through the login stub
        cy.visit("/login");
        cy.get("#email").type("user@example.com");
        cy.get("#password").type("password");
        cy.contains("button", /sign in/i).click();

        // We should land on /dashboard and the UI should request the summary
        cy.location("pathname", { timeout: 10000 }).should(
            "contain",
            "/dashboard",
        );
        cy.wait("@getSummary");

        // Assert visible content once data is loaded
        cy.contains(/Sentiment Dashboard/i).should("be.visible");
        cy.contains(/Total/i, { timeout: 10000 }).should("be.visible");
        cy.contains(/Positive/i).should("be.visible");
        cy.contains(/Negative/i).should("be.visible");
    });
});
