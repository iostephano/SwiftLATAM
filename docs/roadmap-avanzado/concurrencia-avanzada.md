---
sidebar_position: 1
title: Concurrencia Avanzada
---

# Concurrencia Avanzada en iOS

## ¿Qué es la concurrencia y por qué ir más allá de lo básico?

La concurrencia es la capacidad de ejecutar múltiples tareas de forma simultánea o intercalada. En iOS, todos hemos usado `DispatchQueue.main.async` o algún `DispatchQueue.global().async` para "mover trabajo al background". Pero la concurrencia avanzada va mucho más allá: implica entender **modelos de ejecución**, **garantías de seguridad de datos**, **patrones de sincronización**, y dominar **Swift Concurrency** (async/await, actores, grupos de tareas) a un nivel que te permita construir aplicaciones robustas, escalables y libres de data races.

---

## ¿Por qué es crítico para un dev iOS en LATAM?

En el mercado latinoamericano, la diferencia entre un desarrollador junior y uno senior frecuentemente se mide en su capacidad para resolver problemas de concurrencia. Las empresas —tanto startups locales como compañías que contratan remoto para EE.UU. y Europa— buscan ingenieros que puedan:

- **Diagnosticar y corregir crashes intermitentes** causados por accesos concurrentes a datos compartidos.
- **Optimizar el rendimiento** de apps que consumen APIs lentas o inestables (algo común en infraestructura LATAM).
- **Diseñar arquitecturas** que escalen sin introducir bugs difíciles de reproducir.
- **Pasar entrevistas técnicas** donde los problemas de concurrencia son filtro habitual para roles senior y semi-senior.

Dominar este tema te posiciona directamente para roles mejor remunerados, tanto locales como remotos.

---

## Los pilares de la concurrencia avanzada en iOS

### 1. Grand Central Dispatch (GCD) — Más allá del básico

GCD sigue siendo el motor subyacente. Entender sus primitivas avanzadas es fundamental.

#### Dispatch Barriers para lectura/escritura segura

El patrón **readers-writers** con barreras es una de las técnicas más poderosas y menos comprendidas:

```swift
final class ThreadSafeCache<Key: Hashable, Value> {
    private var storage: [Key: Value] = [:]
    private let queue = DispatchQueue(
        label: "com.miapp.cache",
        attributes: .concurrent
    )

    /// Lectura concurrente — múltiples hilos pueden leer simultáneamente
    func value(forKey key: Key) -> Value? {
        queue.sync {
            storage[key]
        }
    }

    /// Escritura exclusiva — la barrera bloquea todas las lecturas
    /// hasta que la escritura termine
    func setValue(_ value: Value, forKey key: Key) {
        queue.async(flags: .barrier) {
            self.storage[key] = value
        }
    }

    /// Eliminación también requiere barrera
    func removeValue(forKey key: Key) {
        queue.async(flags: .barrier) {
            self.storage.removeValue(forKey: key)
        }
    }
}
```

**¿Por qué funciona?** La cola concurrente permite múltiples lecturas simultáneas. Cuando llega una operación con `.barrier`, GCD espera a que terminen todas las lecturas en curso, ejecuta la escritura de forma exclusiva, y luego reanuda las lecturas pendientes.

#### DispatchSemaphore para limitar concurrencia

Cuando necesitas controlar cuántas operaciones concurrentes se ejecutan (por ejemplo, limitar descargas simultáneas):

```swift
final class ThrottledDownloader {
    private let semaphore: DispatchSemaphore
    private let downloadQueue = DispatchQueue(
        label: "com.miapp.downloads",
        attributes: .concurrent
    )

    /// maxConcurrent: número máximo de descargas simultáneas
    init(maxConcurrent: Int = 3) {
        self.semaphore = DispatchSemaphore(value: maxConcurrent)
    }

    func download(urls: [URL], completion: @escaping ([Data?]) -> Void) {
        var results = [Data?](repeating: nil, count: urls.count)
        let group = DispatchGroup()

        for (index, url) in urls.enumerated() {
            group.enter()
            downloadQueue.async { [weak self] in
                guard let self else {
                    group.leave()
                    return
                }

                // Espera hasta que haya un "slot" disponible
                self.semaphore.wait()

                let data = try? Data(contentsOf: url)
                results[index] = data

                // Libera el slot para la siguiente descarga
                self.semaphore.signal()
                group.leave()
            }
        }

        group.notify(queue: .main) {
            completion(results)
        }
    }
}
```

