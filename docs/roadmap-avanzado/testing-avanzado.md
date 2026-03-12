---
sidebar_position: 1
title: Testing Avanzado
---

# Testing Avanzado en iOS

## Más allá de los tests unitarios básicos

Si ya escribes tests unitarios simples, felicidades: estás por encima del promedio en muchos equipos de desarrollo en Latinoamérica. Pero la realidad es que los tests básicos solo rascan la superficie. **El testing avanzado es lo que separa a un desarrollador competente de uno verdaderamente confiable.**

En esta guía vamos a profundizar en técnicas que te permitirán construir suites de testing robustas, mantenibles y que realmente atrapen bugs antes de que lleguen a producción.

---

## ¿Por qué esto importa especialmente en LATAM?

En el mercado latinoamericano hay una realidad concreta:

- **Equipos pequeños** donde cada bug en producción cuesta caro (no hay un equipo de QA de 20 personas para respaldarte).
- **Clientes internacionales** que esperan estándares de calidad altos — el testing avanzado es una ventaja competitiva real cuando compites por proyectos remotos.
- **Alta rotación de desarrolladores** — una buena suite de tests actúa como documentación viva y red de seguridad cuando alguien nuevo toca el código.
- **Apps financieras y de salud en crecimiento** en la región, donde un fallo puede tener consecuencias legales y financieras severas.

No es un lujo académico. Es una necesidad práctica.

---

## 1. Test Doubles avanzados: Más allá del Mock simple

La mayoría de desarrolladores conocen los mocks, pero rara vez distinguen entre los diferentes tipos de test doubles ni los usan correctamente.

### Tipos de Test Doubles

| Tipo | Propósito | Cuándo usarlo |
|------|-----------|---------------|
| **Dummy** | Rellenar parámetros que no importan | Cumplir firmas de funciones |
| **Stub** | Devolver valores predefinidos | Controlar el input del SUT |
| **Spy** | Registrar interacciones | Verificar que algo se llamó |
| **Mock** | Verificar comportamiento esperado | Validar interacciones específicas |
| **Fake** | Implementación funcional simplificada | Reemplazar dependencias complejas |

### Ejemplo práctico: Spy vs Mock

```swift
// MARK: - Protocolo de servicio
protocol PaymentServiceProtocol {
    func processPayment(amount: Decimal, currency: String) async throws -> PaymentResult
    func refund(transactionId: String) async throws -> RefundResult
}

// MARK: - Spy: registra TODO lo que pasa
class PaymentServiceSpy: PaymentServiceProtocol {
    // Registro de llamadas
    var processPaymentCallCount = 0
    var processPaymentArguments: [(amount: Decimal, currency: String)] = []
    var refundCallCount = 0
    var refundArguments: [String] = []

    // Valores de retorno configurables
    var processPaymentResult: PaymentResult = .success(transactionId: "fake-123")
    var refundResult: RefundResult = .success

    func processPayment(amount: Decimal, currency: String) async throws -> PaymentResult {
        processPaymentCallCount += 1
        processPaymentArguments.append((amount, currency))
        return processPaymentResult
    }

    func refund(transactionId: String) async throws -> RefundResult {
        refundCallCount += 1
        refundArguments.append(transactionId)
        return refundResult
    }
}

// MARK: - Fake: implementación simplificada pero funcional
class FakePaymentService: PaymentServiceProtocol {
    // Estado interno que simula un backend real
    private var transactions: [String: Decimal] = [:]
    private var refundedTransactions: Set<String> = []

    func processPayment(amount: Decimal, currency: String) async throws -> PaymentResult {
        guard amount > 0 else {
            throw PaymentError.invalidAmount
        }

        let id = UUID().uuidString
        transactions[id] = amount
        return .success(transactionId: id)
    }

    func refund(transactionId: String) async throws -> RefundResult {
        guard transactions[transactionId] != nil else {
            throw PaymentError.transactionNotFound
        }
        guard !refundedTransactions.contains(transactionId) else {
            throw PaymentError.alreadyRefunded
        }

        refundedTransactions.insert(transactionId)
        return .success
    }
}
```

### Cuándo usar cada uno

