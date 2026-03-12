---
sidebar_position: 1
title: Combine Mastery
---

# Combine Mastery: Dominando la Programación Reactiva en iOS

## ¿Qué es Combine?

Combine es el framework de **programación reactiva** de Apple, introducido en WWDC 2019. Su propósito es claro: proporcionar una API declarativa y unificada para procesar valores a lo largo del tiempo. En lugar de depender de callbacks anidados, delegados dispersos o notificaciones desconectadas, Combine te permite construir **pipelines de datos** elegantes y predecibles.

En su núcleo, Combine se basa en tres conceptos fundamentales:

- **Publishers**: Emiten valores a lo largo del tiempo
- **Operators**: Transforman, filtran y combinan esos valores
- **Subscribers**: Reciben y reaccionan a los valores finales

```swift
// La esencia de Combine en 3 líneas
let publisher = URLSession.shared.dataTaskPublisher(for: url)  // Publisher
    .map(\.data)                                                 // Operator
    .sink { data in print(data) }                                // Subscriber
```

## ¿Por qué es fundamental para un dev iOS en LATAM?

El mercado de desarrollo iOS en Latinoamérica está en plena transformación. Las empresas — desde fintechs en Colombia y México hasta startups en Argentina y Chile — buscan desarrolladores que dominen arquitecturas modernas. Aquí es donde Combine marca la diferencia:

1. **Es prerequisito para SwiftUI**: No puedes dominar SwiftUI sin entender `@Published`, `ObservableObject` y los flujos reactivos que Combine alimenta.
2. **Diferenciación salarial real**: En el mercado LATAM remoto, las posiciones que exigen Combine + SwiftUI pagan significativamente más que las que solo requieren UIKit con MVC tradicional.
3. **Es de Apple, no de terceros**: A diferencia de RxSwift (excelente pero externo), Combine está integrado nativamente. No agregas dependencias, no tienes conflictos de versión, y Apple lo mantiene directamente.
4. **Código de producción real lo usa**: Si revisas ofertas en plataformas como Turing, Toptal o empresas como Rappi, Nubank y Mercado Libre, Combine aparece consistentemente en los requisitos.

## Los Pilares de Combine: Explicación Profunda

### 1. Publishers — La Fuente de Verdad

Un `Publisher` es cualquier cosa que emite una secuencia de valores y, eventualmente, un evento de finalización (éxito o error).

```swift
import Combine

// Publisher más simple: Just emite un solo valor y termina
let simplePublisher = Just("Hola desde Combine")

// Publisher que emite una secuencia
let arrayPublisher = [1, 2, 3, 4, 5].publisher

// Publisher basado en un Subject (emisión manual)
let subject = PassthroughSubject<String, Never>()

// CurrentValueSubject mantiene el último valor emitido
let currentValue = CurrentValueSubject<Int, Never>(0)
```

#### Tipos de Publisher que DEBES conocer

| Publisher | Uso | Ejemplo Real |
|-----------|-----|-------------|
| `Just` | Emitir un solo valor | Valores por defecto |
| `Future` | Operación async que emite un resultado | Llamadas a API |
| `PassthroughSubject` | Emisión manual sin estado | Eventos de UI |
| `CurrentValueSubject` | Emisión manual CON estado | Estado de sesión |
| `@Published` | Property wrapper reactivo | ViewModels |
| `URLSession.DataTaskPublisher` | Peticiones de red | Consumo de APIs |
| `NotificationCenter.Publisher` | Escuchar notificaciones del sistema | Teclado, app lifecycle |
| `Timer.TimerPublisher` | Emisiones periódicas | Countdowns, polling |

### 2. Operators — El Verdadero Poder

Los operadores son donde Combine brilla. Transforman el flujo de datos sin efectos secundarios ni estado mutable.

#### Operadores de Transformación

