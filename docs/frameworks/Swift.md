---
sidebar_position: 1
title: Swift
---

# Swift

## ¿Qué es Swift?

Swift es el lenguaje de programación moderno, seguro y de alto rendimiento creado por Apple en 2014 para el desarrollo de aplicaciones en todas sus plataformas: iOS, macOS, watchOS, tvOS y visionOS. Nació como sucesor de Objective-C con el objetivo de ofrecer una sintaxis más clara, expresiva y menos propensa a errores, sin sacrificar la velocidad de ejecución. Swift es un lenguaje compilado, de tipado estático con inferencia de tipos, que combina paradigmas de programación orientada a objetos, programación funcional y programación orientada a protocolos.

Desde su lanzamiento como proyecto de código abierto en 2015, Swift ha evolucionado rápidamente, incorporando características avanzadas como concurrencia estructurada con `async/await`, macros, `Result Builders` y un sistema de genéricos cada vez más potente. Su diseño prioriza la seguridad — eliminando categorías completas de errores como los punteros nulos, los desbordamientos de enteros y los accesos a memoria no inicializada — mientras mantiene un rendimiento comparable al de C y C++.

Swift no se limita al ecosistema Apple: también se utiliza en desarrollo del lado del servidor (con frameworks como Vapor y Hummingbird), en scripts de línea de comandos y en proyectos multiplataforma. Sin embargo, su uso principal y donde más brilla es en el desarrollo de aplicaciones para las plataformas de Apple, donde está profundamente integrado con frameworks como SwiftUI, UIKit, Combine, Foundation y todos los SDKs nativos.

## Casos de uso principales

- **Desarrollo de aplicaciones iOS/iPadOS**: Es el lenguaje estándar y recomendado por Apple para crear apps para iPhone e iPad, desde aplicaciones sencillas hasta complejas aplicaciones empresariales.

- **Desarrollo de interfaces con SwiftUI**: Swift es el único lenguaje compatible con SwiftUI, el framework declarativo de Apple para construir interfaces de usuario modernas y reactivas en todas las plataformas.

- **Aplicaciones macOS nativas**: Permite crear aplicaciones de escritorio de alto rendimiento aprovechando todas las APIs del sistema operativo Mac.

- **Desarrollo para watchOS y tvOS**: Swift es el lenguaje principal para crear experiencias en Apple Watch y Apple TV, donde el rendimiento y la eficiencia energética son críticos.

- **Desarrollo del lado del servidor (Server-Side Swift)**: Con frameworks como Vapor, Swift se utiliza para construir APIs REST, microservicios y backends con excelente rendimiento y seguridad de tipos.

- **Herramientas de línea de comandos y automatización**: Swift puede usarse para crear scripts y herramientas CLI aprovechando `Swift Argument Parser` y el acceso directo a las APIs del sistema.

## Instalación y configuración

### Requisitos previos

Swift viene incluido con **Xcode**, el entorno de desarrollo integrado de Apple. No requiere instalación independiente para desarrollo en plataformas Apple.

```bash
# Verificar la versión de Swift instalada
swift --version

# Ejemplo de salida:
# swift-driver version: 1.90.11.1 Apple Swift version 5.10
```

### Crear un nuevo proyecto

```bash
# Crear un proyecto de línea de comandos
mkdir MiProyecto && cd MiProyecto
swift package init --type executable

# Crear un proyecto como librería
swift package init --type library

# Compilar y ejecutar
swift build
swift run
```

### Estructura de un Package.swift

```swift
// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "MiProyecto",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "MiProyecto",
            targets: ["MiProyecto"]
        ),
    ],
    dependencies: [
        // Dependencias externas se declaran aquí
    ],
    targets: [
        .target(
            name: "MiProyecto",
            dependencies: []
        ),
        .testTarget(
            name: "MiProyectoTests",
            dependencies: ["MiProyecto"]
        ),
    ]
)
```

### Import principal

```swift
import Foundation  // Tipos fundamentales, colecciones, networking, fechas, etc.
import SwiftUI     // Framework de interfaz declarativa
import UIKit       // Framework de interfaz imperativa (iOS)
import Combine     // Programación reactiva
```

## Conceptos clave

### 1. Seguridad de tipos y opcionales

Swift utiliza un sistema de tipos estricto donde la ausencia de valor se representa explícitamente con **opcionales** (`Optional<T>` o `T?`). Esto elimina por completo la categoría de errores por referencia nula, obligando al desarrollador a manejar la ausencia de valor de forma consciente y deliberada.

