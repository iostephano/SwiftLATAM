---
sidebar_position: 1
title: XCTest
---

# XCTest

## ¿Qué es XCTest?

XCTest es el framework nativo de Apple para escribir y ejecutar pruebas unitarias, pruebas de integración y pruebas de interfaz de usuario (UI tests) en proyectos desarrollados para las plataformas Apple (iOS, macOS, tvOS, watchOS y visionOS). Viene integrado directamente en Xcode, lo que significa que no requiere dependencias externas ni configuraciones complejas para comenzar a utilizarlo. Es la piedra angular de cualquier estrategia de testing en el ecosistema Apple.

Este framework proporciona una infraestructura completa que incluye clases base para definir casos de prueba, métodos de aserción para validar resultados esperados, mecanismos para medir el rendimiento del código y herramientas sofisticadas para simular interacciones del usuario con la interfaz gráfica. XCTest se ejecuta directamente desde Xcode, integrándose con el sistema de reportes de resultados, el depurador y las herramientas de integración continua como Xcode Cloud, Jenkins o GitHub Actions.

Deberías usar XCTest siempre que necesites verificar que tu código funciona correctamente, que las regresiones no se introducen con nuevos cambios y que la experiencia de usuario es consistente. Es especialmente valioso en equipos de desarrollo donde múltiples personas contribuyen al mismo proyecto, ya que las pruebas automatizadas actúan como una red de seguridad que detecta problemas antes de que lleguen a producción. Desde verificar que una función de cálculo retorna el valor correcto hasta confirmar que un flujo completo de registro funciona de principio a fin, XCTest cubre todo el espectro de necesidades de testing.

## Casos de uso principales

- **Pruebas unitarias de lógica de negocio**: Verificar que funciones puras, modelos de datos, validadores y transformaciones producen los resultados esperados ante diferentes entradas, incluyendo casos límite y valores nulos.

- **Pruebas de ViewModels y presenters**: Validar que la capa de presentación responde correctamente a eventos del usuario, transforma datos del dominio al formato adecuado para la vista y gestiona correctamente los estados de carga, error y éxito.

- **Pruebas de integración con servicios de red**: Comprobar que las capas de networking parsean correctamente respuestas JSON, manejan errores HTTP de forma apropiada y que los repositorios de datos coordinan correctamente entre fuentes locales y remotas, utilizando mocks y stubs.

- **Pruebas de interfaz de usuario (UI Tests)**: Automatizar la interacción con la app compilada para verificar flujos completos como login, navegación entre pantallas, llenado de formularios y visualización de datos, simulando toques, deslizamientos y escritura de texto.

- **Pruebas de rendimiento (Performance Tests)**: Medir tiempos de ejecución de operaciones críticas como parsing de datos masivos, consultas a base de datos local o renderizado de vistas complejas, estableciendo baselines y detectando regresiones de rendimiento automáticamente.

- **Pruebas asíncronas y de concurrencia**: Verificar el comportamiento correcto de operaciones que utilizan async/await, Combine, callbacks o Grand Central Dispatch, asegurando que los resultados llegan en tiempo y forma y que no existen condiciones de carrera.

## Instalación y configuración

### Creación del target de tests

XCTest viene incluido con Xcode, por lo que no necesitas instalar nada adicional. Al crear un nuevo proyecto, Xcode ofrece la opción de incluir targets de prueba automáticamente. Si tu proyecto no los tiene, puedes agregarlos manualmente:

1. En Xcode, ve a **File → New → Target...**
2. Selecciona **Unit Testing Bundle** para pruebas unitarias
3. Selecciona **UI Testing Bundle** para pruebas de interfaz
4. Asegúrate de que el **Target to be Tested** apunte a tu app principal
5. Haz clic en **Finish**

### Estructura del proyecto

```
MiProyecto/
├── MiProyecto/
│   ├── Models/
│   ├── ViewModels/
│   └── Services/
├── MiProyectoTests/           // ← Pruebas unitarias
│   ├── ModelTests/
│   ├── ViewModelTests/
│   └── ServiceTests/
└── MiProyectoUITests/         // ← Pruebas de UI
    └── Flows/
```

### Import necesario

```swift
import XCTest
@testable import MiProyecto  // Permite acceder a tipos internal del módulo
```

La directiva `@testable` es fundamental: otorga acceso a las declaraciones con visibilidad `internal` del módulo importado, lo cual no estaría disponible desde un módulo de test externo bajo condiciones normales. Los elementos `private` y `fileprivate` siguen siendo inaccesibles.

### Configuración del esquema

Asegúrate de que tu esquema (Scheme) tenga configurado el target de tests:

1. Ve a **Product → Scheme → Edit Scheme...**
2. En la sección **Test**, verifica que tus bundles de prueba estén listados
3. Activa **Code Coverage** si deseas medir la cobertura de código
4. Configura **Diagnostics** para habilitar Address Sanitizer o Thread Sanitizer durante las pruebas

## Conceptos clave

### XCTestCase

Es la clase base de la que heredan todos tus casos de prueba. Cada subclase de `XCTestCase` agrupa pruebas relacionadas, y cada método que comience con `test` se ejecuta automáticamente como una prueba individual. Proporciona los métodos de ciclo de vida `setUp()` y `tearDown()` para preparar y limpiar el entorno antes y después de cada prueba.

### Aserciones (Assertions)

Son funciones que verifican condiciones durante la ejecución de una prueba. Si la condición no se cumple, la prueba falla y se registra un mensaje de error. Las más utilizadas son:

| Aserción | Propósito |
|---|---|
| `XCTAssertEqual(a, b)` | Verifica que dos valores sean iguales |
| `XCTAssertTrue(expr)` | Verifica que una expresión sea verdadera |
| `XCTAssertFalse(expr)` | Verifica que una expresión sea falsa |
| `XCTAssertNil(expr)` | Verifica que un valor sea nil |
| `XCTAssertNotNil(expr)` | Verifica que un valor NO sea nil |
| `XCTAssertThrowsError(expr)` | Verifica que se lance un error |
| `XCTAssertNoThrow(expr)` | Verifica que NO se lance un error |
| `XCTAssertGreaterThan(a, b)` | Verifica que a > b |
| `XCTAssertLessThan(a, b)` | Verifica que a < b |

### Expectations (Expectativas)

Mecanismo para probar código asíncrono. Creas una expectativa con `expectation(description:)`, la cumples con `fulfill()` cuando el evento asíncrono ocurre y esperas su cumplimiento con `wait(for:timeout:)`. Si la expectativa no se cumple dentro del tiempo límite, la prueba falla automáticamente.

### Test Doubles (Dobles de prueba)

Objetos que reemplazan dependencias reales durante las pruebas para aislar la unidad bajo test. Los tipos principales son:

- **Mock**: Verifica que ciertos métodos fueron llamados con parámetros específicos
- **Stub**: Retorna valores predefinidos sin lógica real
- **Spy**: Registra las interacciones para verificarlas después
- **Fake**: Implementación funcional simplificada (ej: base de datos en memoria)

### XCUIApplication y XCUIElement

Clases fundamentales para UI Testing. `XCUIApplication` representa la app en ejecución y permite lanzarla y terminarla. `XCUIElement` representa un elemento de la interfaz (botón, campo de texto, celda) y permite interactuar con él mediante métodos como `tap()`, `typeText()`, `swipeUp()`, etc.

### Medición de rendimiento (Performance Metrics)

El método `measure {}` ejecuta un bloque de código múltiples veces y registra métricas como tiempo de reloj, uso de CPU y memoria. Xcode establece baselines automáticas y te alerta cuando el rendimiento se desvía significativamente.

## Ejemplo básico

