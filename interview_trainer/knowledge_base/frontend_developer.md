# Frontend Developer Interview Knowledge Base
# Role: Frontend Developer | Category: Technical

---
## Q1 | difficulty: beginner
**Question:** What is the difference between `var`, `let`, and `const` in JavaScript?

**Answer:**
- `var`: function-scoped, hoisted (declared at top of function with `undefined`), can be re-declared. Avoid in modern JS.
- `let`: block-scoped, hoisted but in Temporal Dead Zone (TDZ), cannot be re-declared in same scope.
- `const`: block-scoped, must be initialised, cannot be reassigned (but objects/arrays it points to are mutable).
Best practice: default to `const`; use `let` when reassignment is needed; avoid `var`.

---
## Q2 | difficulty: intermediate
**Question:** Explain event loop and asynchronous JavaScript.

**Answer:**
JavaScript is single-threaded. The event loop enables async behaviour without blocking.
Components: Call Stack, Heap, Task Queue (macrotasks: setTimeout, setInterval), Microtask Queue (Promises, queueMicrotask).
Execution order: synchronous code → microtasks (drain completely) → one macrotask → microtasks again.
`async/await` is syntactic sugar over Promises. `await` pauses execution of the async function, not the entire thread. Errors caught with try/catch around await.
Common pitfall: `await` inside `forEach` doesn't work as expected; use `for...of` or `Promise.all()`.

---
## Q3 | difficulty: intermediate
**Question:** What is React's virtual DOM and reconciliation?

**Answer:**
React maintains a lightweight in-memory representation (virtual DOM) of the real DOM. On state change, React re-renders the component tree in the virtual DOM, diffs it against the previous version (reconciliation), and applies only the minimal set of real DOM updates (patching).
Keys help React identify which list items changed/moved — always use stable, unique keys (not array index for dynamic lists).
React 18 Concurrent Mode: renders can be interrupted and resumed, enabling features like Suspense, startTransition, and useTransition for non-blocking updates.

---
## Q4 | difficulty: intermediate
**Question:** What are React hooks? Explain useState, useEffect, useCallback, useMemo.

**Answer:**
Hooks let functional components use state and lifecycle features.
- `useState(initial)` → `[value, setter]`: local state.
- `useEffect(fn, deps)`: side effects after render. Empty deps `[]` = mount only; no deps = every render; specific deps = when deps change. Return cleanup function for subscriptions/timers.
- `useCallback(fn, deps)`: memoises a function reference. Avoids child re-renders when passing callbacks as props.
- `useMemo(fn, deps)`: memoises a computed value. Use for expensive calculations.
Rules: call only at top level, not inside conditions or loops; call only in React functions.

---
## Q5 | difficulty: advanced
**Question:** What is CSS specificity and how does the cascade work?

**Answer:**
Specificity determines which CSS rule applies when multiple rules target the same element. Calculated as a (a, b, c) tuple:
- `a`: inline styles (1, 0, 0)
- `b`: IDs (0, 1, 0)
- `c`: classes, attributes, pseudo-classes (0, 0, 1)
Elements and pseudo-elements: (0, 0, 0) but count as 1 in c column.
Higher specificity wins; equal specificity — last rule wins (cascade order).
`!important` overrides all — use sparingly.
CSS custom properties (variables) and `calc()` enable dynamic styling without JS.

---
## Q6 | difficulty: intermediate
**Question:** What is responsive web design? Explain Flexbox vs CSS Grid.

**Answer:**
Responsive design adapts layout to different screen sizes using fluid grids, flexible images, and media queries.
**Flexbox:** 1D layout (row or column). Best for component-level layouts (nav bars, card rows, form inputs). `display: flex` + `justify-content` + `align-items`.
**CSS Grid:** 2D layout (rows AND columns). Best for page-level layouts. `display: grid` + `grid-template-columns` + `grid-template-rows`.
**Media queries:** `@media (max-width: 768px) { ... }` — apply styles at breakpoints. Mobile-first approach: default styles for mobile, add complexity for larger screens.

