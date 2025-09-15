// frontend/cypress/e2e/login.cy.ts
describe("Login", () => {
  it("redirects unauthenticated to /login", () => {
    cy.clearAllLocalStorage();
    cy.visit("/dashboard");
    cy.location("pathname").should("eq", "/login");
  });

  it("logs in with dummy token and redirects to /dashboard", () => {
    cy.visit("/login");
    cy.get("#email").type("test@example.com");
    cy.get("#password").type("password123");
    cy.contains("button", /sign in/i).click();

    // Wait for navigation and then assert token presence
    cy.location("pathname", { timeout: 10000 }).should("contain", "/dashboard");
    cy.window().then((win) => {
      const token = win.localStorage.getItem("auth_token");
      expect(token, "auth token should be set in localStorage").to.be.a("string");
      expect(token).to.have.length.greaterThan(0);
    });
  });
});