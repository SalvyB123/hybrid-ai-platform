// frontend/src/tests/setup.ts
import "@testing-library/jest-dom"

// Helpful if anything tries to read these before navigation occurs
// (jsdom provides them once a URL is set via environmentOptions above)
Object.defineProperty(window, "scrollTo", { value: () => {}, writable: true })