---
## Q7 | difficulty: advanced
**Question:** What is TypeScript and what are its main benefits?

**Answer:**
TypeScript is a statically typed superset of JavaScript that compiles to JS. Adds:
- Static type checking: catch type errors at compile time.
- Interfaces and types: define shapes for objects, function signatures, generics.
- Enums, decorators, access modifiers (for OOP patterns).
Benefits: better IDE autocomplete and refactoring, self-documenting code, catches bugs early in large codebases, improved team collaboration via explicit contracts.
Common patterns: `interface` for object shapes, `type` for unions/intersections, `generic types` `<T>` for reusable components, `Partial<T>`, `Required<T>`, `Readonly<T>` utility types.

---
## Q8 | difficulty: intermediate
**Question:** Explain the concept of web accessibility (WCAG).

**Answer:**
Web accessibility ensures websites are usable by people with disabilities. WCAG 2.1 defines four principles (POUR):
- **Perceivable:** content available to all senses (alt text for images, captions for video, sufficient colour contrast ≥ 4.5:1 for normal text).
- **Operable:** navigable by keyboard (tab order), no keyboard traps, focus visible, skip navigation links.
- **Understandable:** clear language, consistent navigation, helpful error messages, form labels.
- **Robust:** works with assistive technologies (screen readers). Use semantic HTML (`<nav>`, `<main>`, `<button>`) and ARIA attributes appropriately.
Testing: axe, Lighthouse, NVDA/VoiceOver screen readers.

---
## Q9 | difficulty: advanced
**Question:** What is server-side rendering (SSR) vs client-side rendering (CSR) vs static site generation (SSG)?

**Answer:**
- **CSR:** browser downloads minimal HTML + JS bundle; JS renders the page client-side. Fast navigation after initial load but slow first paint; poor SEO.
- **SSR:** server renders full HTML per request; faster first paint, better SEO; higher server load; Next.js `getServerSideProps`.
- **SSG:** pages generated at build time as static HTML. Fastest delivery (CDN); best for content that doesn't change often. Next.js `getStaticProps`.
- **ISR (Incremental Static Regeneration):** SSG + revalidate on a schedule without full rebuild. Next.js feature.
- **Hydration:** SSR sends HTML, then JS "attaches" event handlers (hydration). React 18 selective hydration reduces blocking.

---
## Q10 | difficulty: intermediate
**Question:** What are common performance optimisation techniques for frontend applications?

**Answer:**
1. **Code splitting:** `React.lazy` + `Suspense`; split by route so users only download what they need.
2. **Tree shaking:** bundle only used exports (ESM + Webpack/Vite).
3. **Image optimisation:** responsive images (`srcset`), modern formats (WebP/AVIF), lazy loading (`loading="lazy"`).
4. **Caching:** HTTP cache headers (`Cache-Control`), service workers (PWA), CDN for static assets.
5. **Reduce render cycles:** `React.memo`, `useMemo`, `useCallback` to prevent unnecessary re-renders.
6. **Virtualise long lists:** `react-window` or `react-virtual` — render only visible rows.
7. **Critical CSS:** inline above-the-fold CSS; defer non-critical CSS.
8. **Measure first:** Lighthouse, Web Vitals (LCP, FID/INP, CLS) before optimising.

---
## Q11 | difficulty: advanced
**Question:** What is state management? When to use Context vs Redux vs Zustand?

