---
sidebar_position: 1
title: URLSession
---

# URLSession

## ¿Qué es URLSession?

`URLSession` es el framework nativo de Apple para realizar peticiones de red en aplicaciones iOS, macOS, watchOS y tvOS. Es la piedra angular de toda comunicación HTTP/HTTPS en el ecosistema Apple y proporciona una API completa y altamente configurable para descargar y subir datos desde y hacia servidores remotos. Sin depender de librerías de terceros, `URLSession` ofrece todo lo necesario para interactuar con APIs REST, descargar archivos, gestionar autenticación y manejar tareas en segundo plano.

Internamente, `URLSession` gestiona un conjunto de tareas (`URLSessionTask`) que representan operaciones individuales de red. Cada tarea pasa por un ciclo de vida bien definido (suspendida, en ejecución, cancelada o completada) y puede ser monitoreada tanto mediante closures como mediante el patrón delegado. Apple ha ido evolucionando esta API a lo largo de los años, incorporando soporte nativo para `async/await` a partir de iOS 15 y macOS 12, lo que simplifica enormemente el código asíncrono.

Usar `URLSession` es la opción recomendada por Apple para cualquier operación de red. A diferencia de librerías populares como Alamofire, no requiere dependencias externas, se mantiene actualizada con cada versión del sistema operativo y ofrece integración profunda con el sistema, incluyendo descargas en segundo plano, políticas de caché del sistema y compatibilidad directa con App Transport Security (ATS). Todo desarrollador iOS debería dominar este framework antes de considerar alternativas de terceros.

## Casos de uso principales

- **Consumo de APIs REST**: Realizar peticiones GET, POST, PUT, PATCH y DELETE contra servicios web RESTful, enviando y recibiendo datos en formato JSON. Es el caso de uso más común en cualquier aplicación moderna.

- **Descarga de archivos**: Descargar imágenes, documentos, vídeos u otros recursos desde servidores remotos, con soporte para seguimiento de progreso y almacenamiento temporal o permanente en disco.

- **Subida de archivos (upload)**: Enviar archivos al servidor mediante peticiones multipart o mediante cuerpos de datos binarios, útil para funcionalidades como subir fotos de perfil o documentos.

- **Descargas en segundo plano**: Continuar descargas incluso cuando la aplicación pasa a segundo plano o es terminada por el sistema. Ideal para contenido multimedia pesado o sincronización de datos offline.

- **WebSockets**: A partir de iOS 13, `URLSession` soporta conexiones WebSocket bidireccionales para comunicación en tiempo real, útil en aplicaciones de chat, juegos multijugador o dashboards en vivo.

- **Autenticación y manejo de certificados**: Gestionar flujos de autenticación HTTP Basic, Digest, certificados SSL personalizados o autenticación por token mediante el sistema de delegados.

## Instalación y configuración

### Importación

`URLSession` forma parte del framework `Foundation`, que viene incluido en todos los proyectos de Xcode. No necesitas instalar ningún paquete adicional ni configurar gestores de dependencias:

```swift
import Foundation
```

### Configuración de App Transport Security (ATS)