```swift
// Usa el SPY cuando quieres verificar CÓMO se interactúa con la dependencia
func testCheckout_processesPaymentWithCorrectCurrency() async throws {
    let spy = PaymentServiceSpy()
    let sut = CheckoutViewModel(paymentService: spy)

    sut.selectedCurrency = "MXN"
    sut.cartTotal = 1500.00

    await sut.checkout()

    // Verificamos la interacción exacta
    XCTAssertEqual(spy.processPaymentCallCount, 1)
    XCTAssertEqual(spy.processPaymentArguments.first?.currency, "MXN")
    XCTAssertEqual(spy.processPaymentArguments.first?.amount, 1500.00)
}

// Usa el FAKE cuando quieres probar flujos completos con lógica realista
func testFullPurchaseAndRefundFlow() async throws {
    let fake = FakePaymentService()
    let sut = OrderManager(paymentService: fake)

    // Flujo completo: compra → reembolso
    let order = try await sut.placeOrder(amount: 299.99, currency: "COP")
    XCTAssertNotNil(order.transactionId)

    let refundResult = try await sut.refundOrder(order)
    XCTAssertEqual(refundResult, .success)

    // Verificar que no se puede reembolsar dos veces
    do {
        _ = try await sut.refundOrder(order)
        XCTFail("Debería haber lanzado un error")
    } catch PaymentError.alreadyRefunded {
        // Comportamiento esperado ✅
    }
}
```

---

## 2. Testing de código asíncrono con Swift Concurrency

El testing asíncrono es donde la mayoría de las suites de tests se rompen. Con `async/await` la situación mejoró enormemente, pero hay trampas sutiles.

### Patrón básico: Tests async nativos

```swift
// ✅ XCTest soporta async/await de forma nativa desde Xcode 13.2
func testFetchUserProfile_returnsCorrectData() async throws {
    let mockService = UserServiceStub(
        stubbedProfile: UserProfile(name: "María", country: "Argentina")
    )
    let sut = ProfileViewModel(userService: mockService)

    try await sut.loadProfile()

    XCTAssertEqual(sut.userName, "María")
    XCTAssertEqual(sut.userCountry, "Argentina")
    XCTAssertFalse(sut.isLoading)
}
```

### Testeando @MainActor y actualizaciones de UI

```swift
@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var userName: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let userService: UserServiceProtocol

    init(userService: UserServiceProtocol) {
        self.userService = userService
    }

    func loadProfile() async {
        isLoading = true
        errorMessage = nil

        do {
            let profile = try await userService.fetchProfile()
            userName = profile.name
        } catch {
            errorMessage = "No pudimos cargar tu perfil. Intenta de nuevo."
        }

        isLoading = false
    }
}

// MARK: - Tests
@MainActor
final class ProfileViewModelTests: XCTestCase {

    func testLoadProfile_whileLoading_showsLoadingState() async {
        // Usamos una continuación para "pausar" el servicio
        let service = ControllableUserService()
        let sut = ProfileViewModel(userService: service)

        // Iniciamos la carga pero NO la completamos aún
        let task = Task {
            await sut.loadProfile()
        }

        // Esperamos brevemente a que el estado se actualice
        await Task.yield()

        XCTAssertTrue(sut.isLoading) // ✅ Podemos verificar el estado intermedio

        // Ahora completamos la operación
        service.complete(with: UserProfile(name: "Carlos", country: "Chile"))
        await task.value

        XCTAssertFalse(sut.isLoading)
        XCTAssertEqual(sut.userName, "Carlos")
    }

    func testLoadProfile_onError_showsUserFriendlyMessage() async {
        let failingService = UserServiceStub(error: URLError(.notConnectedToInternet))
        let sut = ProfileViewModel(userService: failingService)

        await sut.loadProfile()

        XCTAssertNil(sut.userName.isEmpty ? nil : sut.userName)
        XCTAssertEqual(sut.errorMessage, "No pudimos cargar tu perfil. Intenta de nuevo.")
        XCTAssertFalse(sut.isLoading)
    }
}
```

### Servicio controlable para tests de timing

```swift
class ControllableUserService: UserServiceProtocol {
    private var continuation: CheckedContinuation<UserProfile, Error>?

    func fetchProfile() async throws -> UserProfile {
        return try await withCheckedThrowingContinuation { continuation in
            self.continuation = continuation
        }
    }

    // Métodos para controlar desde el test
    func complete(with profile: UserProfile) {
        continuation?.resume(returning: profile)
    }

    func fail(with error: Error) {
        continuation?.resume(throwing: error)
    }
}
```

---

## 3. Property-Based Testing con swift-custom-dump y swift-testing

En lugar de probar con valores específicos que tú eliges, el property-based testing genera cientos de inputs aleatorios y verifica que ciertas propiedades siempre se cumplan.

### Concepto: No pruebes con UN ejemplo, prueba con una PROPIEDAD