**Answer:**
State management handles shared application state across components.
- **Local state** (`useState`): simplest; use for component-specific state.
- **Context API:** good for low-frequency updates (theme, auth, locale); creates re-renders for all consumers on every change.
- **Redux (+ RTK):** centralised store, predictable updates via reducers/actions, devtools time-travel debugging. Use for complex state logic with many interactions, or large teams needing clear conventions.
- **Zustand:** lightweight (600 bytes), simple API, selective subscriptions (no unnecessary re-renders), no boilerplate. Good middle ground for medium apps.
- **React Query / SWR:** specialised for server state (fetching, caching, synchronisation). Removes most need for Redux in data-fetching scenarios.
Rule of thumb: server state → React Query; UI state → Zustand; forms → React Hook Form.

---
## Q12 | difficulty: intermediate
**Question:** What are Web APIs? Explain fetch API and XMLHttpRequest.

**Answer:**
Web APIs are interfaces provided by browsers: DOM, Fetch, LocalStorage, IndexedDB, WebSockets, Web Workers, etc.
**Fetch API** (modern): Promise-based, cleaner syntax.
```javascript
const res = await fetch('/api/data', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
const json = await res.json();
```
Note: `fetch` only rejects on network errors, not HTTP error status codes — always check `res.ok`.
**XMLHttpRequest (XHR):** older, callback-based. Still used via Axios (which abstracts both).
Interceptors (Axios): middleware for request/response transformation, auth headers, error handling.

---
## Q13 | difficulty: advanced
**Question:** What is a service worker and how does it enable Progressive Web Apps?

**Answer:**
A service worker is a JS script running in the background (separate thread) that intercepts network requests, enabling:
- **Offline support:** cache-first or stale-while-revalidate strategies via Cache API.
- **Push notifications:** receive push events even when app is closed.
- **Background sync:** defer actions until connectivity is restored.
- **PWA features:** installability (web app manifest), splash screen, standalone mode.
```javascript
// sw.js
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
```
Lifecycle: install → activate → idle/fetch. Update requires new SW version + `skipWaiting()` + `clients.claim()`.

---
## Q14 | difficulty: intermediate
**Question:** How does the browser render a web page (critical rendering path)?

**Answer:**
1. **DNS lookup + TCP connection + TLS handshake**
2. **HTML parsing → DOM construction**
3. **CSS parsing → CSSOM construction**
4. **Render tree construction** (DOM + CSSOM; excludes `display:none` elements)
5. **Layout (Reflow):** calculate geometry of each element
6. **Paint:** fill in pixels (colour, borders, shadows)
7. **Composite:** layer composition via GPU

Performance optimisations:
- Reduce render-blocking CSS/JS (defer/async scripts, preload critical resources).
- Minimise layout thrashing (batch DOM reads/writes).
- Use `will-change: transform` to promote animations to compositor thread.
- Key metrics: FCP (First Contentful Paint), LCP (Largest Contentful Paint), CLS (Cumulative Layout Shift).

---
## Q15 | difficulty: advanced
**Question:** What is CORS and how do you handle it?

**Answer:**
CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts HTTP requests to different origins (protocol + domain + port).
**Preflight request:** browser sends OPTIONS request for non-simple cross-origin requests; server must respond with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`.
Server configuration (Express):
```javascript
app.use(cors({ origin: 'https://myapp.com', methods: ['GET', 'POST'] }));
```
**CORS errors happen in the browser, not the server.** The server can still process the request; the browser blocks the response.
Development workaround: proxy in Vite/Webpack config; production fix: server-side CORS headers.
Security note: `Access-Control-Allow-Origin: *` is unsafe for authenticated endpoints.

---
## Q16 | difficulty: intermediate
**Question:** Explain the difference between authentication and authorisation. JWT?

**Answer:**
- **Authentication:** "Who are you?" Verify identity (login with username/password, OAuth, SSO).
- **Authorisation:** "What can you do?" Check permissions after authentication.
**JWT (JSON Web Token):** compact, self-contained token with header.payload.signature.
- Header: algorithm (HS256, RS256).
- Payload: claims (user ID, roles, expiry).
- Signature: HMAC or RSA signature to verify integrity.
Storage: `localStorage` (XSS risk) vs `httpOnly` cookie (CSRF risk, mitigated with SameSite + CSRF token).
Token refresh: short-lived access tokens (15min) + long-lived refresh tokens (stored securely). Refresh token rotation (invalidate on use) prevents replay attacks.

---
## Q17 | difficulty: beginner
**Question:** What is semantic HTML and why does it matter?

**Answer:**
Semantic HTML uses elements that carry meaning about their content: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`, `<figure>`, `<button>`, `<form>`.
Benefits:
- **Accessibility:** screen readers use semantic structure to navigate.
- **SEO:** search engines understand page structure and content hierarchy.
- **Maintainability:** self-documenting code; `<button>` vs `<div onclick>` makes intent clear.
- **Default behaviour:** `<button>` is keyboard-accessible, `<a href>` is focusable and navigable by default.
Bad practice: `<div class="nav">` instead of `<nav>`, `<span class="h1">` instead of `<h1>`.

