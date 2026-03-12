---
sidebar_position: 1
title: Combine
---

# Combine

## ¿Qué es Combine?

Combine es el framework reactivo nativo de Apple, introducido en **WWDC 2019** junto con iOS 13, que proporciona una API declarativa para procesar valores a lo largo del tiempo. En esencia, Combine permite representar flujos de datos asíncronos como secuencias de valores que pueden ser transformados, filtrados, combinados y consumidos de manera elegante y predecible. Es la respuesta de Apple a librerías como RxSwift y ReactiveSwift, pero integrada directamente en el ecosistema del sistema operativo.

El framework se basa en tres pilares fundamentales: **Publishers** (publicadores que emiten valores), **Operators** (operadores que transforman esos valores) y **Subscribers** (suscriptores que consumen los valores finales). Esta arquitectura permite construir cadenas de procesamiento de datos que reaccionan automáticamente a los cambios, eliminando gran parte del código boilerplate asociado a callbacks, delegados y notificaciones.

Combine es especialmente poderoso cuando se combina con **SwiftUI**, ya que ambos frameworks fueron diseñados para trabajar juntos. Sin embargo, también es perfectamente utilizable con UIKit y cualquier otra parte del ecosistema Apple. Su uso es recomendable en cualquier escenario donde necesites manejar eventos asíncronos de forma coordinada: llamadas de red, validación de formularios, sincronización de datos en tiempo real, temporizadores, notificaciones del sistema y mucho más.

## Casos de uso principales

- **Llamadas de red y consumo de APIs REST:** Combine se integra nativamente con `URLSession`, permitiendo encadenar peticiones HTTP, transformar respuestas JSON y manejar errores de forma declarativa sin pirámides de callbacks.

- **Validación de formularios en tiempo real:** Permite observar múltiples campos de texto simultáneamente, combinar sus valores, aplicar reglas de validación y habilitar o deshabilitar botones de envío de forma reactiva.

- **Sincronización de estado en arquitecturas MVVM:** Los ViewModels pueden exponer `@Published` properties que la vista observa automáticamente, creando un flujo de datos unidireccional limpio y predecible.

- **Debounce en búsquedas:** Cuando el usuario escribe en un campo de búsqueda, Combine permite esperar a que deje de teclear (debounce), eliminar duplicados y ejecutar la búsqueda solo cuando sea necesario, reduciendo llamadas innecesarias al servidor.

- **Coordinación de múltiples operaciones asíncronas:** Permite ejecutar varias peticiones en paralelo y combinar sus resultados cuando todas hayan terminado (`CombineLatest`, `Zip`, `Merge`), sin caer en callback hell.

- **Reemplazo de NotificationCenter, KVO y Target-Action:** Combine ofrece publishers nativos para `NotificationCenter`, Key-Value Observing y eventos de controles UIKit, unificando todos los patrones de observación bajo una misma API.

## Instalación y configuración

Combine es un **framework nativo de Apple** incluido en el SDK a partir de iOS 13, macOS 10.15, tvOS 13 y watchOS 6. No requiere instalación mediante gestores de paquetes como Swift Package Manager, CocoaPods o Carthage.

### Requisitos mínimos

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 13.0          |
| macOS      | 10.15         |
| tvOS       | 13.0          |
| watchOS    | 6.0           |
| Xcode      | 11.0+         |
| Swift      | 5.1+          |

### Import necesario

Para utilizar Combine en cualquier archivo Swift, simplemente añade el import correspondiente:

```swift
import Combine
```

### Permisos y configuración adicional

Combine **no requiere** permisos en `Info.plist` ni configuración adicional en el proyecto. Al ser parte del SDK del sistema, está disponible inmediatamente tras importarlo. Solo debes asegurarte de que el deployment target de tu proyecto sea iOS 13.0 o superior.

```swift
// En cualquier archivo donde necesites Combine
import Combine
import Foundation // Generalmente ya importado

// Si trabajas con SwiftUI, Combine se importa implícitamente
import SwiftUI // Incluye acceso a @Published, ObservableObject, etc.
```

## Conceptos clave

### 1. Publisher (Publicador)

Un `Publisher` es un protocolo que define un tipo capaz de emitir una secuencia de valores a lo largo del tiempo. Cada publisher declara dos tipos asociados: el tipo de **Output** (valores que emite) y el tipo de **Failure** (errores que puede producir). Un publisher puede emitir cero o más valores y eventualmente completar con éxito o con un error.

