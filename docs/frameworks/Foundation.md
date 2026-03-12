---
sidebar_position: 1
title: Foundation
---

# Foundation

## ¿Qué es Foundation?

Foundation es el framework fundamental de Apple que proporciona la capa base de funcionalidad para todas las aplicaciones en el ecosistema Apple (iOS, macOS, watchOS, tvOS y visionOS). Es, literalmente, los cimientos sobre los que se construye cualquier aplicación. Ofrece tipos de datos primitivos, colecciones, manejo de fechas, operaciones de red, gestión de archivos, concurrencia, serialización y mucho más. Sin Foundation, prácticamente ninguna aplicación podría funcionar.

Este framework define las clases raíz, los protocolos fundamentales y los tipos de valor que se utilizan en todo el SDK de Apple. Desde algo tan simple como una cadena de texto (`String`, que se conecta con `NSString`) hasta operaciones complejas como peticiones HTTP (`URLSession`), codificación/decodificación JSON (`JSONEncoder`/`JSONDecoder`), notificaciones entre componentes (`NotificationCenter`) y manejo de fechas y calendarios (`Date`, `Calendar`, `DateFormatter`). Foundation es omnipresente: se importa implícita o explícitamente en prácticamente cada archivo Swift de cualquier proyecto.

Su importancia radica en que abstrae complejidades del sistema operativo y ofrece APIs consistentes y seguras. Antes de buscar librerías de terceros para tareas como parsear JSON, manejar fechas, realizar peticiones de red o trabajar con el sistema de archivos, todo desarrollador iOS debería dominar las herramientas que Foundation pone a su disposición. Es el primer framework que cualquier desarrollador Apple debe conocer en profundidad.

## Casos de uso principales

- **Networking y comunicación con APIs REST**: `URLSession` permite realizar peticiones HTTP/HTTPS, descargar archivos, subir datos y manejar autenticación. Es la base de toda comunicación de red en iOS sin dependencias externas.

- **Serialización y deserialización de datos (JSON, Property Lists)**: `JSONEncoder`, `JSONDecoder`, `PropertyListEncoder` y `PropertyListDecoder` permiten convertir modelos Swift a/desde formatos de intercambio de datos de manera nativa y con seguridad de tipos gracias al protocolo `Codable`.

- **Persistencia y manejo del sistema de archivos**: `FileManager`, `UserDefaults` y los tipos `Data` y `URL` permiten leer, escribir, mover y eliminar archivos, así como almacenar preferencias del usuario de forma sencilla.

- **Manejo de fechas, calendarios y zonas horarias**: `Date`, `Calendar`, `DateFormatter`, `DateComponents` y `RelativeDateTimeFormatter` cubren desde cálculos de diferencias entre fechas hasta formateo localizado para mostrar al usuario.

- **Concurrencia y operaciones en segundo plano**: `OperationQueue`, `Operation`, `DispatchQueue` (a través de libDispatch/GCD) y `Timer` permiten ejecutar tareas asíncronas, programar ejecuciones periódicas y gestionar dependencias entre operaciones.

- **Notificaciones y comunicación entre componentes**: `NotificationCenter` implementa el patrón Observer, permitiendo que partes desacopladas de la aplicación se comuniquen sin referencias directas entre sí. `KVO` (Key-Value Observing) añade otra capa de observación de cambios en propiedades.

## Instalación y configuración

Foundation viene integrado de forma nativa en todas las plataformas Apple. **No requiere instalación adicional**, ni CocoaPods, ni Swift Package Manager, ni ninguna configuración especial.

### Import necesario

```swift
import Foundation
```

> **Nota importante**: Cuando importas `UIKit` o `SwiftUI`, Foundation se importa automáticamente de forma implícita. Sin embargo, en archivos que solo contienen lógica de negocio, modelos de datos o servicios (sin UI), es buena práctica importar únicamente `Foundation`.

### Permisos en Info.plist

Foundation en sí no requiere permisos especiales. Sin embargo, algunas de sus funcionalidades sí necesitan configuración adicional:

```xml
<!-- Para conexiones de red (URLSession) -->
<!-- En iOS 9+, App Transport Security está habilitado por defecto -->
<!-- Solo si necesitas conexiones HTTP no seguras (NO recomendado en producción): -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- Para acceder a documentos del usuario -->
<key>UIFileSharingEnabled</key>
<true/>
<key>LSSupportsOpeningDocumentsInPlace</key>
<true/>
```

### Configuración en un Package.swift (para Swift Packages)

```swift
// Foundation está disponible automáticamente, no necesitas declararla como dependencia
let package = Package(
    name: "MiModulo",
    platforms: [.iOS(.v15), .macOS(.v12)],
    targets: [
        .target(
            name: "MiModulo"
            // No es necesario listar Foundation en dependencies
        )
    ]
)
```