```swift
var nombre: String? = nil  // Puede contener un String o nil
var edad: Int = 25         // Siempre contiene un Int, nunca nil

// Desenvoltura segura con if let
if let nombreDesenvuelto = nombre {
    print("Hola, \(nombreDesenvuelto)")
} else {
    print("No se proporcionó nombre")
}

// Guard let para salida temprana
func saludar(nombre: String?) {
    guard let nombre = nombre else {
        print("Nombre requerido")
        return
    }
    print("Hola, \(nombre)")
}
```

### 2. Programación Orientada a Protocolos (POP)

En lugar de depender exclusivamente de la herencia de clases, Swift promueve la **programación orientada a protocolos**. Los protocolos definen contratos que cualquier tipo puede adoptar, y las extensiones de protocolo proporcionan implementaciones por defecto, logrando polimorfismo sin los problemas de la herencia múltiple.

```swift
protocol Describible {
    var descripcion: String { get }
}

extension Describible {
    var descripcion: String {
        return "Instancia de \(type(of: self))"
    }
}

struct Producto: Describible {
    let nombre: String
    var descripcion: String {
        return "Producto: \(nombre)"
    }
}
```

### 3. Tipos de valor vs tipos de referencia

Swift diferencia claramente entre **structs** (tipos de valor, se copian) y **clases** (tipos de referencia, se comparten). Esta distinción es fundamental para entender el manejo de memoria, la concurrencia y las decisiones de diseño en Swift. Las structs son preferidas por defecto por su predecibilidad y seguridad en contextos concurrentes.

```swift
// Tipo de valor: cada variable tiene su propia copia
struct Punto {
    var x: Double
    var y: Double
}

var a = Punto(x: 1, y: 2)
var b = a       // b es una copia independiente
b.x = 10       // a.x sigue siendo 1

// Tipo de referencia: comparten la misma instancia
class Persona {
    var nombre: String
    init(nombre: String) { self.nombre = nombre }
}

let persona1 = Persona(nombre: "Ana")
let persona2 = persona1       // Ambos apuntan al mismo objeto
persona2.nombre = "María"     // persona1.nombre también es "María"
```

### 4. Enumeraciones con valores asociados

Las enumeraciones de Swift van mucho más allá de simples constantes numéricas. Pueden contener **valores asociados** de cualquier tipo, métodos, propiedades computadas y conformar protocolos, convirtiéndolas en una herramienta poderosísima para modelar estados y dominios complejos.

```swift
enum ResultadoRed {
    case exito(datos: Data, codigoHTTP: Int)
    case error(Error)
    case sinConexion
    
    var esExitoso: Bool {
        if case .exito = self { return true }
        return false
    }
}
```

### 5. Concurrencia estructurada (async/await)

Desde Swift 5.5, el lenguaje incluye soporte nativo para **concurrencia estructurada** con `async/await`, `Task`, `TaskGroup` y **actores**. Este modelo reemplaza los callbacks anidados por código secuencial legible y elimina categorías completas de errores de concurrencia en tiempo de compilación.

```swift
func obtenerUsuario(id: Int) async throws -> Usuario {
    let url = URL(string: "https://api.ejemplo.com/usuarios/\(id)")!
    let (datos, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(Usuario.self, from: datos)
}
```

### 6. Closures y funciones de orden superior

Los **closures** (también llamados lambdas o bloques) son funciones anónimas que capturan valores de su contexto. Swift ofrece una sintaxis extremadamente concisa para closures y las colecciones estándar incluyen funciones de orden superior como `map`, `filter`, `reduce`, `compactMap` y `flatMap`.

```swift
let numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

let paresMayoresA5 = numeros
    .filter { $0 % 2 == 0 }     // [2, 4, 6, 8, 10]
    .filter { $0 > 5 }           // [6, 8, 10]
    .map { "Número: \($0)" }     // ["Número: 6", "Número: 8", "Número: 10"]
```

## Ejemplo básico

