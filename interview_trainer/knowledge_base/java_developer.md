# Java Developer Interview Knowledge Base
# Role: Java Developer | Category: Technical

---
## Q1 | difficulty: beginner
**Question:** What are the four pillars of Object-Oriented Programming in Java?

**Answer:**
The four pillars of OOP are:
1. **Encapsulation** – bundling data (fields) and behaviour (methods) together and hiding internal state via access modifiers (`private`, `protected`). Example: a `BankAccount` class exposes `deposit()` and `withdraw()` but keeps `balance` private.
2. **Abstraction** – exposing only essential features and hiding implementation details using abstract classes or interfaces.
3. **Inheritance** – a child class inherits fields and methods from a parent class (`extends` keyword), enabling code reuse. Java supports single inheritance for classes but multiple inheritance via interfaces.
4. **Polymorphism** – the same method name behaves differently based on the object (method overloading at compile time; method overriding at runtime via dynamic dispatch).

---
## Q2 | difficulty: beginner
**Question:** What is the difference between `==` and `.equals()` in Java?

**Answer:**
- `==` compares **references** (memory addresses). Two distinct `String` objects with the same content return `false` with `==`.
- `.equals()` compares **logical equality** (content). `String`, `Integer`, and other value types override `.equals()` to compare content.
- Best practice: always use `.equals()` for object comparison; use `==` only for primitives or intentional reference checks.
- Note: comparing with `null` via `.equals()` throws `NullPointerException`; use `Objects.equals(a, b)` for null-safe comparison.

---
## Q3 | difficulty: intermediate
**Question:** Explain Java memory model: stack vs heap.

**Answer:**
- **Heap** stores objects and class instances. Managed by the Garbage Collector (GC). Shared across threads.
- **Stack** stores primitive variables and method call frames. Each thread has its own stack. LIFO structure; auto-freed when method returns.
- **String pool** is a special area in the heap where string literals are interned to save memory.
- Memory leaks happen when objects are referenced but logically unused (e.g., static collections holding references).

---
## Q4 | difficulty: intermediate
**Question:** What is the Java Collections Framework? Compare ArrayList vs LinkedList.

**Answer:**
The Java Collections Framework (JCF) provides interfaces (`List`, `Set`, `Map`, `Queue`) and implementations for common data structures.

**ArrayList vs LinkedList:**
| Feature | ArrayList | LinkedList |
|---|---|---|
| Internal structure | Dynamic array | Doubly-linked list |
| Random access (get) | O(1) | O(n) |
| Insert/delete (middle) | O(n) – shifting | O(1) – pointer update |
| Memory overhead | Low | Higher (node pointers) |
| Cache locality | Good | Poor |

**When to use:** `ArrayList` for frequent reads; `LinkedList` for frequent insertions/deletions at ends or middle.

---
## Q5 | difficulty: intermediate
**Question:** What are Java Generics and why are they useful?

**Answer:**
Generics allow classes, interfaces, and methods to operate on typed parameters, enabling compile-time type safety and eliminating explicit casting.
```java
List<String> names = new ArrayList<>();
names.add("Alice");
String name = names.get(0); // No cast needed
```
Benefits: type safety, code reusability, no `ClassCastException` at runtime.
Type erasure: generic type info is erased at runtime; `List<String>` becomes `List` in bytecode.

---
## Q6 | difficulty: intermediate
**Question:** Explain multithreading in Java. What is the difference between `Thread` and `Runnable`?

**Answer:**
Java supports multithreading via `java.lang.Thread` and `java.util.concurrent` package.
- Extending `Thread` creates a subclass; implementing `Runnable` (or `Callable`) is preferred because Java allows only single inheritance.
- `ExecutorService` (thread pools) should be used in production instead of raw `Thread` creation for resource management.
- `synchronized` keyword ensures mutual exclusion on shared resources.
- `volatile` ensures visibility of variable changes across threads without locking.
- Modern alternative: `CompletableFuture` for async, non-blocking pipelines.