```swift
import XCTest
@testable import MiProyecto

// MARK: - Modelo a probar

/// Calculadora simple que implementa operaciones matemáticas básicas
struct Calculadora {
    
    /// Suma dos números enteros
    func sumar(_ a: Int, _ b: Int) -> Int {
        return a + b
    }
    
    /// Divide dos números, retorna nil si el divisor es cero
    func dividir(_ a: Double, entre b: Double) -> Double? {
        guard b != 0 else { return nil }
        return a / b
    }
    
    /// Calcula el factorial de un número no negativo
    func factorial(_ n: Int) -> Int? {
        guard n >= 0 else { return nil }
        guard n > 1 else { return 1 }
        return n * (factorial(n - 1) ?? 0)
    }
}

// MARK: - Tests

/// Caso de prueba para la Calculadora
final class CalculadoraTests: XCTestCase {
    
    // Sistema bajo prueba (SUT)
    private var sut: Calculadora!
    
    // Se ejecuta ANTES de cada método de test
    override func setUp() {
        super.setUp()
        sut = Calculadora()
    }
    
    // Se ejecuta DESPUÉS de cada método de test
    override func tearDown() {
        sut = nil
        super.tearDown()
    }
    
    // MARK: - Tests de suma
    
    func test_sumar_dosNumerosPositivos_retornaResultadoCorrecto() {
        // Given (Dado)
        let a = 3
        let b = 7
        
        // When (Cuando)
        let resultado = sut.sumar(a, b)
        
        // Then (Entonces)
        XCTAssertEqual(resultado, 10, "La suma de 3 + 7 debería ser 10")
    }
    
    func test_sumar_numerosNegativos_retornaResultadoCorrecto() {
        let resultado = sut.sumar(-5, -3)
        XCTAssertEqual(resultado, -8)
    }
    
    func test_sumar_conCero_retornaElOtroNumero() {
        XCTAssertEqual(sut.sumar(42, 0), 42)
        XCTAssertEqual(sut.sumar(0, 42), 42)
    }
    
    // MARK: - Tests de división
    
    func test_dividir_divisionNormal_retornaResultadoCorrecto() {
        let resultado = sut.dividir(10, entre: 3)
        
        // Para comparar Doubles, usamos accuracy
        XCTAssertEqual(resultado!, 3.333, accuracy: 0.001)
    }
    
    func test_dividir_entreCero_retornaNil() {
        let resultado = sut.dividir(10, entre: 0)
        XCTAssertNil(resultado, "Dividir entre cero debe retornar nil")
    }
    
    // MARK: - Tests de factorial
    
    func test_factorial_deNumeroPositivo_retornaResultadoCorrecto() {
        XCTAssertEqual(sut.factorial(5), 120)
    }
    
    func test_factorial_deCero_retornaUno() {
        XCTAssertEqual(sut.factorial(0), 1)
    }
    
    func test_factorial_deNumeroNegativo_retornaNil() {
        XCTAssertNil(sut.factorial(-3))
    }
    
    // MARK: - Test de rendimiento
    
    func test_factorial_rendimiento() {
        measure {
            // Este bloque se ejecuta múltiples veces para medir rendimiento
            _ = sut.factorial(20)
        }
    }
}
```

## Ejemplo intermedio

```swift
import XCTest
@testable import MiProyecto

// MARK: - Protocolo del servicio de red

/// Protocolo que abstrae las llamadas de red para facilitar el testing
protocol NetworkServiceProtocol {
    func fetchData(from url: URL) async throws -> Data
}

// MARK: - Modelo de dominio

struct Usuario: Codable, Equatable {
    let id: Int
    let nombre: String
    let email: String
    let activo: Bool
}

// MARK: - Errores personalizados

enum RepositorioError: Error, Equatable {
    case urlInvalida
    case sinDatos
    case decodificacionFallida
    case sinConexion
}

// MARK: - Repositorio a probar

/// Repositorio que gestiona la obtención y procesamiento de usuarios
final class UsuarioRepositorio {
    
    private let networkService: NetworkServiceProtocol
    private let baseURL: String
    
    init(networkService: NetworkServiceProtocol, baseURL: String = "https://api.ejemplo.com") {
        self.networkService = networkService
        self.baseURL = baseURL
    }
    
    /// Obtiene la lista de todos los usuarios
    func obtenerUsuarios() async throws -> [Usuario] {
        guard let url = URL(string: "\(baseURL)/usuarios") else {
            throw RepositorioError.urlInvalida
        }
        
        let data = try await networkService.fetchData(from: url)
        
        guard !data.isEmpty else {
            throw RepositorioError.sinDatos
        }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode([Usuario].self, from: data)
        } catch {
            throw RepositorioError.decodificacionFallida
        }
    }
    
    /// Obtiene solo los usuarios activos
    func obtenerUsuariosActivos() async throws -> [Usuario] {
        let todos = try await obtenerUsuarios()
        return todos.filter { $0.activo }
    }
    
    /// Busca un usuario por su email
    func buscarUsuario(porEmail email: String) async throws -> Usuario? {
        let todos = try await obtenerUsuarios()
        return todos.first { $0.email.lowercased() == email.lowercased() }
    }
}

// MARK: - Mock del servicio de red

/// Mock que simula el servicio de red para pruebas
final class MockNetworkService: NetworkServiceProtocol {
    
    // Datos que el mock retornará
    var dataToReturn: Data?
    
    // Error que el mock lanzará (si se configura)
    var errorToThrow: Error?
    
    // Registro de llamadas para verificar comportamiento
    var fetchDataCallCount = 0
    var lastRequestedURL: URL?
    
    func fetchData(from url: URL) async throws -> Data {
        fetchDataCallCount += 1
        lastRequestedURL = url
        
        if let error = errorToThrow {
            throw error
        }
        
        return dataToReturn ?? Data()
    }
}

// MARK: - Tests del Repositorio

final class UsuarioRepositorioTests: XCTestCase {
    
    private var sut: UsuarioRepositorio!
    private var mockNetworkService: MockNetworkService!
    
    //