---
## Q18 | difficulty: advanced
**Question:** What are micro-frontends and when would you use them?

**Answer:**
Micro-frontends apply microservices thinking to the frontend: decompose a large SPA into independently deployable, team-owned frontend modules.
Approaches:
- **Build-time integration:** publish packages to npm; compose in a container app. Simple but requires coordinated releases.
- **Server-side composition:** server assembles fragments from different services (ESI).
- **Runtime integration (Module Federation):** Webpack 5 Module Federation allows runtime sharing of React components across separately deployed apps. Each micro-frontend can be deployed independently.
When to use: multiple teams working on a large application, teams with different release cadences, different tech stacks per domain.
Trade-offs: added complexity (shared state, routing, auth), potential for dependency duplication, coordination overhead. Only justified for large, multi-team products.

---
## Q19 | difficulty: intermediate
**Question:** What is Next.js and its key features?

**Answer:**
Next.js is a React framework for production with built-in SSR, SSG, and ISR.
Key features:
- **File-system routing:** `pages/about.js` → `/about`; `app/` directory with React Server Components (Next 13+).
- **API routes:** `pages/api/*.js` → serverless functions.
- **Image Optimisation:** `next/image` auto-resizes, converts to WebP, lazy loads.
- **Font Optimisation:** `next/font` inlines fonts, eliminates layout shift.
- **React Server Components (RSC):** components render on server; zero JS shipped to client; enables async server-side data fetching in components.
- **Edge Runtime:** middleware can run at the CDN edge for low-latency personalisation.
Deployment: Vercel (first-party), self-hosted with Docker.

---
## Q20 | difficulty: advanced
**Question:** How do you test frontend applications? Unit, integration, E2E?

**Answer:**
Testing pyramid for frontend:
- **Unit tests (Jest + RTL):** test individual functions and React components in isolation. Mock external deps.
  ```javascript
  render(<Button onClick={mockFn} label="Submit" />);
  fireEvent.click(screen.getByText('Submit'));
  expect(mockFn).toHaveBeenCalledOnce();
  ```
- **Integration tests (React Testing Library):** test component interactions, data flow. Don't test implementation details (use screen queries, not component state).
- **E2E tests (Playwright/Cypress):** test complete user flows in a real browser. Slower but highest confidence.
Testing best practices: test behaviour, not implementation; avoid testing library internals; mock network with MSW (Mock Service Worker); co-locate tests with components.

---
## Q21 | difficulty: intermediate
**Question:** What are web security best practices for frontend?

**Answer:**
Common attacks and defences:
- **XSS (Cross-Site Scripting):** never use `dangerouslySetInnerHTML` with user content; React auto-escapes JSX; Content Security Policy (CSP) header.
- **CSRF (Cross-Site Request Forgery):** use SameSite cookie attribute; CSRF tokens for state-changing requests.
- **Clickjacking:** `X-Frame-Options: DENY` or `frame-ancestors 'none'` in CSP.
- **Sensitive data exposure:** never store tokens or PII in localStorage; use httpOnly cookies; HTTPS everywhere.
- **Dependency vulnerabilities:** `npm audit` regularly; Dependabot; lock file version pinning.
- **Subresource Integrity (SRI):** `integrity` attribute on third-party scripts/stylesheets.

