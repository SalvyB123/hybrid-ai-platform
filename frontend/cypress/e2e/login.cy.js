// frontend/cypress/e2e/login.cy.ts
describe('Login', function () {
    it('logs in with dummy token and redirects to /dashboard', function () {
        cy.visit('/login');
        cy.findByLabelText(/email/i).type('test@example.com');
        cy.findByLabelText(/password/i).type('password123');
        cy.findByRole('button', { name: /sign in/i }).click();
        // expect instead of bare `.should` expression:
        cy.location('pathname').then(function (p) {
            expect(p).to.eq('/dashboard');
        });
        // Optional: assert token is in localStorage
        cy.window().then(function (w) {
            expect(w.localStorage.getItem('jwt')).to.match(/^dummy|eyJ/); // whatever your app sets
        });
    });
});
