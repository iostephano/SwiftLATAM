---
sidebar_position: 1
title: Product Thinking
---

# Product Thinking para Desarrolladores iOS

## ¿Qué es Product Thinking?

Product Thinking es la capacidad de **pensar más allá del código** y entender el *por qué* detrás de cada feature que construyes. No se trata solo de implementar tickets de Jira: se trata de comprender el problema del usuario, el contexto del negocio y cómo cada línea de código que escribes genera (o destruye) valor.

Un desarrollador iOS con Product Thinking no pregunta únicamente *"¿cómo lo implemento?"*. Pregunta:

- **¿Qué problema resuelve esto para el usuario?**
- **¿Cómo medimos si funciona?**
- **¿Es la solución más simple que podemos entregar primero?**
- **¿Qué pasa si el usuario no tiene internet, tiene un iPhone 8 o vive en una zona rural de Colombia?**

---

## ¿Por qué es crucial para un dev iOS en LATAM?

El contexto latinoamericano tiene particularidades que hacen que el Product Thinking sea aún más relevante:

### 1. Equipos más pequeños, mayor impacto individual
En startups y empresas de tecnología en LATAM, los equipos de desarrollo suelen ser reducidos. Un desarrollador iOS frecuentemente es **el único** desarrollador iOS. Esto significa que tus decisiones técnicas **son** decisiones de producto.

### 2. Restricciones reales del mercado
- **Dispositivos más antiguos**: Un porcentaje significativo de usuarios en México, Colombia, Argentina y Perú usa iPhones de generaciones anteriores con almacenamiento limitado.
- **Conectividad intermitente**: No todos tienen 5G ni Wi-Fi estable. Tu app debe funcionar offline o degradar graciosamente.
- **Sensibilidad al precio**: Las compras in-app y suscripciones deben considerar el poder adquisitivo local.

### 3. Diferenciación profesional
En un mercado donde muchos desarrolladores compiten por posiciones remotas bien remuneradas, **la capacidad de pensar como producto te separa del 90% de los candidatos**. Las empresas no buscan "manos que codean"; buscan personas que entienden el negocio.

---

## Los 5 pilares del Product Thinking aplicados a iOS

### Pilar 1: Empatía con el usuario

Antes de escribir una sola línea de Swift, entiende quién va a usar tu feature.

```swift
// ❌ Sin Product Thinking: Asumir que todos tienen conexión
func fetchUserProfile() async throws -> UserProfile {
    let (data, _) = try await URLSession.shared.data(from: profileURL)
    return try JSONDecoder().decode(UserProfile.self, from: data)
}

// ✅ Con Product Thinking: Considerar el escenario offline
func fetchUserProfile() async -> UserProfile {
    // Primero intentar mostrar datos en caché para experiencia inmediata
    if let cached = localCache.getUserProfile() {
        return cached
    }

    do {
        let (data, _) = try await URLSession.shared.data(from: profileURL)
        let profile = try JSONDecoder().decode(UserProfile.self, from: data)
        localCache.save(profile) // Guardar para uso offline
        return profile
    } catch {
        // Degradar graciosamente: mostrar perfil básico desde Keychain
        return UserProfile.offlinePlaceholder()
    }
}
```

**Pregunta clave**: *¿Qué experimenta mi usuario en Oaxaca con 2G cuando abre esta pantalla?*

### Pilar 2: Visión de negocio

Entiende cómo tu empresa genera dinero y cómo tu feature contribuye a eso.

```swift
// Un desarrollador con Product Thinking estructura su analytics así:
enum ProductEvent: String {
    // Eventos de activación (¿el usuario entiende el valor?)
    case onboardingCompleted = "onboarding_completed"
    case firstPurchaseViewed = "first_purchase_viewed"

    // Eventos de retención (¿vuelve el usuario?)
    case appOpenedDay2 = "app_opened_day_2"
    case featureUsedRepeatedly = "feature_used_3_plus_times"

    // Eventos de monetización (¿genera revenue?)
    case subscriptionStarted = "subscription_started"
    case subscriptionCancelled = "subscription_cancelled"
    case cancellationReasonProvided = "cancellation_reason_provided"
}

struct AnalyticsService {
    func track(_ event: ProductEvent, properties: [String: Any] = [:]) {
        var enrichedProperties = properties

        // Contexto de producto que ayuda a tomar decisiones
        enrichedProperties["device_model"] = UIDevice.current.modelName
        enrichedProperties["os_version"] = UIDevice.current.systemVersion
        enrichedProperties["app_version"] = Bundle.main.appVersion
        enrichedProperties["locale"] = Locale.current.identifier
        enrichedProperties["connectivity"] = NetworkMonitor.shared.currentType.rawValue

        // Enviar a tu herramienta de analytics
        provider.log(event.rawValue, properties: enrichedProperties)
    }
}
```