## Conceptos clave

### 1. Tipos de valor vs. tipos de referencia (Value Types vs. Reference Types)

Foundation ofrece dos familias paralelas de tipos. Los tipos de valor de Swift (`String`, `Array`, `Dictionary`, `Data`, `Date`, `URL`, `UUID`) y sus contrapartes de Objective-C basadas en clases (`NSString`, `NSArray`, `NSDictionary`, `NSData`, `NSDate`, `NSURL`, `NSUUID`). Los tipos de valor de Swift utilizan semántica de copia (copy-on-write) y son los preferidos en código Swift moderno por su seguridad en entornos concurrentes y su previsibilidad.

```swift
// Tipo de valor (Swift) - Preferido
var nombre: String = "Hola"
var copia = nombre
copia += " Mundo"
// nombre sigue siendo "Hola", copia es "Hola Mundo"

// Tipo de referencia (Objective-C bridge) - Evitar salvo necesidad
let nsNombre: NSMutableString = "Hola"
let referencia = nsNombre
referencia.append(" Mundo")
// Ambos apuntan al mismo objeto: "Hola Mundo"
```

### 2. Protocolo Codable (Encodable + Decodable)

`Codable` es la piedra angular de la serialización en Swift moderno. Permite que tus modelos de datos se conviertan automáticamente a/desde JSON, Property Lists y otros formatos. Se compone de dos protocolos: `Encodable` (para serializar) y `Decodable` (para deserializar). Cuando un tipo conforma ambos, se dice que es `Codable`.

```swift
struct Usuario: Codable {
    let id: Int
    let nombre: String
    let email: String
    let fechaRegistro: Date
    
    // CodingKeys personaliza el mapeo entre propiedades Swift y claves JSON
    enum CodingKeys: String, CodingKey {
        case id
        case nombre = "full_name"
        case email
        case fechaRegistro = "created_at"
    }
}
```

### 3. URLSession y el modelo de networking

`URLSession` es el sistema de networking de Foundation. Funciona con un modelo basado en tareas (`URLSessionTask`) que pueden ser de datos (`dataTask`), descarga (`downloadTask`) o subida (`uploadTask`). Soporta callbacks con closures, Combine publishers y `async/await` en Swift moderno. Gestiona automáticamente caché, cookies, autenticación y conexiones TLS.

### 4. RunLoop y el ciclo de eventos

El `RunLoop` es el mecanismo que mantiene viva una aplicación y procesa eventos de entrada (toques, temporizadores, puertos de red). El hilo principal siempre tiene un RunLoop activo. Entender los RunLoops es crucial para comprender por qué ciertos temporizadores no se ejecutan durante el scroll (`Timer` vs. `.common` mode) y cómo funciona la programación asíncrona en iOS.

### 5. NotificationCenter y el patrón Observer

`NotificationCenter` permite la comunicación desacoplada entre componentes. Un objeto puede publicar una notificación sin saber quién la recibirá, y múltiples observadores pueden suscribirse a la misma notificación. Es fundamental para responder a eventos del sistema (teclado aparece/desaparece, app entra a background, cambios de accesibilidad).

### 6. FileManager y el sandbox de la aplicación

Cada aplicación iOS opera dentro de un sandbox con directorios específicos: `Documents` (datos del usuario, respaldados en iCloud), `Library/Caches` (datos recuperables, no respaldados), `tmp` (datos temporales que el sistema puede eliminar). `FileManager` es la API para navegar y manipular este sistema de archivos.

## Ejemplo básico

