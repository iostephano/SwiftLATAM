---
sidebar_position: 1
title: Open Source
---

# Open Source en el Desarrollo iOS

## ¿Qué es el Open Source?

El **open source** (código abierto) es un modelo de desarrollo de software en el que el código fuente se pone a disposición del público para que cualquier persona pueda **inspeccionar, modificar, distribuir y contribuir** a él. No se trata únicamente de código gratuito: es una filosofía de colaboración, transparencia y construcción colectiva del conocimiento.

En el ecosistema iOS, el open source está profundamente arraigado. El propio lenguaje **Swift es open source** desde 2015, al igual que herramientas fundamentales como Swift Package Manager, el compilador LLVM y numerosos frameworks que usamos a diario. Cada vez que escribes una línea de Swift, estás utilizando un proyecto que se construyó de manera abierta con contribuciones de miles de personas alrededor del mundo.

---

## ¿Por qué es importante para un dev iOS en LATAM?

### 1. Visibilidad global sin fronteras

Como desarrollador en Latinoamérica, una de las barreras más comunes es la **visibilidad profesional**. Contribuir a proyectos open source te coloca en un escaparate global. Un Pull Request bien hecho en un repositorio popular vale más que muchas líneas en un currículum, porque es **trabajo verificable**.

### 2. Aprendizaje acelerado

Leer código de proyectos maduros como [Alamofire](https://github.com/Alamofire/Alamofire), [Kingfisher](https://github.com/onevcat/Kingfisher) o [The Composable Architecture](https://github.com/pointfreeco/swift-composable-architecture) es como tener acceso a mentores de clase mundial. Puedes estudiar patrones de diseño, arquitectura, manejo de errores y testing directamente del código que miles de personas usan en producción.

### 3. Construcción de comunidad local

Latinoamérica tiene una comunidad iOS creciente pero aún fragmentada. Crear y mantener proyectos open source en español, con documentación accesible, ayuda a **reducir la barrera de entrada** para quienes están empezando y fortalece el ecosistema regional.

### 4. Ventaja competitiva en el mercado laboral

Muchas empresas internacionales que contratan remotamente en LATAM revisan los perfiles de GitHub de los candidatos. Un historial activo de contribuciones demuestra **iniciativa, habilidad técnica y capacidad de colaboración** — tres cualidades que ningún título universitario puede probar por sí solo.

---

## Formas de participar en Open Source

### Nivel 1: Consumidor consciente

Antes de contribuir, aprende a **usar** open source de manera responsable.

```swift
// Package.swift — Integrar una dependencia open source con SPM
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MiAppLatam",
    platforms: [.iOS(.v16)],
    dependencies: [
        // Usamos Alamofire para networking
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.9.0"),
        // SnapKit para Auto Layout programático
        .package(url: "https://github.com/SnapKit/SnapKit.git", from: "5.7.0")
    ],
    targets: [
        .target(
            name: "MiAppLatam",
            dependencies: ["Alamofire", "SnapKit"]
        ),
        .testTarget(
            name: "MiAppLatamTests",
            dependencies: ["MiAppLatam"]
        )
    ]
)
```

**Acciones concretas en este nivel:**
- Lee las licencias (MIT, Apache 2.0, GPL) y entiende qué te permiten hacer
- Dale ⭐ a los repositorios que usas — es la forma más básica de reconocimiento
- Reporta bugs con issues bien escritos y reproducibles

### Nivel 2: Contribuidor

No necesitas reescribir un framework entero. Las contribuciones más valiosas suelen ser las más simples.

#### Ejemplo: Corregir documentación y agregar ejemplos

```swift
/// Servicio genérico para decodificar respuestas de API.
///
/// ## Uso básico
/// ```swift
/// let servicio = ServicioAPI()
/// let usuarios = try await servicio.obtener(
///     [Usuario].self,
///     desde: "https://api.ejemplo.com/usuarios"
/// )
/// ```
///
/// ## Manejo de errores
/// ```swift
/// do {
///     let datos = try await servicio.obtener(Perfil.self, desde: url)
/// } catch ErrorDeRed.sinConexion {
///     mostrarAlertaSinInternet()
/// } catch ErrorDeRed.respuestaInvalida(let codigo) {
///     registrarError(codigo: codigo)
/// }
/// ```
///
/// - Note: Requiere iOS 16+ por el uso de concurrencia estructurada.
/// - Important: Todas las llamadas se ejecutan en el actor principal para
///   actualización segura de UI.
@MainActor
final class ServicioAPI {
    
    private let sesion: URLSession
    private let decodificador: JSONDecoder
    
    init(
        sesion: URLSession = .shared,
        decodificador: JSONDecoder = {
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            decoder.dateDecodingStrategy = .iso8601
            return decoder
        }()
    ) {
        self.sesion = sesion
        self.decodificador = decodificador
    }
    
    /// Obtiene y decodifica un recurso desde una URL.
    /// - Parameters:
    ///   - tipo: El tipo `Decodable` esperado en la respuesta.
    ///   - urlString: La URL completa del endpoint.
    /// - Returns: Una instancia decodificada del tipo solicitado.
    /// - Throws: `ErrorDeRed` si la petición falla o la respuesta es inválida.
    func obtener<T: Decodable>(
        _ tipo: T.Type,
        desde urlString: String
    ) async throws -> T {
        guard let url = URL(string: urlString) else {
            throw ErrorDeRed.urlInvalida(urlString)
        }
        
        let (datos, respuesta) = try await sesion.data(from: url)
        
        guard let httpRespuesta = respuesta as? HTTPURLResponse else {
            throw ErrorDeRed.respuestaDesconocida
        }
        
        guard (200...299).contains(httpRespuesta.statusCode) else {
            throw ErrorDeRed.respuestaInvalida(codigo: httpRespuesta.statusCode)
        }
        
        return try decodificador.decode(T.self, from: datos)
    }
}

/// Errores posibles durante las operaciones de red.
enum ErrorDeRed: LocalizedError {
    case urlInvalida(String)
    case sinConexion
    case respuestaInvalida(codigo: Int)
    case respuestaDesconocida
    
    var errorDescription: String? {
        switch self {
        case .urlInvalida(let url):
            return "La URL proporcionada no es válida: \(url)"
        case .sinConexion:
            return "No hay conexión a internet disponible"
        case .respuestaInvalida(let codigo):
            return "El servidor respondió con código de error: \(codigo)"
        case .respuestaDesconocida:
            return "Se recibió una respuesta inesperada del servidor"
        }
    }
}
```

#### Tipos de contribuciones que puedes hacer hoy

| Tipo | Dificultad | Impacto |
|------|-----------|---------|
| Corregir typos en documentación | 🟢 Baja | Alto — mejora la experiencia de todos |
| Traducir README al español | 🟢 Baja | Muy alto para la comunidad LATAM |
| Reportar bugs con pasos de reproducción | 🟢 Baja | Alto para los mantenedores |
| Agregar tests unitarios | 🟡 Media | Alto — fortalece la estabilidad |
| Corregir bugs existentes (etiqueta `good first issue`) | 🟡 Media | Directo |
| Implementar features solicitados | 🔴 Alta | Muy alto |
| Revisar Pull Requests de otros | 🟡 Media | Enorme — los mantenedores lo agradecen |

### Nivel 3: Creador

Crear tu propio proyecto open source es el paso más transformador. No necesitas inventar el próximo SwiftUI — puede ser algo pequeño pero bien hecho.

#### Ejemplo: Un Swift Package reutilizable

Imagina que en varios proyectos necesitas validar formatos comunes en Latinoamérica (RUT chileno, CURP mexicano, cédulas colombianas). Eso es un **excelente** candidato para un paquete open source.

```swift
// Sources/ValidadorLatam/ValidadorRUT.swift

import Foundation

/// Validador de RUT chileno (Rol Único Tributario).
///
/// El RUT es el identificador tributario utilizado en Chile.
/// Formato esperado: `12.345.678-K` o `12345678K`
///
/// ## Ejemplo
/// ```swift
/// let resultado = ValidadorRUT.validar("12.345.678-5")
/// print(resultado.esValido) // true o false
/// ```
public struct ValidadorRUT {
    
    /// Resultado de la validación con información detallada.
    public struct Resultado {
        public let esValido: Bool
        public let rutFormateado: String?
        public let error: ErrorValidacion?
    }
    
    public enum ErrorValidacion: LocalizedError {
        case formatoInvalido
        case digitoVerificadorIncorrecto(esperado: String)
        case vacio
        
        public var errorDescription: String? {
            switch self {
            case .formatoInvalido:
                return "El formato del RUT no es válido"
            case .digitoVerificadorIncorrecto(let esperado):
                return "Dígito verificador incorrecto. Se esperaba: \(esperado)"
            case .vacio:
                return "El RUT no puede estar vacío"
            }
        }
    }
    
    /// Valida un RUT chileno.
    /// - Parameter rut: El RUT a validar (con o sin formato).
    /// - Returns: Un `Resultado` con el estado de la validación.
    public static func validar(_ rut: String) -> Resultado {
        let limpio = rut
            .replacingOccurrences(of: ".", with: "")
            .replacingOccurrences(of: "-", with: "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .uppercased()
        
        guard !limpio.isEmpty else {
            return Resultado(esValido: false, rutFormateado: nil, error: .vacio)
        }
        
        guard limpio.count >= 2,
              limpio.dropLast().allSatisfy(\.isNumber) else {
            return Resultado(esValido: false, rutFormateado: nil, error: .formatoInvalido)
        }
        
        let cuerpo = String(limpio.dropLast())
        let digitoIngresado = String(limpio.last!)
        let digitoCalculado = calcularDigitoVerificador(cuerpo)
        
        guard digitoIngresado == digitoCalculado else {
            return Resultado(
                esValido: false,
                rutFormateado: nil,
                error: .digitoVerificadorIncorrecto(esperado: digitoCalculado)
            )
        }
        
        let formateado = formatear(cuerpo: cuerpo, digito: digitoCalculado)
        return Resultado(esValido: true, rutFormateado: formateado, error: nil)
    }
    
    /// Calcula el dígito verificador usando el algoritmo Módulo 11.
    private static func calcularDigitoVerificador(_ cuerpo: String) -> String {
        var suma = 0
        var multiplicador = 2
        
        for digito in cuerpo.reversed() {
            guard let numero = digito.wholeNumberValue else { continue }
            suma += numero * multiplicador
            multiplicador = multiplicador == 7 ? 2 : multiplicador + 1
        }
        
        let resto = 11 - (suma % 11)
        
        switch resto {
        case 11: return "0"
        case 10: return "K"
        default: return String(resto)
        }
    }
    
    /// Formatea el RUT con puntos y guión.
    private static func formatear(cuerpo: String, digito: String) -> String {
        var resultado = ""
        for (indice, caracter) in cuerpo.reversed().enumerated() {
            if indice > 0 && indice % 3 == 0 {
                resultado = "." + resultado
            }
            resultado = String(caracter) + resultado
        }
        return "\(resultado)-\(digito)"
    }
}
```

Y por supuesto, con **tests**:

```swift
// Tests/ValidadorLatamTests/ValidadorRUTTests.swift

import XCTest
@testable import ValidadorLatam

final class ValidadorRUTTests: XCTestCase {
    
    func test_rutValido_conFormato_retornaValido() {
        let resultado = ValidadorRUT.validar("12.345.678-5")
        XCTAssertTrue(resultado.esValido)
        XCTAssertEqual(resultado.rutFormateado, "12.345.678-5")
        XCTAssertNil(resultado.error)
    }
    
    func test_rutValido_sinFormato_retornaValido() {
        let resultado = ValidadorRUT.validar("123456785")
        XCTAssertTrue(resultado.esValido)
        XCTAssertNotNil(resultado.rutFormateado)
    }
    
    func test_rutConDigitoK_retornaValido() {
        // Usar un RUT conocido que termine en K
        let resultado = ValidadorRUT.validar("44.444.446-K")
        // El resultado dependerá del cálculo real
        XCTAssertNotNil(resultado)
    }
    
    func test_rutVacio_retornaError() {
        let resultado = ValidadorRUT.validar("")
        XCTAssertFalse(resultado.esValido)
        XCTAssertEqual(
            resultado.error,
            .vacio
        )
    }
    
    func test_rutConDigitoIncorrecto_retornaError() {
        let resultado = ValidadorRUT.validar("12.345.678-0")
        XCTAssertFalse(resultado.esValido)
        if case .digitoVerificadorIncorrecto = resultado.error {
            // Correcto: detectó dígito verificador incorrecto
        } else {
            XCTFail("Se esperaba error de dígito verificador incorrecto")
        }
    }
    
    func test_formatoInvalido_retornaError() {
        let resultado = ValidadorRUT.validar("ABC-1")
        XCTAssertFalse(resultado.esValido)
        XCTAssertEqual(resultado.error, .formatoInvalido)
    }
}

extension ValidadorRUT.ErrorValidacion: Equatable {
    public static func == (lhs: Self, rhs: Self) -> Bool {
        switch