**Pregunta clave**: *¿Qué métrica del negocio mueve esta feature? Si no mueve ninguna, ¿por qué la estamos construyendo?*

### Pilar 3: Priorización implacable

No todo lo que se puede construir se debe construir. Un dev con Product Thinking ayuda a priorizar.

```swift
// Framework mental para evaluar un feature request:

struct FeatureEvaluation {
    let featureName: String
    let userImpact: Impact        // ¿Cuántos usuarios se benefician?
    let businessImpact: Impact    // ¿Mueve métricas clave?
    let technicalEffort: Effort   // ¿Cuánto cuesta implementarlo?
    let technicalRisk: Risk       // ¿Puede romper algo existente?

    enum Impact: Int, Comparable {
        case low = 1, medium = 2, high = 3, critical = 4

        static func < (lhs: Impact, rhs: Impact) -> Bool {
            lhs.rawValue < rhs.rawValue
        }
    }

    enum Effort: Int {
        case trivial = 1, small = 2, medium = 3, large = 5, massive = 8
    }

    enum Risk: Int {
        case minimal = 1, moderate = 2, significant = 3, critical = 5
    }

    /// Puntaje de priorización: mayor es mejor
    var priorityScore: Double {
        let impactScore = Double(userImpact.rawValue + businessImpact.rawValue)
        let costScore = Double(technicalEffort.rawValue + technicalRisk.rawValue)
        return impactScore / costScore
    }
}

// Ejemplo de uso en una discusión de planning:
let darkMode = FeatureEvaluation(
    featureName: "Dark Mode",
    userImpact: .medium,
    businessImpact: .low,
    technicalEffort: .large,
    technicalRisk: .moderate
)

let offlineMode = FeatureEvaluation(
    featureName: "Modo Offline",
    userImpact: .critical,      // En LATAM, esto es crítico
    businessImpact: .high,      // Reduce churn significativamente
    technicalEffort: .medium,
    technicalRisk: .moderate
)

print(darkMode.priorityScore)    // 1.0
print(offlineMode.priorityScore) // 1.4 → Priorizar esto primero
```

### Pilar 4: Iteración sobre perfección

El Product Thinking favorece **entregas incrementales** sobre releases monolíticos.

```swift
// Fase 1: MVP - Feature flag con funcionalidad básica
struct FeatureFlags {
    /// Usar un servicio remoto como Firebase Remote Config
    /// para activar features gradualmente
    static func isEnabled(_ feature: Feature) -> Bool {
        RemoteConfig.shared.boolValue(forKey: feature.rawValue)
    }

    enum Feature: String {
        case newCheckoutFlow = "new_checkout_flow"
        case aiRecommendations = "ai_recommendations"
        case offlineMode = "offline_mode"
    }
}

// En tu vista:
struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()

    var body: some View {
        NavigationStack {
            List(viewModel.products) { product in
                ProductRowView(product: product)
            }
            .overlay {
                if viewModel.products.isEmpty && viewModel.isLoading {
                    ProgressView("Cargando productos...")
                } else if viewModel.products.isEmpty && !viewModel.isLoading {
                    emptyStateView
                }
            }
            .refreshable {
                await viewModel.refresh()
            }
        }
    }

    @ViewBuilder
    private var emptyStateView: some View {
        // Con Product Thinking: el estado vacío no es un error,
        // es una oportunidad de guiar al usuario
        ContentUnavailableView {
            Label("Sin productos", systemImage: "bag")
        } description: {
            if NetworkMonitor.shared.isConnected {
                Text("No encontramos productos disponibles en tu zona.")
            } else {
                Text("Parece que no tienes conexión. Revisa tu internet e intenta de nuevo.")
            }
        } actions: {
            Button("Reintentar") {
                Task { await viewModel.refresh() }
            }
            .buttonStyle(.borderedProminent)
        }
    }
}
```

### Pilar 5: Decisiones basadas en datos

No adivines: mide.