Por defecto, iOS exige que todas las conexiones de red usen HTTPS. Si necesitas conectarte a un servidor HTTP sin cifrar (solo en desarrollo o casos excepcionales), debes configurar una excepción en `Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <!-- Permitir conexiones HTTP para un dominio específico (recomendado) -->
    <key>NSExceptionDomains</key>
    <dict>
        <key>miapi-desarrollo.local</key>
        <dict>
            <key>NSAllowsArbitraryLoads</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

> ⚠️ **Nunca** uses `NSAllowsArbitraryLoads` como clave global en producción. Apple puede rechazar tu app en la revisión de App Store.

### Permisos adicionales

Si tu aplicación realiza descargas en segundo plano, asegúrate de habilitar el modo **Background Modes** → **Background fetch** en las capacidades del target dentro de Xcode.

## Conceptos clave

### 1. URLSessionConfiguration

Define el comportamiento global de la sesión. Existen tres tipos principales:

- **`.default`**: Usa caché persistente en disco y almacena cookies. Es la configuración estándar para la mayoría de aplicaciones.
- **`.ephemeral`**: Similar a la navegación privada. No persiste caché, cookies ni credenciales en disco. Ideal para peticiones sensibles.
- **`.background(withIdentifier:)`**: Permite que las transferencias continúen cuando la app no está en primer plano. El sistema gestiona las tareas de forma independiente.

### 2. URLSessionTask

Es la unidad de trabajo dentro de una sesión. Existen cuatro subclases principales:

| Tipo | Uso |
|---|---|
| `URLSessionDataTask` | Peticiones estándar donde la respuesta se almacena en memoria |
| `URLSessionDownloadTask` | Descarga archivos directamente a disco |
| `URLSessionUploadTask` | Sube datos al servidor |
| `URLSessionWebSocketTask` | Comunicación bidireccional WebSocket |

### 3. URLRequest

Objeto que encapsula todos los detalles de una petición HTTP: URL, método, cabeceras, cuerpo, política de caché y timeout. Permite un control granular sobre cada petición individual.

### 4. URLResponse y HTTPURLResponse

`URLResponse` contiene metadatos de la respuesta del servidor. Su subclase `HTTPURLResponse` añade información específica del protocolo HTTP como el código de estado, las cabeceras de respuesta y el tipo MIME.

### 5. Async/Await vs Closures vs Delegados

`URLSession` ofrece tres patrones de uso:

- **Async/Await** (iOS 15+): El más moderno y legible. Ideal para código nuevo.
- **Closures (completion handlers)**: Clásico y compatible con versiones anteriores.
- **Delegados (`URLSessionDelegate`)**: Máximo control sobre cada fase de la petición. Necesario para descargas en segundo plano y autenticación personalizada.

### 6. Codable

El protocolo `Codable` (`Encodable` + `Decodable`) de Swift es el compañero natural de `URLSession`. Permite serializar objetos Swift a JSON para enviarlos al servidor y deserializar respuestas JSON directamente a structs o clases tipadas.

## Ejemplo básico

El siguiente ejemplo muestra cómo hacer una petición GET sencilla para obtener datos de una API pública usando `async/await`:

```swift
import Foundation

// MARK: - Modelo de datos
struct Post: Decodable {
    let id: Int
    let title: String
    let body: String
    let userId: Int
}

// MARK: - Petición GET básica con async/await
func obtenerPosts() async throws -> [Post] {
    // 1. Crear la URL
    guard let url = URL(string: "https://jsonplaceholder.typicode.com/posts") else {
        throw URLError(.badURL)
    }
    
    // 2. Realizar la petición usando la sesión compartida
    let (data, response) = try await URLSession.shared.data(from: url)
    
    // 3. Verificar que el código de estado sea exitoso
    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw URLError(.badServerResponse)
    }
    
    // 4. Decodificar el JSON a nuestro modelo
    let posts = try JSONDecoder().decode([Post].self, from: data)
    
    return posts
}

// MARK: - Uso
Task {
    do {
        let posts = try await obtenerPosts()
        print("Se obtuvieron \(posts.count) posts")
        posts.prefix(3).forEach { print("  → \($0.title)") }
    } catch {
        print("Error al obtener posts: \(error.localizedDescription)")
    }
}
```

## Ejemplo intermedio

Este ejemplo implementa un cliente de red reutilizable que soporta múltiples métodos HTTP, codificación/decodificación automática y manejo robusto de errores:

```swift
import Foundation

// MARK: - Errores personalizados de red
enum NetworkError: LocalizedError {
    case urlInvalida
    case sinConexion
    case respuestaInvalida(statusCode: Int)
    case decodificacionFallida(Error)
    case desconocido(Error)
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida:
            return "La URL proporcionada no es válida."
        case .sinConexion:
            return "No hay conexión a internet."
        case .respuestaInvalida(let codigo):
            return "El servidor respondió con código \(codigo)."
        case .decodificacionFallida(let error):
            return "Error al procesar la respuesta: \(error.localizedDescription)"
        case .desconocido(let error):
            return "Error inesperado: \(error.localizedDescription)"
        }
    }
}

// MARK: - Método HTTP
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

