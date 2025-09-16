// frontend/cypress/e2e/dashboard.cy.ts
describe("Dashboard", () => {
    it("shows sentiment dashboard after login", () => {
        cy.visit("/login");
        cy.get("#email").type("user@example.com");
        cy.get("#password").type("password");
        cy.contains("button", /sign in/i).click();

        cy.location("pathname", { timeout: 10000 }).should(
            "contain",
            "/dashboard",
        );
        cy.contains(/Sentiment Dashboard/i).should("be.visible");

        // Either chart or cards visible
        cy.contains(/Total/i).should("be.visible");
    });
});