---
## Q7 | difficulty: intermediate
**Question:** What are Java 8 streams and lambda expressions?

**Answer:**
**Lambda expressions** are anonymous functions: `(params) -> expression`. They enable functional-style programming and implement `@FunctionalInterface`.
**Streams** provide a pipeline to process sequences of elements declaratively:
```java
List<Integer> evens = numbers.stream()
    .filter(n -> n % 2 == 0)
    .sorted()
    .collect(Collectors.toList());
```
Key operations:
- Intermediate (lazy): `filter`, `map`, `flatMap`, `distinct`, `sorted`
- Terminal (eager): `collect`, `forEach`, `reduce`, `count`, `findFirst`
Streams don't modify the source and can be parallelised with `.parallelStream()`.

---
## Q8 | difficulty: advanced
**Question:** Explain the SOLID principles with Java examples.

**Answer:**
- **S** – Single Responsibility: a class has one reason to change. `InvoiceCalculator` should not also handle PDF generation.
- **O** – Open/Closed: open for extension, closed for modification. Use interfaces/abstract classes; add behaviour via new implementations, not by modifying existing code.
- **L** – Liskov Substitution: subclasses must be substitutable for base classes without breaking behaviour.
- **I** – Interface Segregation: prefer small, specific interfaces over fat ones. Don't force clients to implement methods they don't need.
- **D** – Dependency Inversion: depend on abstractions, not concretions. Inject dependencies via constructor injection (IoC).

---
## Q9 | difficulty: advanced
**Question:** What is Spring Boot and how does auto-configuration work?

**Answer:**
Spring Boot is an opinionated framework built on Spring that eliminates boilerplate configuration.
- `@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`.
- **Auto-configuration** scans classpath for libraries (e.g., if H2 and Spring Data JPA are present, it auto-configures a DataSource and EntityManagerFactory).
- `spring.factories` / `AutoConfiguration.imports` lists auto-configuration classes that are conditionally applied via `@ConditionalOnClass`, `@ConditionalOnMissingBean`, etc.
- `application.properties` / `application.yml` externalises configuration.
- Actuator adds production-ready endpoints (`/actuator/health`, `/actuator/metrics`).

---
## Q10 | difficulty: advanced
**Question:** Explain JVM internals: class loading, JIT compilation, and GC algorithms.

**Answer:**
**Class Loading:** Bootstrap → Extension → Application classloaders (parent delegation model). Classes loaded once per classloader.
**JIT Compilation:** JVM interprets bytecode initially; hotspot methods are compiled to native code by C1 (client) and C2 (server) compilers. JVM uses profiling to optimise hot paths.
**GC Algorithms:**
- **Serial GC:** single-threaded; suitable for small heaps.
- **Parallel GC:** multi-threaded STW (stop-the-world); throughput-focused.
- **G1 GC (default Java 9+):** divides heap into regions; concurrent marking; predictable pause times.
- **ZGC / Shenandoah:** low-latency GCs with sub-millisecond pauses; suitable for large heaps.
Tuning flags: `-Xms`, `-Xmx`, `-XX:+UseG1GC`, `-XX:MaxGCPauseMillis`.

---
## Q11 | difficulty: beginner
**Question:** What is exception handling in Java? Checked vs unchecked exceptions?

**Answer:**
Exceptions are events that disrupt normal flow. Java uses try-catch-finally blocks.
- **Checked exceptions** (subclass of `Exception` but not `RuntimeException`): must be declared or caught. E.g., `IOException`, `SQLException`.
- **Unchecked exceptions** (subclass of `RuntimeException`): optional to catch. E.g., `NullPointerException`, `ArrayIndexOutOfBoundsException`.
- **Error**: severe JVM issues (`OutOfMemoryError`); generally not caught.
Best practices: catch specific exceptions, use finally for cleanup, prefer try-with-resources for `AutoCloseable` resources.