// MARK: - Cliente de red reutilizable
final class NetworkClient {
    
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    init(session: URLSession = .shared) {
        self.session = session
        
        // Configurar decoder con estrategia de claves snake_case
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.decoder.dateDecodingStrategy = .iso8601
        
        // Configurar encoder
        self.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy = .convertToSnakeCase
        self.encoder.dateEncodingStrategy = .iso8601
    }
    
    /// Realiza una petición de red genérica y decodifica la respuesta
    func request<T: Decodable>(
        url: String,
        method: HTTPMethod = .get,
        body: (any Encodable)? = nil,
        headers: [String: String]? = nil
    ) async throws -> T {
        
        // Construir URL
        guard let url = URL(string: url) else {
            throw NetworkError.urlInvalida
        }
        
        // Configurar la petición
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 30
        
        // Agregar cabeceras personalizadas
        headers?.forEach { clave, valor in
            request.setValue(valor, forHTTPHeaderField: clave)
        }
        
        // Codificar el cuerpo si existe
        if let body {
            request.httpBody = try encoder.encode(body)
        }
        
        // Ejecutar la petición
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError where error.code == .notConnectedToInternet {
            throw NetworkError.sinConexion
        } catch {
            throw NetworkError.desconocido(error)
        }
        
        // Validar respuesta HTTP
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.respuestaInvalida(statusCode: -1)
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.respuestaInvalida(statusCode: httpResponse.statusCode)
        }
        
        // Decodificar respuesta
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw NetworkError.decodificacionFallida(error)
        }
    }
}

// MARK: - Modelos
struct Usuario: Codable {
    let id: Int?
    let nombre: String
    let email: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case nombre = "name"
        case email
    }
}

// MARK: - Uso del cliente
let cliente = NetworkClient()

Task {
    do {
        // GET - Obtener usuarios
        let usuarios: [Usuario] = try await cliente.request(
            url: "https://jsonplaceholder.typicode.com/users"
        )
        print("Usuarios obtenidos: \(usuarios.count)")
        
        // POST - Crear un nuevo usuario
        let nuevoUsuario = Usuario(id: nil, nombre: "Carlos García", email: "carlos@ejemplo.com")
        let creado: Usuario = try await cliente.request(
            url: "https://jsonplaceholder.typicode.com/users",
            method: .post,
            body: nuevoUsuario
        )
        print("Usuario creado con ID: \(creado.id ?? 0)")
        
    } catch let error as NetworkError {
        print("Error de red: \(error.localizedDescription)")
    } catch {
        print("Error inesperado: \(error)")
    }
}
```

## Ejemplo avanzado

Este ejemplo implementa una arquitectura limpia MVVM con repositorio, protocolo para testing, manejo de estados de carga e integración lista para SwiftUI:

```swift
import Foundation
import SwiftUI

// MARK: - ═══════════════════════════════════════════
// CAPA DE RED (Networking Layer)
// MARK: - ═══════════════════════════════════════════

/// Protocolo que define un endpoint de API
protocol APIEndpoint {
    var baseURL: String { get }
    var path: String { get }
    var method: String { get }
    var headers: [String: String] { get }
    var queryItems: [URLQueryItem]? { get }
    var body: Data? { get }
}

extension APIEndpoint {
    var headers: [String: String] {
        ["Content-Type": "application/json", "Accept": "application/json"]
    }
    var queryItems: [URLQueryItem]? { nil }
    var body: Data? { nil }
    
    /// Construye el URLRequest a partir del endpoint
    func buildRequest() throws -> URLRequest {
        var components = URLComponents(string: baseURL + path)
        components?.queryItems = queryItems
        
        guard let url = components?.url else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = body
        request.timeoutInterval = 30
        headers.forEach { request.setValue($1, forHTTPHeaderField: $0) }
        
        return request
    }
}

/// Endpoints concretos para la API de artículos
enum ArticulosAPI: APIEndpoint {
    case listar(pagina: Int, porPagina: Int)
    case detalle(id: Int)
    case crear(titulo: String, contenido: String)
    case eliminar(id: Int)
    
    var baseURL: String { "https://jsonplaceholder.typicode.com" }
    
    var path: String {
        switch self {
        case .listar:
            return "/