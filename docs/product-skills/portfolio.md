---
sidebar_position: 1
title: Portfolio
---

# Portfolio para Desarrolladores iOS en LATAM

## ¿Qué es un portfolio de desarrollo iOS?

Un portfolio es mucho más que una colección de proyectos: es tu **carta de presentación profesional**. Es la evidencia tangible de que puedes resolver problemas reales con código, diseño y pensamiento crítico. Mientras un CV dice lo que *afirmas* saber hacer, el portfolio **demuestra** lo que realmente puedes hacer.

Para un desarrollador iOS, el portfolio típicamente incluye aplicaciones publicadas en la App Store, proyectos de código abierto en GitHub, contribuciones a la comunidad y, en algunos casos, un sitio web personal que conecta todo.

## ¿Por qué es crucial para un dev iOS en LATAM?

### La realidad del mercado latinoamericano

En Latinoamérica enfrentamos desafíos específicos que hacen del portfolio una herramienta **estratégicamente vital**:

- **Competencia global remota**: Compites por posiciones remotas con desarrolladores de todo el mundo. Un portfolio sólido te diferencia inmediatamente.
- **Brecha de credenciales**: Muchos devs LATAM son autodidactas o provienen de bootcamps. Sin un título de Stanford, tu código habla por ti.
- **Barrera del idioma y la ubicación**: Un portfolio bien construido derriba prejuicios. Cuando un reclutador en San Francisco ve tu app funcionando impecablemente, tu ubicación geográfica se vuelve irrelevante.
- **Diferencial salarial**: Un portfolio fuerte puede ser la diferencia entre un salario local y uno internacional (que puede ser 3-5x mayor).

### La ecuación es simple

> Sin portfolio = dependes de que alguien **confíe** en tu palabra.
> Con portfolio = **demuestras** tu valor antes de la primera entrevista.

## Anatomía de un portfolio iOS efectivo

### 1. Proyectos que demuestran habilidad real

No necesitas 20 proyectos. Necesitas **3-5 proyectos excelentes** que cubran diferentes competencias:

| Tipo de proyecto | Qué demuestra | Ejemplo |
|---|---|---|
| App completa en App Store | Capacidad de enviar producto real | App de finanzas personales |
| Clone de app conocida | Dominio técnico específico | Clone de la UI de Spotify |
| Proyecto open source | Colaboración y código limpio | Librería de componentes SwiftUI |
| Proyecto con API real | Integración y manejo de datos | App de clima con OpenWeather |
| Desafío técnico resuelto | Resolución de problemas | Algoritmo de búsqueda visual |

### 2. Estructura de cada proyecto en GitHub

Cada repositorio debe tener un README que cuente una historia profesional. Aquí tienes una plantilla:

```markdown
# 🏦 FinanzasApp

App de finanzas personales para el mercado latinoamericano.

## Screenshots
[imágenes de la app en funcionamiento]

## Tecnologías
- SwiftUI + Combine
- Core Data con CloudKit
- Charts framework
- Widget Extensions

## Arquitectura
MVVM + Clean Architecture

## Qué aprendí
- Manejo de múltiples monedas LATAM
- Sincronización offline-first
- Accesibilidad (VoiceOver completo)

## Cómo ejecutar
1. Clonar repositorio
2. Abrir .xcodeproj
3. Cmd + R
```

### 3. Código que habla por sí solo

Tu código es tu mejor argumento. Veamos un ejemplo de cómo un proyecto de portfolio debe reflejar buenas prácticas:

```swift
// MARK: - Protocolo del repositorio (Clean Architecture)
protocol ExpenseRepositoryProtocol {
    func fetchExpenses(for month: Date) async throws -> [Expense]
    func saveExpense(_ expense: Expense) async throws
    func deleteExpense(id: UUID) async throws
    func totalByCategory(for month: Date) async throws -> [CategoryTotal]
}

// MARK: - Modelo de dominio claro y bien documentado
struct Expense: Identifiable, Codable {
    let id: UUID
    let amount: Decimal
    let currency: LatamCurrency
    let category: ExpenseCategory
    let description: String
    let date: Date
    let isRecurring: Bool
    
    /// Convierte el monto a la moneda local del usuario
    func converted(to targetCurrency: LatamCurrency,
                   using exchangeRate: ExchangeRate) -> Decimal {
        guard currency != targetCurrency else { return amount }
        return amount * exchangeRate.rate(from: currency, to: targetCurrency)
    }
}

// MARK: - Enum que muestra conocimiento del contexto LATAM
enum LatamCurrency: String, Codable, CaseIterable {
    case mxn = "MXN" // Peso mexicano
    case cop = "COP" // Peso colombiano
    case ars = "ARS" // Peso argentino
    case clp = "CLP" // Peso chileno
    case pen = "PEN" // Sol peruano
    case brl = "BRL" // Real brasileño
    case usd = "USD" // Dólar (referencia)
    
    var symbol: String {
        switch self {
        case .mxn, .cop, .ars, .clp: return "$"
        case .pen: return "S/"
        case .brl: return "R$"
        case .usd: return "US$"
        }
    }
    
    var decimalPlaces: Int {
        switch self {
        case .clp, .cop: return 0 // Estas monedas no usan decimales comúnmente
        default: return 2
        }
    }
}
```