```swift
import Testing

// ❌ Test basado en ejemplos (frágil, incompleto)
@Test func testCurrencyFormatting_specificValue() {
    let result = formatCurrency(1234.56, locale: "es_MX")
    #expect(result == "$1,234.56")
}

// ✅ Test basado en propiedades (robusto)
@Test(arguments: [
    (0.01, "es_MX"),
    (999999.99, "es_AR"),
    (0.00, "es_CO"),
    (1234.567, "es_CL"),
])
func testCurrencyFormatting_alwaysProducesValidOutput(
    amount: Double,
    locale: String
) {
    let result = formatCurrency(amount, locale: locale)

    // Propiedades que SIEMPRE deben cumplirse:
    #expect(!result.isEmpty, "El resultado nunca debe estar vacío")
    #expect(result.contains(Locale(identifier: locale).currencySymbol ?? "$"),
            "Siempre debe incluir el símbolo de moneda")

    if amount == 0 {
        #expect(result.contains("0"), "Cero siempre debe mostrar 0")
    }
}
```

### Propiedades comunes para validar

```swift
@Test func testEmailValidator_properties() {
    let validEmails = [
        "user@example.com",
        "maria.garcia@empresa.com.mx",
        "dev+tag@startup.co",
    ]

    let invalidEmails = [
        "",
        "noarroba.com",
        "@sinusuario.com",
        "espacios en@email.com",
        "user@",
    ]

    // Propiedad 1: Todo email válido debe ser aceptado
    for email in validEmails {
        #expect(
            EmailValidator.isValid(email),
            "'\(email)' debería ser válido"
        )
    }

    // Propiedad 2: Todo email inválido debe ser rechazado
    for email in invalidEmails {
        #expect(
            !EmailValidator.isValid(email),
            "'\(email)' debería ser inválido"
        )
    }

    // Propiedad 3: Idempotencia - validar dos veces da el mismo resultado
    for email in validEmails + invalidEmails {
        #expect(
            EmailValidator.isValid(email) == EmailValidator.isValid(email),
            "La validación debe ser determinista"
        )
    }
}
```

---

## 4. Snapshot Testing

Los snapshot tests capturan el output visual o estructural de un componente y lo comparan contra una referencia previamente aprobada. Son ideales para detectar regresiones visuales involuntarias.

### Configuración con swift-snapshot-testing de Point-Free

```swift
// Package.swift
dependencies: [
    .package(
        url: "https://github.com/pointfreeco/swift-snapshot-testing",
        from: "1.15.0"
    ),
]
```

### Tests de snapshot para SwiftUI Views

```swift
import SnapshotTesting
import SwiftUI
import XCTest

final class PaymentCardSnapshotTests: XCTestCase {

    func testPaymentCard_defaultState() {
        let view = PaymentCardView(
            cardNumber: "**** **** **** 4242",
            holderName: "MARÍA GARCÍA",
            expiryDate: "12/27",
            brand: .visa
        )

        let controller = UIHostingController(rootView: view)
        controller.view.frame = CGRect(x: 0, y: 0, width: 350, height: 220)

        assertSnapshot(of: controller, as: .image(on: .iPhone13))
    }

    func testPaymentCard_allBrands() {
        let brands: [CardBrand] = [.visa, .mastercard, .amex]

        for brand in brands {
            let view = PaymentCardView(
                cardNumber: "**** **** **** 4242",
                holderName: "CARLOS LÓPEZ",
                expiryDate: "06/28",
                brand: brand
            )

            let controller = UIHostingController(rootView: view)
            controller.view.frame = CGRect(x: 0, y: 0, width: 350, height: 220)

            assertSnapshot(
                of: controller,
                as: .image(on: .iPhone13),
                named: "brand-\(brand.rawValue)"
            )
        }
    }

    // Snapshot de accesibilidad: verifica la jerarquía
    func testPaymentCard_accessibilityHierarchy() {
        let view = PaymentCardView(
            cardNumber: "**** **** **** 4242",
            holderName: "ANA MARTÍNEZ",
            expiryDate: "03/26",
            brand: .visa
        )

        let controller = UIHostingController(rootView: view)
        controller.view.frame = CGRect(x: 0, y: 0, width: 350, height: 220)

        // Snapshot de la jerarquía de accesibilidad (texto, no imagen)
        assertSnapshot(of: controller, as: .recursiveDescription)
    }
}
```

### Snapshot de modelos de datos (no solo UI)

```swift
import CustomDump // De Point-Free, complemento perfecto

func testAPIResponse_