---
## Q22 | difficulty: beginner
**Question:** What is the difference between `null`, `undefined`, and `NaN` in JavaScript?

**Answer:**
- `undefined`: variable declared but not assigned; missing function parameter; accessing non-existent property.
- `null`: intentional absence of value — explicitly assigned. `typeof null === 'object'` (historical bug in JS).
- `NaN` (Not a Number): result of invalid numeric operation (`"hello" * 2`, `parseInt("abc")`). `NaN !== NaN` (use `Number.isNaN()` to check).
Type coercion gotchas: `null == undefined` (true); `null === undefined` (false); `0 == false` (true); `0 === false` (false).
Best practices: prefer `===` (strict equality) over `==`; use `??` (nullish coalescing) for null/undefined defaults; use `?.` (optional chaining) for safe property access.

---
## Q23 | difficulty: advanced
**Question:** Explain closures in JavaScript with examples.

**Answer:**
A closure is a function that "closes over" variables from its outer (lexical) scope, maintaining access to them even after the outer function has returned.
```javascript
function makeCounter() {
    let count = 0;               // count is "enclosed"
    return {
        increment: () => ++count,
        decrement: () => --count,
        value: () => count
    };
}
const c = makeCounter();
c.increment(); c.increment();
console.log(c.value()); // 2 — count is private!
```
Use cases: data privacy (module pattern), currying, memoisation, event handlers with state, React useState (closure over stale state — common gotcha).
Common bug: loop closures with `var` → use `let` or closure factory.

---
## Q24 | difficulty: intermediate
**Question:** What is the prototype chain in JavaScript?

**Answer:**
JavaScript uses prototypal inheritance. Every object has a hidden `[[Prototype]]` link (accessible as `__proto__` or via `Object.getPrototypeOf()`).
When accessing a property, JS looks: own properties → `[[Prototype]]` → `[[Prototype]]`'s `[[Prototype]]` → ... → `Object.prototype` → null.
`class` syntax in ES6+ is syntactic sugar over prototypes.
```javascript
class Animal { speak() { return 'sound'; } }
class Dog extends Animal { speak() { return 'woof'; } }
const d = new Dog();
d.speak(); // 'woof' (own method)
Object.getPrototypeOf(d) === Dog.prototype; // true
```
`instanceof` checks the prototype chain. `Object.create(proto)` creates object with specified prototype.

---
## Q25 | difficulty: advanced
**Question:** What are design patterns commonly used in frontend development?

**Answer:**
- **Module pattern:** use ES modules or IIFE to encapsulate private state. Standard in modern JS with `import/export`.
- **Observer / PubSub:** emit/subscribe to events. Used in state management, event systems.
- **Factory:** functions that create objects. `createStore()`, `renderComponent()`.
- **Singleton:** one instance (e.g., app config, logger).
- **Higher-Order Components (HOC):** function that takes a component and returns enhanced component (auth guards, analytics).
- **Render props:** component accepts a function prop to render dynamic content.
- **Container/Presentational split:** container (data fetching, state) + presentational (pure UI) separation — less common since hooks.
- **Compound components:** `<Tabs>`, `<Tab>`, `<TabPanel>` sharing implicit state via Context. Used in design systems.

---
## Q26 | difficulty: intermediate
**Question:** How do you optimise the performance of a React application?