```swift
// Ejemplo: un publisher que emite enteros y nunca falla
let numbersPublisher: AnyPublisher<Int, Never> = [1, 2, 3, 4, 5].publisher.eraseToAnyPublisher()
```

### 2. Subscriber (Suscriptor)

Un `Subscriber` es quien recibe los valores emitidos por un publisher. El subscriber más común es `sink`, que permite definir closures para manejar tanto los valores recibidos como la completación del flujo. Otro subscriber importante es `assign`, que asigna valores directamente a una propiedad de un objeto.

### 3. Operator (Operador)

Los operadores son métodos que se aplican sobre un publisher y devuelven un **nuevo publisher** transformado. Combine incluye decenas de operadores: `map`, `filter`, `flatMap`, `debounce`, `removeDuplicates`, `combineLatest`, `merge`, `zip`, `catch`, `retry`, entre muchos otros. Estos operadores se encadenan para formar pipelines de procesamiento.

### 4. Subject

Un `Subject` es un tipo especial de publisher al que puedes **enviar valores manualmente**. Existen dos tipos principales:
- **`PassthroughSubject`**: No almacena valores. Solo retransmite los valores que recibe a sus suscriptores activos.
- **`CurrentValueSubject`**: Almacena el último valor emitido y lo envía inmediatamente a cualquier nuevo suscriptor.

### 5. AnyCancellable y gestión de memoria

Cuando te suscribes a un publisher, recibes un objeto `AnyCancellable`. Este objeto **debe almacenarse** mientras quieras que la suscripción permanezca activa. Cuando el `AnyCancellable` se desaloca o se llama a `.cancel()`, la suscripción se cancela automáticamente. Es el mecanismo fundamental para evitar fugas de memoria.

### 6. @Published y ObservableObject

El property wrapper `@Published` convierte cualquier propiedad en un publisher que emite el nuevo valor cada vez que la propiedad cambia. Combinado con el protocolo `ObservableObject`, permite que SwiftUI observe automáticamente los cambios en un ViewModel y actualice la interfaz.

## Ejemplo básico

```swift
import Combine

// MARK: - Ejemplo básico: Suscripción simple a un publisher

class EjemploBasico {
    // Almacén de suscripciones para evitar que se cancelen prematuramente
    var cancellables = Set<AnyCancellable>()
    
    func ejecutar() {
        // 1. Crear un publisher a partir de un array de números
        let numerosPublisher = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].publisher
        
        // 2. Aplicar operadores para transformar el flujo
        numerosPublisher
            .filter { $0 % 2 == 0 }          // Filtrar solo números pares
            .map { $0 * $0 }                   // Elevar al cuadrado
            .sink(
                receiveCompletion: { completion in
                    switch completion {
                    case .finished:
                        print("✅ El flujo se completó exitosamente")
                    case .failure(let error):
                        print("❌ Error: \(error)")
                    }
                },
                receiveValue: { valor in
                    // Se imprimirá: 4, 16, 36, 64, 100
                    print("Valor recibido: \(valor)")
                }
            )
            .store(in: &cancellables) // Almacenar la suscripción
    }
    
    func ejemploSubject() {
        // Crear un PassthroughSubject para enviar valores manualmente
        let subject = PassthroughSubject<String, Never>()
        
        // Suscribirse al subject
        subject
            .sink { valor in
                print("Mensaje recibido: \(valor)")
            }
            .store(in: &cancellables)
        
        // Enviar valores manualmente
        subject.send("Hola")
        subject.send("Mundo")
        subject.send("desde Combine")
        
        // Completar el subject
        subject.send(completion: .finished)
    }
    
    func ejemploCurrentValue() {
        // CurrentValueSubject almacena el último valor
        let temperaturaActual = CurrentValueSubject<Double, Never>(20.0)
        
        // Al suscribirse, recibe inmediatamente el valor actual (20.0)
        temperaturaActual
            .sink { temp in
                print("Temperatura: \(temp)°C")
            }
            .store(in: &cancellables)
        
        // Actualizar el valor
        temperaturaActual.send(22.5)
        temperaturaActual.send(25.0)
        
        // Acceder al valor actual directamente
        print("Valor actual: \(temperaturaActual.value)°C") // 25.0
    }
}
```

## Ejemplo intermedio