```swift
import Combine

var cancellables = Set<AnyCancellable>()

// map: Transforma cada valor
[1, 2, 3, 4, 5].publisher
    .map { $0 * 10 }
    .sink { print($0) } // 10, 20, 30, 40, 50
    .store(in: &cancellables)

// flatMap: Transforma en un nuevo Publisher (esencial para llamadas encadenadas)
func fetchUser(id: Int) -> AnyPublisher<String, Never> {
    Just("Usuario_\(id)")
        .delay(for: .seconds(1), scheduler: RunLoop.main)
        .eraseToAnyPublisher()
}

Just(42)
    .flatMap { userId in
        fetchUser(id: userId)
    }
    .sink { userName in
        print("Nombre: \(userName)") // "Nombre: Usuario_42"
    }
    .store(in: &cancellables)

// compactMap: Transforma y descarta nils
["1", "dos", "3", "cuatro", "5"].publisher
    .compactMap { Int($0) }
    .sink { print($0) } // 1, 3, 5
    .store(in: &cancellables)
```

#### Operadores de Filtrado

```swift
// filter: Solo deja pasar valores que cumplan la condición
(1...20).publisher
    .filter { $0.isMultiple(of: 3) }
    .sink { print($0) } // 3, 6, 9, 12, 15, 18
    .store(in: &cancellables)

// removeDuplicates: Elimina valores consecutivos duplicados
[1, 1, 2, 2, 3, 1, 1].publisher
    .removeDuplicates()
    .sink { print($0) } // 1, 2, 3, 1
    .store(in: &cancellables)

// debounce: Espera un tiempo sin nuevas emisiones (CRÍTICO para búsquedas)
let searchSubject = PassthroughSubject<String, Never>()

searchSubject
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { query in
        print("Buscando: \(query)")
    }
    .store(in: &cancellables)

// Simula escritura rápida del usuario
searchSubject.send("M")
searchSubject.send("Me")
searchSubject.send("Mer")
searchSubject.send("Merc")
searchSubject.send("Merca")
searchSubject.send("Mercad")
searchSubject.send("Mercado")
// Solo imprime "Buscando: Mercado" (después de 300ms sin cambios)
```

#### Operadores de Combinación

```swift
// combineLatest: Combina el último valor de múltiples publishers
let email = CurrentValueSubject<String, Never>("")
let password = CurrentValueSubject<String, Never>("")

email.combineLatest(password)
    .map { email, password in
        !email.isEmpty && password.count >= 8
    }
    .sink { isValid in
        print("Formulario válido: \(isValid)")
    }
    .store(in: &cancellables)

email.send("dev@ejemplo.com")   // Formulario válido: false
password.send("12345678")        // Formulario válido: true

// merge: Unifica múltiples publishers del mismo tipo
let notificacionesPush = PassthroughSubject<String, Never>()
let notificacionesLocal = PassthroughSubject<String, Never>()

notificacionesPush
    .merge(with: notificacionesLocal)
    .sink { mensaje in
        print("Notificación: \(mensaje)")
    }
    .store(in: &cancellables)

// zip: Combina valores en pares (espera a que ambos emitan)
let nombres = PassthroughSubject<String, Never>()
let edades = PassthroughSubject<Int, Never>()

nombres.zip(edades)
    .sink { nombre, edad in
        print("\(nombre) tiene \(edad) años")
    }
    .store(in: &cancellables)

nombres.send("Carlos")
edades.send(28) // "Carlos tiene 28 años"
```

### 3. Subscribers y Gestión de Memoria

#### El contrato de AnyCancellable

Cada suscripción en Combine retorna un `AnyCancellable`. Si no lo almacenas, la suscripción se cancela inmediatamente. Este es el **error #1** de los principiantes.

```swift
class MiViewModel {
    // ❌ MAL: La suscripción muere inmediatamente
    func malaIdea() {
        Just("Hola")
            .sink { print($0) } // Nunca se ejecuta con publishers async
    }
    
    // ✅ BIEN: Almacenar la suscripción
    private var cancellables = Set<AnyCancellable>()
    
    func buenaIdea() {
        Just("Hola")
            .sink { print($0) }
            .store(in: &cancellables)
    }
}
```

#### sink vs assign

```swift
class UserViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var isValid: Bool = false
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // sink: Control total sobre qué hacer con el valor
        $username
            .map { $0.count >= 3 }
            .sink { [weak self] isValid in
                self?.isValid = isValid
            }
            .store(in: &cancellables)
        
        // assign: Asigna directamente a una propiedad (más limpio)
        // ⚠️ Cuidado: assign(to:on:) puede causar retain cycles
        $username
            .map { $0.count >= 3 }
            .assign(to: &$isValid) // Versión segura con & (no necesita cancellable)
    }
}
```