```swift
// Implementar un A/B test simple para validar una hipótesis de producto
final class ExperimentManager: ObservableObject {
    static let shared = ExperimentManager()

    struct Experiment {
        let name: String
        let variants: [String]
        let assignedVariant: String

        var isControl: Bool { assignedVariant == "control" }
    }

    func getExperiment(_ name: String) -> Experiment {
        // En producción, esto vendría de Firebase A/B Testing,
        // Amplitude Experiment, o tu backend
        let variant = RemoteConfig.shared.stringValue(forKey: "experiment_\(name)")

        return Experiment(
            name: name,
            variants: ["control", "variant_a"],
            assignedVariant: variant ?? "control"
        )
    }
}

// Uso en una vista:
struct CheckoutView: View {
    let experiment = ExperimentManager.shared
        .getExperiment("checkout_button_copy")

    var body: some View {
        VStack {
            // ... resto del checkout

            Button(action: completePurchase) {
                Text(checkoutButtonText)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .onAppear {
                AnalyticsService().track(
                    .experimentViewed,
                    properties: [
                        "experiment": experiment.name,
                        "variant": experiment.assignedVariant
                    ]
                )
            }
        }
    }

    private var checkoutButtonText: String {
        // Hipótesis: "Comprar ahora" convierte mejor
        // que "Proceder al pago" en LATAM
        experiment.isControl ? "Proceder al pago" : "¡Comprar ahora! 🛒"
    }
}
```

---

## Framework práctico: Las 5 preguntas del Dev con Product Thinking

Antes de empezar a codear cualquier feature, hazte estas preguntas:

| # | Pregunta | Si no puedes responder... |
|---|----------|--------------------------|
| 1 | **¿Qué problema del usuario resuelve esto?** | Pide contexto al PM o investiga por tu cuenta |
| 2 | **¿Cómo sabremos que funciona?** | Define métricas de éxito antes de escribir código |
| 3 | **¿Cuál es la versión más simple que entrega valor?** | Reduce el scope hasta encontrar el MVP real |
| 4 | **¿Qué puede salir mal para el usuario?** | Diseña para los edge cases: offline, errores, dispositivos viejos |
| 5 | **¿Qué aprendemos si esto falla?** | Si no aprendes nada al fallar, replantea el enfoque |

---

## Pasos accionables para desarrollar tu Product Thinking

### Semana 1-2: Observar
- [ ] Descarga tu propia app y úsala como un usuario real durante una semana
- [ ] Lee las últimas 50 reseñas en App Store (las de 1-3 estrellas son oro)
- [ ] Pide acceso a las herramientas de analytics de tu equipo (Mixpanel, Amplitude, Firebase Analytics)
- [ ] Identifica los 3 flujos más usados y los 3 puntos donde más usuarios abandonan

### Semana 3-4: Preguntar
- [ ] En el próximo sprint planning, pregunta *"¿qué métrica mueve este ticket?"*
- [ ] Habla con alguien de soporte al cliente y pregúntale cuáles son las quejas más frecuentes
- [ ] Propón una mejora basada en datos, no en opinión

### Mes 2: Proponer
- [ ] Escribe un **one-pager** de una mejora técnica con impacto en producto
- [ ] Incluye: problema, propuesta, esfuerzo estimado, métrica de éxito
- [ ] Preséntalo al equipo

### Mes 3+: Liderar
- [ ] Implementa analytics significativos en tu feature
- [ ] Haz seguimiento post-lanzamiento: ¿los números confirman tu hipótesis?
- [ ] Comparte los aprendizajes con el equipo

---

## Ejemplo real: Product Thinking en acción

Imagina que trabajas en una app de delivery en LATAM. El PM te pide implementar un **"selector de propina"** en el checkout.

### Sin Product Thinking:
> "Ok, pongo 3 botones con 10%, 15%, 20% y lo subo."

### Con Product Thinking:

```swift
struct TipSelectorView: View {
    // Investigación previa:
    // - El 60% de nuestros usuarios están en zonas donde el salario
    //   mínimo es bajo. Porcentajes altos pueden asustar.
    // - Los repartidores reportan que solo el 20% de pedidos
    //   incluyen propina.
    // - Hipótesis: mostrar montos fijos en moneda local convierte
    //   mejor que porcentajes.

    @Binding var selectedTip: TipOption
    let orderTotal: Decimal
    let currencyCode: String // "MXN", "COP", "ARS"

    enum TipOption: Equatable {
        case none
        case preset(Decimal)
        case custom(Decimal)
    }

    // Montos calibrados por país basados en datos reales
    private var presetAmounts: [Decimal] {
        switch currencyCode {
        case "MXN": return [10, 20, 30]      // ~$0.50, $1, $1.50 USD
        case "COP": return [2000, 5000, 8000] // ~$0.50, $1.25, $2 USD
        case "ARS": return [500, 1000, 2000]  // Ajustar por inflación
        default: return [1, 2, 5]
        }
    }

    var body: