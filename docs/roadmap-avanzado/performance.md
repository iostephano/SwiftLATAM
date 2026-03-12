---
sidebar_position: 1
title: Performance
---

# Performance en iOS: Guía Avanzada para Desarrolladores

## ¿Qué es Performance en el contexto iOS?

Performance (rendimiento) se refiere a la capacidad de tu aplicación para ejecutar sus tareas de manera eficiente, utilizando la menor cantidad de recursos posible — CPU, memoria, batería y red — mientras ofrece una experiencia fluida al usuario. En términos prácticos, significa que tu app debe mantener **60 FPS** (o 120 FPS en dispositivos con ProMotion), responder a interacciones en menos de **100 milisegundos** y nunca hacer sentir al usuario que "algo está trabado".

No se trata de optimización prematura. Se trata de entender las herramientas de diagnóstico, conocer los patrones que generan cuellos de botella y saber cuándo y dónde intervenir.

## ¿Por qué es crítico para un dev iOS en LATAM?

En Latinoamérica, el contexto de uso tiene particularidades que hacen del rendimiento un tema aún más relevante:

- **Dispositivos más antiguos**: Una gran parte de la base de usuarios en LATAM utiliza iPhones de generaciones anteriores (iPhone 8, iPhone SE 2da generación). Lo que funciona bien en un iPhone 15 Pro puede ser inutilizable en un iPhone 8 con 2 GB de RAM.
- **Conectividad limitada**: Muchas regiones tienen redes 3G o conexiones WiFi inestables. Una app que no gestiona bien las llamadas de red puede parecer completamente rota.
- **Retención de usuarios**: Los usuarios en mercados emergentes son menos tolerantes con apps lentas. Si tu app tarda más de 3 segundos en mostrar contenido útil, la desinstalan.
- **Diferenciador profesional**: Dominar Instruments, entender el memory graph y optimizar tiempos de carga te posiciona muy por encima del promedio en el mercado laboral latinoamericano.

## Los pilares del rendimiento en iOS

### 1. Rendimiento de UI (Main Thread)

El hilo principal es sagrado. Todo lo que bloquee el main thread se traduce en frames perdidos y una interfaz que se siente "pegajosa".

```swift
// ❌ MAL: Procesamiento pesado en el hilo principal
func loadData() {
    let data = try? Data(contentsOf: hugeFileURL) // Bloquea el main thread
    let parsed = parseComplexJSON(data!)
    self.tableView.reloadData()
}

// ✅ BIEN: Mover trabajo pesado a un hilo secundario
func loadData() {
    Task.detached(priority: .userInitiated) {
        let data = try Data(contentsOf: hugeFileURL)
        let parsed = parseComplexJSON(data)
        
        await MainActor.run {
            self.items = parsed
            self.tableView.reloadData()
        }
    }
}
```

### 2. Gestión de memoria

Los memory leaks y los retain cycles son los enemigos silenciosos del rendimiento. Tu app puede funcionar bien los primeros 5 minutos y luego colapsar.

```swift
// ❌ Retain cycle clásico con closures
class ProfileViewController: UIViewController {
    var viewModel: ProfileViewModel?
    
    func setupBindings() {
        viewModel?.onUpdate = {
            // `self` es capturado fuertemente → retain cycle
            self.updateUI()
        }
    }
}

// ✅ Captura débil para romper el ciclo
class ProfileViewController: UIViewController {
    var viewModel: ProfileViewModel?
    
    func setupBindings() {
        viewModel?.onUpdate = { [weak self] in
            guard let self else { return }
            self.updateUI()
        }
    }
}
```

#### Detectar leaks programáticamente en Debug

```swift
// Extensión útil para detectar leaks durante desarrollo
extension UIViewController {
    func checkForMemoryLeak(afterDelay delay: TimeInterval = 2.0) {
        #if DEBUG
        let viewControllerName = String(describing: type(of: self))
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            if self != nil {
                print("⚠️ POSIBLE MEMORY LEAK: \(viewControllerName) sigue en memoria después de ser descartado")
                assertionFailure("Memory leak detectado en \(viewControllerName)")
            }
        }
        #endif
    }
}

// Uso en tu view controller
override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    if isBeingDismissed || isMovingFromParent {
        checkForMemoryLeak()
    }
}
```

### 3. Optimización de listas y colecciones

Las tablas y colecciones son el componente más usado y más fácil de arruinar en términos de rendimiento.

```swift
// ✅ Cell reuse eficiente con prefetching
class FeedViewController: UIViewController {
    
    private let tableView = UITableView()
    private var items: [FeedItem] = []
    private let imageCache = NSCache<NSString, UIImage>()
    
    func setup() {
        tableView.register(FeedCell.self, forCellReuseIdentifier: "FeedCell")
        tableView.prefetchDataSource = self
        
        // Configuración clave para rendimiento
        tableView.estimatedRowHeight = 120
        tableView.rowHeight = UITableView.automaticDimension
    }
}

// MARK: - Prefetching
extension FeedViewController: UITableViewDataSourcePrefetching {
    
    func tableView(_ tableView: UITableView, prefetchRowsAt indexPaths: [IndexPath]) {
        for indexPath in indexPaths {
            let item = items[indexPath.row]
            
            // Pre-cargar imágenes antes de que la celda sea visible
            if imageCache.object(forKey: item.imageURL.absoluteString as NSString) == nil {
                Task {
                    let (data, _) = try await URLSession.shared.data(from: item.imageURL)
                    if let image = UIImage(data: data) {
                        imageCache.setObject(image, forKey: item.imageURL.absoluteString as NSString)
                    }
                }
            }
        }
    }
    
    func tableView(_ tableView: UITableView, cancelPrefetchingForRowsAt indexPaths: [IndexPath]) {
        // Cancelar descargas innecesarias cuando el usuario cambia de dirección
    }
}
```

### 4. Optimización de red para conexiones lentas

```swift
// Estrategia de carga adaptativa según la calidad de conexión
import Network

class AdaptiveNetworkManager {
    
    static let shared = AdaptiveNetworkManager()
    
    private let monitor = NWPathMonitor()
    private(set) var currentConnectionType: ConnectionType = .unknown
    
    enum ConnectionType {
        case wifi
        case cellular
        case expensive   // Datos limitados
        case constrained // Modo de datos reducidos
        case unknown
    }
    
    func startMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            if path.usesInterfaceType(.wifi) {
                self?.currentConnectionType = .wifi
            } else if path.isConstrained {
                self?.currentConnectionType = .constrained
            } else if path.isExpensive {
                self?.currentConnectionType = .expensive
            } else if path.usesInterfaceType(.cellular) {
                self?.currentConnectionType = .cellular
            }
        }
        
        let queue = DispatchQueue(label: "NetworkMonitor")
        monitor.start(queue: queue)
    }
    
    /// Retorna la calidad de imagen apropiada según la conexión
    func appropriateImageQuality() -> ImageQuality {
        switch currentConnectionType {
        case .wifi:
            return .high       // Imágenes completas
        case .cellular:
            return .medium     // Imágenes comprimidas
        case .expensive, .constrained:
            return .low        // Thumbnails mínimos
        case .unknown:
            return .medium
        }
    }
    
    enum ImageQuality {
        case high, medium, low
        
        var maxDimension: Int {
            switch self {
            case .high: return 1080
            case .medium: return 540
            case .low: return 270
            }
        }
    }
}
```

### 5. Instruments: Tu herramienta principal de diagnóstico

Instruments no es opcional — es una herramienta fundamental. Estos son los templates que debes dominar:

| Instrumento | Qué detecta | Cuándo usarlo |
|---|---|---|
| **Time Profiler** | Funciones que consumen más CPU | Cuando la app se siente lenta |
| **Allocations** | Uso de memoria y objetos creados | Cuando la memoria crece sin control |
| **Leaks** | Retain cycles y memory leaks | Después de cada feature nueva |
| **Core Animation** | FPS, offscreen rendering, blending | Cuando el scroll no es fluido |
| **Network** | Llamadas HTTP, tamaños, latencia | Optimización de carga de datos |
| **Energy Log** | Consumo de batería | Antes de enviar a producción |

### 6. Medir el tiempo de arranque (App Launch Time)

