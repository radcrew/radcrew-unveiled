import "@testing-library/jest-dom";

// jsdom does not implement scrollIntoView; components that auto-scroll need it.
Element.prototype.scrollIntoView = () => {};

// jsdom does not implement IntersectionObserver; framer-motion's `whileInView`
// throws without it. Observing never reports an intersection, so elements stay
// in their initial variant, which is enough for DOM assertions.
class IntersectionObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() {
    return [];
  }
}
Object.defineProperty(window, "IntersectionObserver", {
  writable: true,
  value: IntersectionObserverStub,
});
Object.defineProperty(globalThis, "IntersectionObserver", {
  writable: true,
  value: IntersectionObserverStub,
});

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});