---
## Q12 | difficulty: intermediate
**Question:** What is the difference between `HashMap` and `ConcurrentHashMap`?

**Answer:**
- `HashMap` is **not thread-safe**; concurrent modification can cause infinite loops or data corruption.
- `ConcurrentHashMap` is **thread-safe** using segment-level locking (Java 7) or CAS + synchronized (Java 8+). Allows concurrent reads without locking.
- `Hashtable` is thread-safe but uses full-method synchronization (slow); legacy.
- For read-heavy concurrent scenarios, `ConcurrentHashMap` is preferred.
- `Collections.synchronizedMap()` wraps any map with coarse-grained locking.

---
## Q13 | difficulty: advanced
**Question:** Explain design patterns: Singleton, Factory, and Observer in Java.

**Answer:**
**Singleton:** ensures one instance per JVM. Thread-safe implementation using `enum` or double-checked locking with `volatile`.
**Factory Method:** defines an interface for creating objects; subclasses decide the concrete type. Decouples creation from usage.
**Observer:** defines a one-to-many dependency so when one object changes state, all dependents are notified. Used in event systems, MVC (Model notifies View).
In Spring: `@Bean` methods are factories; Spring Events implement Observer (`@EventListener`).

---
## Q14 | difficulty: intermediate
**Question:** What are Java interfaces vs abstract classes?

**Answer:**
| Feature | Interface | Abstract Class |
|---|---|---|
| Multiple inheritance | Yes (multiple interfaces) | No (single) |
| Constructor | No | Yes |
| Fields | Only `public static final` | Any type |
| Default methods | Yes (Java 8+) | Yes |
| When to use | Define a contract | Share common base behaviour |
Java 8 added `default` and `static` methods to interfaces, blurring the line, but abstract classes still win when shared state is needed.

---
## Q15 | difficulty: beginner
**Question:** What is the `final` keyword in Java?

**Answer:**
- **`final` variable:** value cannot be reassigned after initialization (effectively a constant for primitives; reference cannot change for objects, but object state can).
- **`final` method:** cannot be overridden by subclasses.
- **`final` class:** cannot be subclassed. E.g., `String`, `Integer` are final for immutability and security.

---
## Q16 | difficulty: intermediate
**Question:** How does Java handle memory with String literals and the String pool?

**Answer:**
String literals (e.g., `"hello"`) are stored in the **String pool** (part of the heap in Java 7+). The JVM reuses existing pool entries, so `"hello" == "hello"` is `true`.
`new String("hello")` always creates a heap object outside the pool; use `.intern()` to add it to the pool.
Strings are **immutable** – any modification creates a new object. Use `StringBuilder` for mutable string operations to avoid excessive object creation.

---
## Q17 | difficulty: advanced
**Question:** What is reactive programming and how is it implemented in Java (WebFlux)?

**Answer:**
Reactive programming is a non-blocking, event-driven paradigm that handles asynchronous data streams. Core concepts: Publisher, Subscriber, Subscription (Reactive Streams spec).
**Spring WebFlux** is Spring's reactive web framework using Project Reactor:
- `Mono<T>` – 0 or 1 element.
- `Flux<T>` – 0 to N elements.
Benefits: better scalability under high concurrency (fewer threads needed vs blocking Servlet model).
Use cases: streaming data, high-throughput microservices, real-time dashboards.

---
## Q18 | difficulty: advanced
**Question:** Explain microservices architecture and how Java/Spring supports it.

**Answer:**
Microservices decompose an application into small, independently deployable services communicating over APIs (REST, gRPC, messaging).
**Spring Cloud** components:
- **Eureka** – service discovery.
- **Spring Cloud Gateway** – API gateway with routing and filtering.
- **Feign** – declarative REST client.
- **Resilience4j** – circuit breaker, rate limiting, retry.
- **Spring Cloud Config** – centralised configuration.
Challenges: distributed transactions (Saga pattern), distributed tracing (Zipkin/Jaeger), eventual consistency.

