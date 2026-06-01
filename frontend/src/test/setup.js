import "@testing-library/jest-dom";

// jsdom does not implement matchMedia / ResizeObserver used by some libs.
global.matchMedia =
  global.matchMedia ||
  function () {
    return { matches: false, addListener() {}, removeListener() {} };
  };

class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserver;