```swift
import Combine
import Foundation

// MARK: - Ejemplo intermedio: Servicio de red con Combine

// Modelo de datos
struct Usuario: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
    let username: String
}

// Errores personalizados del servicio de red
enum NetworkError: Error, LocalizedError {
    case urlInvalida
    case respuestaInvalida(statusCode: Int)
    case decodificacionFallida
    case sinConexion
    case desconocido(Error)
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida:
            return "La URL proporcionada no es válida"
        case .respuestaInvalida(let code):
            return "El servidor respondió con el código: \(code)"
        case .decodificacionFallida:
            return "No se pudo interpretar la respuesta del servidor"
        case .sinConexion:
            return "No hay conexión a internet"
        case .desconocido(let error):
            return "Error desconocido: \(error.localizedDescription)"
        }
    }
}

// Servicio de red genérico usando Combine
class NetworkService {
    private let session: URLSession
    private let decoder: JSONDecoder
    
    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
    }
    
    /// Realiza una petición GET y decodifica la respuesta al tipo especificado
    func fetch<T: Decodable>(url: String) -> AnyPublisher<T, NetworkError> {
        // Validar que la URL sea correcta
        guard let url = URL(string: url) else {
            return Fail(error: NetworkError.urlInvalida)
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: url)
            // Validar que la respuesta HTTP sea exitosa (200-299)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw NetworkError.respuestaInvalida(statusCode: -1)
                }
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw NetworkError.respuestaInvalida(statusCode: httpResponse.statusCode)
                }
                return data
            }
            // Decodificar el JSON al tipo esperado
            .decode(type: T.self, decoder: decoder)
            // Mapear cualquier error al tipo NetworkError
            .mapError { error in
                if let networkError = error as? NetworkError {
                    return networkError
                } else if error is DecodingError {
                    return .decodificacionFallida
                } else {
                    return .desconocido(error)
                }
            }
            // Asegurar que los valores se reciben en el hilo principal
            .receive(on: DispatchQueue.main)
            // Borrar el tipo concreto del publisher
            .eraseToAnyPublisher()
    }
}

// Repositorio que usa el servicio de red
class UserRepository {
    private let networkService: NetworkService
    private var cancellables = Set<AnyCancellable>()
    
    // Cache simple en memoria
    private let cachedUsers = CurrentValueSubject<[Usuario]?, Never>(nil)
    
    init(networkService: NetworkService = NetworkService()) {
        self.networkService = networkService
    }
    
    /// Obtiene la lista de usuarios, usando cache si está disponible
    func obtenerUsuarios(forzarRecarga: Bool = false) -> AnyPublisher<[Usuario], NetworkError> {
        // Si hay datos en cache y no se fuerza la recarga, devolver el cache
        if let cached = cachedUsers.value, !forzarRecarga {
            return Just(cached)
                .setFailureType(to: NetworkError.self)
                .eraseToAnyPublisher()
        }
        
        // Si no hay cache, hacer la petición
        let publisher: AnyPublisher<[Usuario], NetworkError> = networkService
            .fetch(url: "https://jsonplaceholder.typicode.com/users")
        
        return publisher
            .handleEvents(receiveOutput: { [weak self] usuarios in
                // Guardar en cache cuando se reciban los datos
                self?.cachedUsers.send(usuarios)
            })
            .eraseToAnyPublisher()
    }
    
    /// Busca usuarios por nombre con debounce integrado
    func buscarUsuarios(termino: AnyPublisher<String, Never>) -> AnyPublisher<[Usuario], Never> {
        return termino
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .combineLatest(cachedUsers.compactMap { $0 })
            .map { termino, usuarios in
                guard !termino.isEmpty else { return usuarios }
                return usuarios.filter { usuario in
                    usuario.name.localizedCaseInsensitiveContains(termino) ||
                    usuario.email.localizedCaseInsensitiveContains(termino)
                }
            }
            .eraseToAnyPublisher()
    }
}

// MARK: - Ejemplo de uso

class EjemploIntermedio {
    private let repository = UserRepository()
    private var cancellables = Set<AnyCancellable>()
    
    func cargarUsuarios() {
        repository.obtenerUsuarios()
            .sink(
                receiveCompletion: { completion in
                    switch completion {
                    case .finished:
                        print("✅ Carga completada")
                    case .failure(let error):
                        print("❌ Error: \(error.localizedDescription)")
                    }
                },
                receiveValue: { usuarios in
                    print("📋 Se cargaron \(usuarios.count) usuarios:")
                    usuarios.forEach { usuario in
                        print("  