---
## Q19 | difficulty: intermediate
**Question:** What is Hibernate and how does it differ from JDBC?

**Answer:**
Hibernate is a JPA implementation (ORM – Object-Relational Mapping) that maps Java objects to database tables automatically.
- **JDBC** requires manual SQL writing, result-set mapping, and connection management.
- **Hibernate** auto-generates SQL, manages sessions/transactions, supports caching (first/second level), and lazy loading.
Key concepts: `@Entity`, `@OneToMany`, `@ManyToOne`, `SessionFactory`, `HQL` (Hibernate Query Language).
Hibernate N+1 problem: fetching a collection triggers N additional queries; fix with `JOIN FETCH` or `@BatchSize`.

---
## Q20 | difficulty: beginner
**Question:** What are access modifiers in Java?

**Answer:**
| Modifier | Same class | Same package | Subclass | Other packages |
|---|---|---|---|---|
| `private` | ✓ | ✗ | ✗ | ✗ |
| (default) | ✓ | ✓ | ✗ | ✗ |
| `protected` | ✓ | ✓ | ✓ | ✗ |
| `public` | ✓ | ✓ | ✓ | ✓ |
Best practice: use the most restrictive modifier possible. Prefer `private` fields with public getters/setters (encapsulation).

---
## Q21 | difficulty: intermediate
**Question:** Explain Java 8 Optional class and its purpose.

**Answer:**
`Optional<T>` is a container that may or may not hold a non-null value. It forces explicit handling of null cases, reducing `NullPointerException`.
```java
Optional<String> opt = findUserById(id);
String name = opt.orElse("Unknown");
opt.ifPresent(u -> System.out.println(u));
String upper = opt.map(String::toUpperCase).orElseThrow();
```
Avoid: using Optional as a method parameter (use overloading instead); never use `opt.get()` without `isPresent()` check.

---
## Q22 | difficulty: advanced
**Question:** What are Java annotations and how do you create a custom annotation?

**Answer:**
Annotations are metadata attached to code elements. Built-in: `@Override`, `@Deprecated`, `@FunctionalInterface`.
Custom annotation:
```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface AuditLog {
    String value() default "audit";
}
```
Processed at runtime via reflection (`method.getAnnotation(AuditLog.class)`) or at compile time via APT (Annotation Processing Tool).
Spring heavily uses annotations: `@Component`, `@Autowired`, `@Transactional`, `@RequestMapping`.

---
## Q23 | difficulty: intermediate
**Question:** What is dependency injection and how does Spring implement it?

**Answer:**
Dependency Injection (DI) is a design pattern where an object's dependencies are provided externally rather than created internally, enabling loose coupling and testability.
Spring implements DI via:
- **Constructor injection** (preferred): `@Autowired` on constructor or implicit in Spring Boot.
- **Setter injection**: for optional dependencies.
- **Field injection**: `@Autowired` directly on fields (discouraged in production; harder to test).
Spring's IoC container (`ApplicationContext`) manages bean lifecycle and wiring.

---
## Q24 | difficulty: advanced
**Question:** How do you handle transactions in Spring? What is `@Transactional`?

**Answer:**
`@Transactional` marks a method (or class) to run within a database transaction. Spring uses AOP (Aspect-Oriented Programming) proxy to begin/commit/rollback.
Key attributes:
- `propagation`: `REQUIRED` (join existing or create new), `REQUIRES_NEW` (always new), `SUPPORTS`, etc.
- `isolation`: `READ_COMMITTED`, `REPEATABLE_READ`, etc.
- `rollbackFor`: specify exceptions that trigger rollback (by default only `RuntimeException`).
- `readOnly = true`: hint for optimisation (skip dirty-checking in Hibernate).
Pitfall: `@Transactional` on private methods or self-invocation doesn't work (proxy is bypassed).

---
## Q25 | difficulty: advanced
**Question:** What is Kafka and how is it used with Java microservices?