**Answer:**
1. **Avoid unnecessary re-renders:** `React.memo` for pure components; `useMemo`/`useCallback` for stable references; move state down to where it's needed.
2. **Lazy loading routes and components:** `React.lazy(() => import('./Component'))` + `<Suspense>`.
3. **Virtualise long lists:** `react-window` renders only visible items.
4. **Optimise context:** split contexts by update frequency; use selector libraries (Zustand, Jotai) for granular subscriptions.
5. **Profile first:** React DevTools Profiler identifies which components re-render and why. Never optimise without profiling — premature optimisation introduces complexity.
6. **Web Workers:** offload CPU-intensive computation off the main thread.
7. **React 18 concurrent features:** `useTransition` marks updates as non-urgent; `useDeferredValue` for debouncing.

---
## Q27 | difficulty: beginner
**Question:** What is the Box Model in CSS?

**Answer:**
Every HTML element is a rectangular box. The CSS box model defines the space taken up:
- **Content:** actual content area (text, image).
- **Padding:** space between content and border (inside the border).
- **Border:** the visible outline around the element.
- **Margin:** space outside the border (between elements).
`box-sizing: border-box` (recommended, set globally): width/height includes padding and border — more intuitive sizing. Default `content-box` excludes padding and border from width calculation.
`margin: auto` centres block elements horizontally. Margin collapsing: adjacent vertical margins of block elements collapse into the larger value.

---
## Q28 | difficulty: advanced
**Question:** What are React Server Components (RSC) in Next.js 13+?

**Answer:**
React Server Components render exclusively on the server — zero JavaScript sent to the client. They can:
- Directly `async/await` data (no useEffect needed).
- Access backend resources (DB, filesystem) directly.
- Keep large dependencies (markdown parsers, etc.) server-side.
Client Components (`'use client'` directive) retain interactivity (hooks, event handlers) — sent to client as JS.
Pattern: Server Components as the default for data fetching and layout; wrap only interactive parts in Client Components.
```jsx
// page.tsx (Server Component, implicit)
export default async function Page() {
  const data = await fetchFromDB();     // direct DB call, no API needed
  return <ClientChart data={data} />;   // pass serialisable data to client
}
```
Benefits: smaller JS bundles, faster LCP, improved SEO, simpler data fetching.

---
## Q29 | difficulty: intermediate
**Question:** What is GraphQL and how does it compare to REST?

**Answer:**
GraphQL is a query language and runtime for APIs that allows clients to request exactly the data they need.
Key differences from REST:
| Feature | REST | GraphQL |
|---|---|---|
| Endpoint structure | Multiple (`/users`, `/posts`) | Single endpoint (`/graphql`) |
| Over/under-fetching | Common | Eliminated — request exact fields |
| Versioning | URL-based (`/v2/`) | Evolve schema additively |
| Tooling | Postman, curl | GraphiQL, Apollo Studio |
| N+1 problem | Less common | Common — use DataLoader |
Use GraphQL when: complex data relationships, multiple clients with different data needs (mobile vs web), rapid schema iteration.
Apollo Client (React) enables local state management alongside GraphQL data.

---
## Q30 | difficulty: advanced
**Question:** How would you architect a large-scale React application?

**Answer:**
Architectural considerations:
1. **Folder structure:** feature-based (`/features/auth`, `/features/products`) over type-based (`/components`, `/reducers`) for scalability.
2. **State management:** server state → React Query/SWR; client UI state → Zustand/Context; form state → React Hook Form.
3. **Component architecture:** Atomic Design (atoms → molecules → organisms → templates); design system as shared package.
4. **Data fetching layer:** centralised API client (Axios instance with interceptors); React Query for caching and synchronisation.
5. **Routing:** React Router v6 / Next.js app router; code-split by route.
6. **Error boundaries + fallback UI:** wrap top-level routes; structured error pages.
7. **Testing strategy:** unit (Jest+RTL), integration (RTL), E2E (Playwright) with coverage gates in CI.
8. **Performance budget:** Lighthouse CI in pipeline; bundle analyser; Web Vitals monitoring.
9. **Monorepo (large teams):** Nx or Turborepo for shared packages (UI, utils, API types) across apps.