```swift
// En tu AppDelegate o punto de entrada
class AppLaunchTracker {
    
    static let shared = AppLaunchTracker()
    
    private var phaseTimestamps: [String: CFAbsoluteTime] = [:]
    private let launchStart = CFAbsoluteTimeGetCurrent()
    
    func markPhase(_ name: String) {
        let elapsed = CFAbsoluteTimeGetCurrent() - launchStart
        phaseTimestamps[name] = elapsed
        
        #if DEBUG
        print("📊 [\(String(format: "%.3f", elapsed))s] \(name)")
        #endif
    }
    
    func reportLaunchComplete() {
        let totalTime = CFAbsoluteTimeGetCurrent() - launchStart
        
        #if DEBUG
        print("🚀 Tiempo total de arranque: \(String(format: "%.3f", totalTime))s")
        print("   Fases:")
        for (phase, time) in phaseTimestamps.sorted(by: { $0.value < $1.value }) {
            print("   - \(phase): \(String(format: "%.3f", time))s")
        }
        
        if totalTime > 2.0 {
            print("⚠️ ADVERTENCIA: El arranque supera los 2 segundos. Optimización necesaria.")
        }
        #endif
    }
}

// Uso
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        
        AppLaunchTracker.shared.markPhase("didFinishLaunching - inicio")
        
        setupDependencies()
        AppLaunchTracker.shared.markPhase("Dependencias configuradas")
        
        setupAppearance()
        AppLaunchTracker.shared.markPhase("Apariencia configurada")
        
        // Diferir trabajo no crítico
        DispatchQueue.main.async {
            self.setupAnalytics()
            self.setupPushNotifications()
            AppLaunchTracker.shared.markPhase("Tareas diferidas completadas")
            AppLaunchTracker.shared.reportLaunchComplete()
        }
        
        return true
    }
}
```

### 7. Rendimiento en SwiftUI

SwiftUI tiene sus propias trampas de rendimiento. La clave está en minimizar las re-evaluaciones del body.

```swift
// ❌ MAL: Todo se recalcula cuando cambia cualquier estado
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
    
    var body: some View {
        ScrollView {
            LazyVStack { // ✅ Usar LazyVStack en vez de VStack para listas largas
                ForEach(viewModel.items) { item in
                    FeedItemView(item: item)
                }
            }
        }
    }
}

// ✅ BIEN: Componentes aislados que solo se actualizan cuando sus datos cambian
struct FeedItemView: View {
    let item: FeedItem // Usar let, no @Binding ni @ObservedObject si no es necesario
    
    var body: some View {
        // Este body solo se re-evalúa si `item` cambia
        VStack(alignment: .leading, spacing: 8) {
            // Evitar operaciones costosas aquí
            Text(item.title)
                .font(.headline)
            
            Text(item.subtitle)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            // ✅ Usar .drawingGroup() para vistas con muchas capas gráficas
            ComplexGraphView(data: item.graphData)
                .drawingGroup()
        }
    }
}

// ✅ Equatable conformance para evitar re-renders innecesarios
struct ExpensiveView: View, Equatable {
    let data: ChartData
    
    static func == (lhs: ExpensiveView, rhs: ExpensiveView) -> Bool {
        lhs.data.id == rhs.data.id && lhs.data.lastUpdated == rhs.data.lastUpdated
    }
    
    var body: some View {
        // Renderizado costoso que solo ocurre cuando los datos realmente cambian
        Chart(data.points) { point in
            LineMark(x: .value("X", point.x), y: .value("Y", point.y))
        }
    }
}
```

### 8. Caché inteligente de datos

```swift
/// Cache con política de expiración — fundamental para apps con datos dinámicos
actor DataCache<T: Codable> {
    
    struct CachedItem {
        let value: T
        let timestamp: Date
        let ttl: TimeInterval
        
        var isExpired: Bool {
            Date().timeIntervalSince(timestamp) > ttl
        }
    }
    
    private var storage: [String: CachedItem] = [:]
    private let maxItems: Int
    
    init(maxItems: Int = 100) {
        self.maxItems = maxItems
    }
    
    func get(_ key: String) -> T? {
        guard let item = storage[key] else { return nil }
        
        if item.isExpired {
            storage.removeValue(forKey: key)
            return nil
        }
        
        return item.value
    }
    
    func set(_ key: String, value: T, ttl: TimeInterval = 300) {
        // Evicción simple si excedemos el límite
        if storage.count >= maxItems {
            let oldestKey = storage
                .sorted { $0.value.timestamp < $1.value.timestamp }
                .first?.key
            
            if let oldestKey {
                storage.removeValue(forKey: oldestKey)
            }
        }
        
        storage[key] = CachedItem(value: value, timestamp: Date(), ttl: ttl)
    }
    
    func invalidate(_ key: String) {
        storage.removeValue(forKey: key)
    }
    
    func invalidateAll() {
        storage.removeAll()
    }
}

// Uso con el actor
class ProductRepository {
    
    private let cache = DataCache<[Product]>()
    private let apiClient