> ⚠️ **Cuidado:** `semaphore.wait()` bloquea el hilo actual. Nunca lo uses en el hilo principal.

---

### 2. Swift Concurrency — El modelo moderno

A partir de Swift 5.5, el modelo de concurrencia estructurada cambió las reglas del juego.

#### async/await: Fundamento sólido

```swift
struct APIClient {
    private let session: URLSession
    private let baseURL: URL

    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    func fetchUser(id: Int) async throws -> User {
        let url = baseURL.appendingPathComponent("users/\(id)")
        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }

        return try JSONDecoder().decode(User.self, from: data)
    }

    func fetchUserWithPosts(id: Int) async throws -> (User, [Post]) {
        // Ejecución concurrente REAL con async let
        async let user = fetchUser(id: id)
        async let posts = fetchPosts(userId: id)

        // Ambas peticiones se ejecutan en paralelo
        // Aquí esperamos los resultados
        return try await (user, posts)
    }

    private func fetchPosts(userId: Int) async throws -> [Post] {
        let url = baseURL.appendingPathComponent("users/\(userId)/posts")
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode([Post].self, from: data)
    }
}
```

**Punto clave:** `async let` es la forma idiomática de ejecutar tareas en paralelo dentro de concurrencia estructurada. Sin `async let`, las llamadas `await` se ejecutan secuencialmente.

#### TaskGroup: Concurrencia dinámica

Cuando el número de tareas paralelas no es conocido en tiempo de compilación:

```swift
func fetchAllUsers(ids: [Int]) async throws -> [User] {
    try await withThrowingTaskGroup(of: (Int, User).self) { group in
        for id in ids {
            group.addTask {
                let user = try await APIClient.shared.fetchUser(id: id)
                return (id, user)
            }
        }

        var users: [Int: User] = [:]

        for try await (id, user) in group {
            users[id] = user
        }

        // Preservar el orden original
        return ids.compactMap { users[$0] }
    }
}
```

#### Cancelación cooperativa

Una de las ventajas más importantes de Swift Concurrency es la cancelación integrada:

```swift
func fetchDataWithCancellationSupport() async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item?.self) { group in
        let urls = generateURLs()

        for url in urls {
            // Verificar cancelación ANTES de agregar más trabajo
            try Task.checkCancellation()

            group.addTask {
                // Dentro de cada tarea, verificar también
                guard !Task.isCancelled else { return nil }

                let (data, _) = try await URLSession.shared.data(from: url)
                return try JSONDecoder().decode(Item.self, from: data)
            }
        }

        var items: [Item] = []
        for try await item in group {
            if let item {
                items.append(item)
            }
        }
        return items
    }
}

// Uso con cancelación automática
class SearchViewModel: ObservableObject {
    @Published var results: [Item] = []
    private var searchTask: Task<Void, Never>?

    func search(query: String) {
        // Cancelar búsqueda anterior automáticamente
        searchTask?.cancel()

        searchTask = Task {
            // Debounce de 300ms
            try? await Task.sleep(nanoseconds: 300_000_000)

            guard !Task.isCancelled else { return }

            do {
                let results = try await performSearch(query: query)

                // Siempre verificar antes de actualizar UI
                guard !Task.isCancelled else { return }

                await MainActor.run {
                    self.results = results
                }
            } catch {
                // La cancelación lanza CancellationError, no es un error real
                if !(error is CancellationError) {
                    print("Error real: \(error)")
                }
            }
        }
    }
}
```

---

### 3. Actors: Protección de estado sin locks manuales

Los actores son el mecanismo de Swift para garantizar acceso seguro a estado mutable compartido.