**Answer:**
Apache Kafka is a distributed event streaming platform used for high-throughput, fault-tolerant messaging.
Key concepts: Topics, Partitions, Producers, Consumers, Consumer Groups, Offsets, Brokers, ZooKeeper/KRaft.
Java integration via **Spring Kafka**:
```java
@KafkaListener(topics = "orders", groupId = "order-service")
public void consume(String message) { ... }
```
Use cases: event-driven microservices, log aggregation, real-time analytics, CQRS event sourcing.
Guarantees: at-least-once, at-most-once, exactly-once (with transactions and idempotent producers).

---
## Q26 | difficulty: intermediate
**Question:** What are common Java performance optimization techniques?

**Answer:**
1. **Use primitive types** over wrappers where possible (avoids boxing overhead).
2. **Prefer `StringBuilder`** over `String` concatenation in loops.
3. **Connection pooling** (HikariCP) for database connections.
4. **Caching** (Spring Cache, Redis) for expensive computations/queries.
5. **Lazy loading** – defer object initialisation until needed.
6. **Efficient collections** – choose the right data structure for access patterns.
7. **Profiling** with tools like JProfiler, VisualVM, or JMC to find bottlenecks before optimising.
8. **Reduce GC pressure** by reusing objects and avoiding unnecessary allocations.

---
## Q27 | difficulty: intermediate
**Question:** What is REST and how do you build RESTful APIs with Spring Boot?

**Answer:**
REST (Representational State Transfer) is an architectural style using HTTP verbs (GET, POST, PUT, DELETE, PATCH) and stateless requests.
Spring Boot REST:
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) { ... }
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody @Valid UserDTO dto) { ... }
}
```
Best practices: use proper status codes, version APIs (`/v1/`), use DTOs (never expose entities), document with Swagger/OpenAPI.

---
## Q28 | difficulty: advanced
**Question:** What is Docker and how do you containerise a Spring Boot application?

**Answer:**
Docker packages applications with their dependencies into containers for consistent deployment across environments.
Dockerfile for Spring Boot:
```dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```
Multi-stage build (reduces image size):
```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build
COPY . .
RUN mvn package -DskipTests
FROM eclipse-temurin:17-jre-alpine
COPY --from=build /target/app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```
Use `docker-compose` for local multi-service setups.

---
## Q29 | difficulty: intermediate
**Question:** What is JUnit 5 and Mockito? How do you write unit tests for a Spring service?

**Answer:**
**JUnit 5** is the testing framework; **Mockito** mocks dependencies.
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock OrderRepository repo;
    @InjectMocks OrderService service;
    
    @Test
    void shouldReturnOrderById() {
        when(repo.findById(1L)).thenReturn(Optional.of(new Order(1L, "PENDING")));
        Order order = service.getOrder(1L);
        assertThat(order.getStatus()).isEqualTo("PENDING");
        verify(repo, times(1)).findById(1L);
    }
}
```
`@SpringBootTest` for integration tests; `@WebMvcTest` for controller layer only; `@DataJpaTest` for repository layer.

---
## Q30 | difficulty: advanced
**Question:** Explain the Circuit Breaker pattern and implement it with Resilience4j.

**Answer:**
Circuit Breaker prevents cascading failures by stopping calls to a failing service after a threshold.
States: CLOSED (normal) → OPEN (failing, reject calls) → HALF_OPEN (trial calls to check recovery).
```java
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
public PaymentResponse processPayment(PaymentRequest req) {
    return paymentClient.process(req);
}

public PaymentResponse paymentFallback(PaymentRequest req, Exception e) {
    return PaymentResponse.failed("Service temporarily unavailable");
}
```
Configuration in `application.yml`:
```yaml
resilience4j.circuitbreaker.instances.paymentService:
  slidingWindowSize: 10
  failureRateThreshold: 50
  waitDurationInOpenState: 10s
```