```swift
import Foundation

// =============================================================
// Ejemplo básico: Tipos fundamentales de Foundation
// =============================================================

// MARK: - Manejo de Strings
let saludo = "¡Hola, desarrollador iOS!"
let mayusculas = saludo.uppercased()
let contieneiOS = saludo.contains("iOS") // true
let palabras = saludo.split(separator: " ") // ["¡Hola,", "desarrollador", "iOS!"]

print("Original: \(saludo)")
print("Mayúsculas: \(mayusculas)")
print("¿Contiene iOS?: \(contieneiOS)")
print("Palabras: \(palabras)")

// MARK: - Manejo de Fechas
let ahora = Date()
let calendario = Calendar.current

// Obtener componentes de la fecha actual
let componentes = calendario.dateComponents(
    [.year, .month, .day, .hour, .minute],
    from: ahora
)
print("\nFecha actual: \(componentes.day!)/\(componentes.month!)/\(componentes.year!)")

// Formatear fecha para mostrar al usuario
let formateador = DateFormatter()
formateador.locale = Locale(identifier: "es_ES")
formateador.dateStyle = .long
formateador.timeStyle = .short
print("Fecha formateada: \(formateador.string(from: ahora))")

// Calcular una fecha futura (30 días desde hoy)
if let fechaFutura = calendario.date(byAdding: .day, value: 30, to: ahora) {
    print("En 30 días: \(formateador.string(from: fechaFutura))")
}

// MARK: - Manejo de JSON básico con Codable
struct Tarea: Codable {
    let titulo: String
    let completada: Bool
    let prioridad: Int
}

let tarea = Tarea(titulo: "Aprender Foundation", completada: false, prioridad: 1)

// Codificar a JSON
let encoder = JSONEncoder()
encoder.outputFormatting = .prettyPrinted

do {
    let jsonData = try encoder.encode(tarea)
    if let jsonString = String(data: jsonData, encoding: .utf8) {
        print("\nJSON generado:")
        print(jsonString)
    }
    
    // Decodificar desde JSON
    let decoder = JSONDecoder()
    let tareaDecodificada = try decoder.decode(Tarea.self, from: jsonData)
    print("\nTarea decodificada: \(tareaDecodificada.titulo)")
} catch {
    print("Error de codificación: \(error.localizedDescription)")
}

// MARK: - UserDefaults para persistencia simple
let defaults = UserDefaults.standard
defaults.set("Carlos", forKey: "nombreUsuario")
defaults.set(25, forKey: "edad")
defaults.set(true, forKey: "notificacionesActivas")

// Leer valores guardados
let nombre = defaults.string(forKey: "nombreUsuario") ?? "Desconocido"
let edad = defaults.integer(forKey: "edad")
let notificaciones = defaults.bool(forKey: "notificacionesActivas")

print("\nUsuario: \(nombre), Edad: \(edad), Notificaciones: \(notificaciones)")

// MARK: - UUID para identificadores únicos
let identificador = UUID()
print("\nID único generado: \(identificador.uuidString)")
```

## Ejemplo intermedio

```swift
import Foundation

// =============================================================
// Ejemplo intermedio: Servicio de red completo con manejo de
// errores, modelos Codable avanzados y caché en disco
// =============================================================

// MARK: - Modelos de datos

/// Representa un post del blog con fechas y autor anidado
struct Post: Codable, Identifiable {
    let id: Int
    let titulo: String
    let cuerpo: String
    let autor: Autor
    let etiquetas: [String]
    let fechaPublicacion: Date
    let actualizado: Date?
    
    enum CodingKeys: String, CodingKey {
        case id
        case titulo = "title"
        case cuerpo = "body"
        case autor = "author"
        case etiquetas = "tags"
        case fechaPublicacion = "published_at"
        case actualizado = "updated_at"
    }
}

struct Autor: Codable {
    let id: Int
    let nombre: String
    let email: String
    let avatarURL: URL?
    
    enum CodingKeys: String, CodingKey {
        case id
        case nombre = "name"
        case email
        case avatarURL = "avatar_url"
    }
}

/// Respuesta paginada de la API
struct RespuestaPaginada<T: Codable>: Codable {
    let datos: [T]
    let paginaActual: Int
    let totalPaginas: Int
    let totalElementos: Int
    
    enum CodingKeys: String, CodingKey {
        case datos = "data"
        case paginaActual = "current_page"
        case totalPaginas = "total_pages"
        case totalElementos = "total_items"
    }
}

// MARK: - Errores personalizados

/// Errores específicos del servicio de red
enum ErrorDeRed: LocalizedError {
    case urlInvalida
    case sinConexion
    case respuestaInvalida(codigoHTTP: Int)
    case decodificacionFallida(detalle: String)
    case tiempoAgotado
    case desconocido(Error)
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida:
            return "La URL proporcionada no es válida."
        case .sinConexion:
            return "No hay conexión a Internet. Verifica tu red."
        case .respuestaInvalida(let codigo):
            return "El servidor respondió con código HTTP \(codigo)."
        case .decodificacionFallida(let detalle):
            return "Error al procesar los datos: \(detalle)"
        case .tiempoAgotado:
            return "La solicitud tardó demasiado. Intenta de nuevo."
        case .desconocido(let error):
            return "Error inesperado: \(error.localizedDescription)"
        }
    }
}

// MARK: - Servicio de Red

/// Servicio genérico de red con caché en disco y manejo robusto de errores
final class ServicioDeRed {
    
    // Configuración de la sesión con timeouts personalizados
    private let sesion: URLSession
    private let baseURL: URL
    private let decodificador: JSONDecoder
    private let fileManager = FileManager.default
    
    /// Directorio de caché dentro del sandbox de la app
    private var directorioCacheDisco: URL {
        let caches = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        let directorio = caches.append