#### Actor básico

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]
    private var inProgressTasks: [URL: Task<UIImage, Error>] = [:]

    func image(for url: URL) async throws -> UIImage {
        // Si ya está en caché, retornar inmediatamente
        if let cached = cache[url] {
            return cached
        }

        // Si ya hay una descarga en progreso para esta URL,
        // reutilizar esa tarea (evitar descargas duplicadas)
        if let existingTask = inProgressTasks[url] {
            return try await existingTask.value
        }

        // Crear nueva tarea de descarga
        let task = Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            guard let image = UIImage(data: data) else {
                throw ImageCacheError.invalidData
            }
            return image
        }

        inProgressTasks[url] = task

        do {
            let image = try await task.value
            cache[url] = image
            inProgressTasks.removeValue(forKey: url)
            return image
        } catch {
            inProgressTasks.removeValue(forKey: url)
            throw error
        }
    }

    func clearCache() {
        cache.removeAll()
    }

    /// nonisolated: no necesita acceso exclusivo al actor
    nonisolated func supportedFormats() -> [String] {
        ["png", "jpg", "webp", "heic"]
    }
}
```

#### @globalActor: Actores globales personalizados

Cuando necesitas que múltiples tipos compartan el mismo contexto de aislamiento:

```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
final class UserRepository {
    private var localCache: [Int: User] = [:]

    func save(user: User) async throws {
        // Todo este código se ejecuta en el DatabaseActor
        localCache[user.id] = user
        try await persistToDisk(user)
    }

    func fetchAll() -> [User] {
        Array(localCache.values)
    }

    private func persistToDisk(_ user: User) async throws {
        // Operación de I/O
        let data = try JSONEncoder().encode(user)
        let fileURL = getFileURL(for: user.id)
        try data.write(to: fileURL)
    }
}

@DatabaseActor
final class PostRepository {
    // Este repositorio también se ejecuta en el mismo DatabaseActor
    // Garantiza serialización entre UserRepository y PostRepository
    func savePosts(_ posts: [Post]) async throws {
        // ...
    }
}
```

#### Sendable: El contrato de seguridad

`Sendable` es el protocolo que garantiza que un tipo puede cruzar fronteras de concurrencia de forma segura:

```swift
// ✅ Los structs con propiedades Sendable son automáticamente Sendable
struct UserDTO: Sendable {
    let id: Int
    let name: String
    let email: String
}

// ✅ Enums sin valores asociados o con valores Sendable
enum AppError: Error, Sendable {
    case networkError(String)
    case decodingError
    case unauthorized
}

// ✅ Clases finales inmutables
final class AppConfiguration: Sendable {
    let apiBaseURL: URL
    let apiKey: String
    let timeout: TimeInterval

    init(apiBaseURL: URL, apiKey: String, timeout: TimeInterval = 30) {
        self.apiBaseURL = apiBaseURL
        self.apiKey = apiKey
        self.timeout = timeout
    }
}

// ⚠️ Cuando necesitas enviar un closure entre contextos de concurrencia
actor DataProcessor {
    func process(
        items: [Item],
        transform: @Sendable (Item) -> ProcessedItem
    ) async -> [ProcessedItem] {
        await withTaskGroup(of: ProcessedItem.self) { group in
            for item in items {
                group.addTask {
                    transform(item)
                }
            }

            var results: [ProcessedItem] = []
            for await result in group {
                results.append(result)
            }
            return results
        }
    }
}
```

---

### 4. Patrones avanzados del mundo real

#### AsyncSequence para streams de datos

```swift
struct PriceStream: AsyncSequence {
    typealias Element = StockPrice

    let symbol: String
    let refreshInterval: TimeInterval

    struct AsyncIterator: AsyncIteratorProtocol {
        let symbol: String
        let refreshInterval: TimeInterval
        private var isActive = true

        mutating func next() async throws -> StockPrice? {
            guard isActive, !Task.isCancelled else {
                return nil
            }

            try await Task.sleep(
                nanoseconds: UInt64(refreshInterval * 1_000_000_000)
            )

            guard !Task.isCancelled else { return nil }

            return try await StockAPI.fetchPrice(symbol: symbol)
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(symbol: symbol, refreshInterval: refreshInterval)
    }
}

// Uso
class StockViewModel: ObservableObject {
    @Published var currentPrice: StockPrice?
    private var streamTask: Task<Void, Never>?

    func startTracking(symbol: String) {
        streamTask?.cancel()

        streamTask = Task {
            let stream = PriceStream(symbol: symbol, refreshInterval: 5.0)

            do {
                for try await price in stream {
                    await MainActor.run {
                        self.currentPrice = price
                    }
                }
            } catch {
                if !(error is CancellationError) {
                    print("Stream error: \(error)")
                }
            }
        }
    }

    func stopTracking() {
        streamTask?.cancel()
        streamTask = nil
    }
}
```

#### AsyncStream para adaptar APIs basadas en callbacks/delegates

```