## Ejemplo Práctico Completo: Buscador de Productos

Este ejemplo integra todo lo aprendido en un caso real — un buscador como el que encontrarías en apps de e-commerce populares en LATAM:

```swift
import Combine
import Foundation

// MARK: - Modelos
struct Producto: Codable, Identifiable {
    let id: Int
    let nombre: String
    let precio: Double
    let moneda: String
}

struct RespuestaBusqueda: Codable {
    let resultados: [Producto]
}

// MARK: - Capa de Red
enum NetworkError: Error, LocalizedError {
    case urlInvalida
    case sinConexion
    case respuestaInvalida
    case decodificacionFallida
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida: return "La URL no es válida"
        case .sinConexion: return "Sin conexión a internet"
        case .respuestaInvalida: return "Respuesta inesperada del servidor"
        case .decodificacionFallida: return "Error al procesar los datos"
        }
    }
}

protocol ProductoServiceProtocol {
    func buscar(query: String) -> AnyPublisher<[Producto], NetworkError>
}

class ProductoService: ProductoServiceProtocol {
    private let session: URLSession
    private let baseURL = "https://api.mitienda.com/v1"
    
    init(session: URLSession = .shared) {
        self.session = session
    }
    
    func buscar(query: String) -> AnyPublisher<[Producto], NetworkError> {
        guard let queryEncoded = query.addingPercentEncoding(
            withAllowedCharacters: .urlQueryAllowed
        ),
        let url = URL(string: "\(baseURL)/productos?q=\(queryEncoded)") else {
            return Fail(error: NetworkError.urlInvalida)
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: url)
            .mapError { _ in NetworkError.sinConexion }
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw NetworkError.respuestaInvalida
                }
                return data
            }
            .mapError { error in
                (error as? NetworkError) ?? .respuestaInvalida
            }
            .decode(type: RespuestaBusqueda.self, decoder: JSONDecoder())
            .mapError { _ in NetworkError.decodificacionFallida }
            .map(\.resultados)
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// MARK: - ViewModel
enum EstadoBusqueda: Equatable {
    case inactivo
    case cargando
    case resultados([Producto])
    case vacio
    case error(String)
    
    static func == (lhs: EstadoBusqueda, rhs: EstadoBusqueda) -> Bool {
        switch (lhs, rhs) {
        case (.inactivo, .inactivo), (.cargando, .cargando), (.vacio, .vacio):
            return true
        case let (.error(a), .error(b)):
            return a == b
        default:
            return false
        }
    }
}

class BuscadorViewModel: ObservableObject {
    // MARK: - Inputs
    @Published var textoBusqueda: String = ""
    
    // MARK: - Outputs
    @Published private(set) var estado: EstadoBusqueda = .inactivo
    @Published private(set) var historialBusquedas: [String] = []
    
    private let servicio: ProductoServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    
    init(servicio: ProductoServiceProtocol = ProductoService()) {
        self.servicio = servicio
        configurarPipeline()
    }
    
    private func configurarPipeline() {
        $textoBusqueda
            // 1. Esperar que el usuario deje de escribir
            .debounce(for: .milliseconds(400), scheduler: RunLoop.main)
            // 2. No buscar si el texto no cambió
            .removeDuplicates()
            // 3. Limpiar espacios
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            // 4. Decidir qué hacer
            .handleEvents(receiveOutput: { [weak self] query in
                if query.count >= 2 {
                    self?.estado = .cargando
                } else {
                    self?.estado = .inactivo
                }
            })
            // 5. Solo buscar si hay al menos 2 caracteres
            .filter { $0.count >= 2 }
            // 6. Cancelar búsqueda anterior y lanzar nueva
            .flatMap { [weak self] query -> AnyPublisher<[Producto], Never> in
                guard let self = self else {
                    return Just([]).eraseToAnyPublisher()
                }
                
                // Guardar en historial
                if !self.historialBusquedas.contains(query) {
                    self.historialBusquedas.append(query)
                    // Mantener solo las últimas 10
                    if self.historialBusquedas.count > 10 {
                        self.historial