Observa lo que este código comunica a un reclutador:

- **Arquitectura limpia**: Protocolos, separación de responsabilidades.
- **Swift moderno**: `async/await`, `Identifiable`, `CaseIterable`.
- **Conocimiento de dominio**: Entiendes las monedas LATAM y sus particularidades.
- **Documentación**: Comentarios claros sin ser excesivos.

### 4. Un ViewModel que demuestre dominio de SwiftUI moderno

```swift
// MARK: - ViewModel con Observation framework (iOS 17+)
@Observable
final class ExpenseListViewModel {
    
    // MARK: - State
    var expenses: [Expense] = []
    var selectedMonth: Date = .now
    var categoryTotals: [CategoryTotal] = []
    var isLoading = false
    var errorMessage: String?
    
    var totalForMonth: Decimal {
        expenses.reduce(0) { $0 + $1.amount }
    }
    
    var formattedTotal: String {
        CurrencyFormatter.shared.format(
            amount: totalForMonth,
            currency: userPreferences.currency
        )
    }
    
    // MARK: - Dependencies (inyección para testabilidad)
    private let repository: ExpenseRepositoryProtocol
    private let userPreferences: UserPreferencesProtocol
    
    init(repository: ExpenseRepositoryProtocol,
         userPreferences: UserPreferencesProtocol) {
        self.repository = repository
        self.userPreferences = userPreferences
    }
    
    // MARK: - Actions
    func loadExpenses() async {
        isLoading = true
        errorMessage = nil
        
        do {
            async let fetchedExpenses = repository.fetchExpenses(for: selectedMonth)
            async let fetchedTotals = repository.totalByCategory(for: selectedMonth)
            
            let (expensesResult, totalsResult) = try await (fetchedExpenses, fetchedTotals)
            
            expenses = expensesResult.sorted { $0.date > $1.date }
            categoryTotals = totalsResult
        } catch {
            errorMessage = mapError(error)
        }
        
        isLoading = false
    }
    
    func deleteExpense(_ expense: Expense) async {
        do {
            try await repository.deleteExpense(id: expense.id)
            expenses.removeAll { $0.id == expense.id }
        } catch {
            errorMessage = "No se pudo eliminar el gasto. Intenta de nuevo."
        }
    }
    
    // MARK: - Private helpers
    private func mapError(_ error: Error) -> String {
        switch error {
        case is NetworkError:
            return "Sin conexión. Mostrando datos guardados localmente."
        case is DatabaseError:
            return "Error al acceder a tus datos. Reinicia la app."
        default:
            return "Ocurrió un error inesperado."
        }
    }
}
```

Este ViewModel demuestra:

- **Concurrencia estructurada** con `async let` para peticiones paralelas.
- **Inyección de dependencias** para facilitar testing.
- **Manejo de errores** con mensajes amigables en español.
- **@Observable** mostrando que dominas las APIs más recientes.

### 5. Tests que demuestran profesionalismo

```swift
// MARK: - Tests que muestran que escribes código testeable
struct ExpenseListViewModelTests {
    
    @Test("Carga gastos correctamente para el mes seleccionado")
    func loadExpensesSuccessfully() async {
        // Given
        let mockExpenses = [
            Expense.mock(amount: 150.00, currency: .mxn, category: .food),
            Expense.mock(amount: 500.00, currency: .mxn, category: .transport)
        ]
        let mockRepository = MockExpenseRepository(expenses: mockExpenses)
        let sut = ExpenseListViewModel(
            repository: mockRepository,
            userPreferences: MockUserPreferences(currency: .mxn)
        )
        
        // When
        await sut.loadExpenses()
        
        // Then
        #expect(sut.expenses.count == 2)
        #expect(sut.totalForMonth == 650.00)
        #expect(sut.isLoading == false)
        #expect(sut.errorMessage == nil)
    }
    
    @Test("Muestra error amigable cuando falla la red")
    func showsErrorOnNetworkFailure() async {
        // Given
        let mockRepository = MockExpenseRepository(
            error: NetworkError.noConnection
        )
        let sut = ExpenseListViewModel(
            repository: mockRepository,
            userPreferences: MockUserPreferences(currency: .mxn)
        )
        
        // When
        await sut.loadExpenses()
        
        // Then
        #expect(sut.expenses.isEmpty)
        #expect(sut.errorMessage != nil)
        #expect(sut.errorMessage!.contains("Sin conexión"))
    }
}
```

Incluir tests en tu portfolio comunica un mensaje poderoso: **"Escribo código profesional y mantenible"**.

## Tu presencia digital: más allá de GitHub

### Sitio web personal

No necesitas algo complejo. Una página estática simple con:

```
tunombre.dev/
├── Inicio (quién eres, qué haces)
├── Proyectos (3-5 con screenshots y enlaces)
├── Blog (artículos técnicos, opcional pero potente)
└── Contacto (email, LinkedIn, GitHub)
```

**Herramientas recomendadas para devs iOS:**
- **Publish** (de John Sundell): Generador de sitios estáticos escrito en Swift.
- **Docusaurus**: Ideal si también quieres documentar tus proyectos.
- **GitHub Pages**: Hosting gratuito, dominio personalizado fácil.

### LinkedIn optimizado para LATAM

Tu perfil de LinkedIn debe funcionar como extensión de tu portfolio:

- **Headline**: "iOS Developer | SwiftUI · UIKit · Clean Architecture" (en inglés si buscas remoto internacional).
- **About**: Historia concisa de tu journey como dev. Incluye link a tu portfolio.
- **Featured**: Enlaza tus mejores proyectos directamente.
- **Idioma**: Si aplicas a empresas de USA/Europa, mantén el perfil en inglés. Puedes tener un perfil secundario en español.

## Plan de acción: construye tu portfolio en 8 semanas

### Semanas 1-2: Fundamentos

- [ ] Crea tu cuenta de GitHub (o limpia la existente)
- [ ] Define tu "stack de identidad": ¿SwiftUI? ¿UIKit? ¿Ambos?
- [ ] Elige 3 proyectos que vas a construir
- [ ] Configura un template de README profesional

### Semanas 3-4: Proyecto principal

- [ ] Desarrolla tu app estrella (la más completa)
- [ ] Implementa arquitectura MVVM o Clean Architecture
- [ ] Agrega tests unitarios mínimos (cobertura >60%)
- [ ] Escribe un README detallado con screenshots

### Semanas 5-6: Proyectos complementarios

- [ ] Construye un proyecto que use APIs reales
- [ ] Crea un proyecto que muestre UI/UX pulido
- [ ] Asegúrate de que cada repo tenga su README completo

### Semana 7: Presencia digital

- [ ] Despliega tu sitio web personal
- [ ] Optimiza tu perfil de LinkedIn
- [ ] Conecta todo: GitHub ↔ Web ↔ LinkedIn

### Semana 8: Pulido y feedback

- [ ] Pide a 2-3 devs que revisen tu portfolio
- [ ] Corrige código, mejora READMEs
- [ ] Graba un video corto mostrando tu app principal (opcional pero diferenciador)

## Errores comunes que debes evitar

### ❌ Lo que NO hacer

1. **Repositorios vacíos o sin README**: Un repo sin contexto es peor que no tener repo.
2. **Solo tutoriales copiados**: Si hiciste el "Landmarks" de Apple, todos lo reconocen. Agrega tu propio twist.
3. **Código sin estructura**: Un `ViewController` de 800 líneas grita "junior sin mentoría".
4. **Ignorar el diseño**: No necesitas ser diseñador, pero tu app debe verse decente. Usa SF Symbols y las Human Interface Guidelines.
5. **No actualizar**: Un portfolio con el último commit hace 2 años genera dudas.

### ✅ Lo que SÍ hacer

1. **Commits frecuentes y descriptivos**: Muestra tu proceso de desarrollo.
2. **Branches y PRs**: Incluso si trabajas solo, usa feature branches.
3. **Documentación inline**: Comenta el "por qué", no el "qué".
4. **Accesibilidad**: Implementar VoiceOver te diferencia del 90% de los candidatos.
5. **Localización**: Una app que soporte español e inglés muestra madurez profesional.

## Ejemplo: cómo presentar un proyecto en una entrevista

Cuando te pregunten "¿Cuéntame sobre un proyecto tuyo?", usa la estructura **STAR adaptada para devs**:

```
SITUACIÓN: "Vi que muchas apps de finanzas no consideraban las monedas 
            latinoamericanas ni la volatilidad cambiaria de la región."

TAREA:     "Decidí crear FinanzasApp, una app que maneja múltiples 
            monedas LATAM con actualización de tasas en tiempo real."

ACCIÓN:    "Implementé Clean Architecture con SwiftUI, usé Core Data 
            para persistencia offline-first (crítico en zonas con 
            conectividad limitada), y async/await para las llamadas 
            a la API de Exchange Rates."

RESULTADO: "La app tiene 4.6 estrellas en la App Store con 500+ 
            descargas en