```swift
import Foundation

// ==========================================================
// Ejemplo básico: Gestión de una lista de tareas en memoria
// ==========================================================

// Modelo de datos usando struct (tipo de valor)
struct Tarea: Identifiable, CustomStringConvertible {
    let id: UUID
    var titulo: String
    var completada: Bool
    let fechaCreacion: Date
    
    // Inicializador con valores por defecto
    init(titulo: String, completada: Bool = false) {
        self.id = UUID()
        self.titulo = titulo
        self.completada = completada
        self.fechaCreacion = Date()
    }
    
    // Conformidad con CustomStringConvertible para impresión legible
    var description: String {
        let estado = completada ? "✅" : "⬜️"
        return "\(estado) \(titulo)"
    }
}

// Gestor de tareas con funcionalidades básicas
struct GestorDeTareas {
    // Colección privada de tareas
    private(set) var tareas: [Tarea] = []
    
    // Agregar una nueva tarea
    mutating func agregar(titulo: String) {
        let nuevaTarea = Tarea(titulo: titulo)
        tareas.append(nuevaTarea)
        print("📌 Tarea agregada: \(titulo)")
    }
    
    // Marcar una tarea como completada por su índice
    mutating func completar(indice: Int) {
        guard tareas.indices.contains(indice) else {
            print("❌ Índice fuera de rango")
            return
        }
        tareas[indice].completada = true
        print("✅ Tarea completada: \(tareas[indice].titulo)")
    }
    
    // Obtener tareas pendientes usando filter
    var pendientes: [Tarea] {
        tareas.filter { !$0.completada }
    }
    
    // Mostrar resumen
    func mostrarResumen() {
        print("\n📋 Lista de tareas (\(tareas.count) total, \(pendientes.count) pendientes):")
        print(String(repeating: "-", count: 50))
        for (indice, tarea) in tareas.enumerated() {
            print("  \(indice). \(tarea)")
        }
        print(String(repeating: "-", count: 50))
    }
}

// --- Uso ---
var gestor = GestorDeTareas()
gestor.agregar(titulo: "Estudiar Swift")
gestor.agregar(titulo: "Crear proyecto en Xcode")
gestor.agregar(titulo: "Implementar modelo de datos")
gestor.agregar(titulo: "Escribir tests unitarios")

gestor.completar(indice: 0)
gestor.completar(indice: 1)

gestor.mostrarResumen()

// Salida:
// 📋 Lista de tareas (4 total, 2 pendientes):
// --------------------------------------------------
//   0. ✅ Estudiar Swift
//   1. ✅ Crear proyecto en Xcode
//   2. ⬜️ Implementar modelo de datos
//   3. ⬜️ Escribir tests unitarios
// --------------------------------------------------
```

## Ejemplo intermedio

```swift
import Foundation

// ================================================================
// Ejemplo intermedio: Cliente de API REST genérico con async/await
// Incluye manejo robusto de errores, decodificación y genéricos
// ================================================================

// MARK: - Errores de red tipados

/// Enumeración que modela todos los posibles errores de red
enum ErrorDeRed: LocalizedError {
    case urlInvalida(String)
    case sinConexion
    case respuestaInvalida(codigoHTTP: Int)
    case decodificacionFallida(Error)
    case desconocido(Error)
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida(let url):
            return "La URL proporcionada no es válida: \(url)"
        case .sinConexion:
            return "No hay conexión a Internet disponible"
        case .respuestaInvalida(let codigo):
            return "El servidor respondió con código HTTP \(codigo)"
        case .decodificacionFallida(let error):
            return "Error al decodificar la respuesta: \(error.localizedDescription)"
        case .desconocido(let error):
            return "Error inesperado: \(error.localizedDescription)"
        }
    }
}

// MARK: - Modelos de datos

/// Modelo de usuario que viene de una API REST
struct Usuario: Codable, Identifiable {
    let id: Int
    let nombre: String
    let email: String
    let telefono: String
    
    // Mapeo de claves JSON a propiedades Swift
    enum CodingKeys: String, CodingKey {
        case id
        case nombre = "name"
        case email
        case telefono = "phone"
    }
}

/// Modelo de publicación asociada a un usuario
struct Publicacion: Codable, Identifiable {
    let id: Int
    let idUsuario: Int
    let titulo: String
    let cuerpo: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case idUsuario = "userId"
        case titulo = "title"
        case cuerpo = "body"
    }
}

// MARK: - Protocolo de servicio de red

/// Protocolo que define las capacidades de un cliente HTTP
protocol ServicioDeRed {
    func obtener<T: Decodable>(desde urlString: String) async throws -> T
    func obtener<T: Decodable>(desde urlString: String) async throws -> [T]
}

// MARK: - Implementación del cliente API

/// Cliente HTTP genérico y reutilizable
final class ClienteAPI: ServicioDeRed {
    
    // Sesión de URL configurada (inyectable para testing)
    private let sesion: URLSession
    private let decodificador: JSONDecoder
    
    init(sesion: URLSession =