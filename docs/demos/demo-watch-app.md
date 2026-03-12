---
sidebar_position: 1
title: Demo Watch App
---

# Demo Watch App: Tu Primera Aplicación para Apple Watch

## ¿Qué es una Watch App?

Una **Watch App** es una aplicación diseñada específicamente para ejecutarse en el Apple Watch. Desde la introducción de **SwiftUI**, el desarrollo para watchOS se ha simplificado enormemente, permitiendo crear interfaces nativas con el mismo lenguaje declarativo que usamos en iOS.

En esta demo construiremos una aplicación completa paso a paso: un **rastreador de hidratación** que permite al usuario registrar vasos de agua consumidos durante el día. Es un proyecto sencillo pero que abarca los conceptos fundamentales que necesitas dominar.

## ¿Por qué es importante para un dev iOS en LATAM?

El mercado de wearables en Latinoamérica está creciendo de manera acelerada. Según datos recientes, las ventas de Apple Watch en México, Brasil, Colombia y Chile han aumentado consistentemente año tras año. Esto representa una **oportunidad concreta** para desarrolladores de la región:

- **Diferenciación profesional**: Muy pocos desarrolladores en LATAM dominan watchOS. Agregar esta habilidad a tu perfil te posiciona por encima de la competencia inmediatamente.
- **Aplicaciones de salud**: La región tiene una demanda creciente de soluciones de salud digital. El Apple Watch con sus sensores (ritmo cardíaco, oxígeno en sangre, acelerómetro) es la plataforma ideal.
- **Freelancing internacional**: Clientes en Estados Unidos y Europa buscan frecuentemente desarrolladores que puedan extender sus apps iOS al Apple Watch. Los devs LATAM con esta especialidad pueden acceder a proyectos mejor remunerados.
- **Ecosistema completo**: Dominar watchOS demuestra que entiendes el ecosistema Apple de forma integral, no solo una parte.

## Requisitos Previos

Antes de comenzar, asegúrate de tener:

- **Xcode 15** o superior instalado
- Conocimientos básicos de **SwiftUI**
- Simulador de Apple Watch configurado (viene incluido con Xcode)
- macOS Sonoma o superior (recomendado)

:::tip No necesitas un Apple Watch físico
El simulador de Xcode es suficiente para desarrollar y probar. Solo necesitarás un dispositivo real para probar sensores como el acelerómetro o el monitor cardíaco.
:::

## Paso 1: Crear el Proyecto

Abre Xcode y sigue estos pasos:

1. Selecciona **File → New → Project**
2. En la pestaña **watchOS**, elige **App**
3. Configura el proyecto:
   - **Product Name**: `HydrationTracker`
   - **Interface**: SwiftUI
   - **Language**: Swift
   - **Watch-only App**: Activado (para esta demo no necesitamos companion app)

```
📁 HydrationTracker
├── 📁 HydrationTrackerWatch
│   ├── HydrationTrackerApp.swift
│   ├── ContentView.swift
│   └── Assets.xcassets
└── 📁 HydrationTrackerWatch Tests
```

:::info Watch-only vs. Companion App
Una **Watch-only App** funciona de manera independiente sin necesitar una app en el iPhone. Una **Companion App** requiere una app iOS asociada. Para proyectos nuevos, Apple recomienda empezar con Watch-only siempre que sea posible.
:::

## Paso 2: Definir el Modelo de Datos

Creemos nuestro modelo para manejar el registro de hidratación. Crea un nuevo archivo llamado `HydrationModel.swift`:

```swift
import Foundation
import SwiftUI

// MARK: - Modelo de datos para el registro de hidratación
struct WaterEntry: Identifiable, Codable {
    let id: UUID
    let amount: Double // en mililitros
    let timestamp: Date
    
    init(id: UUID = UUID(), amount: Double, timestamp: Date = .now) {
        self.id = id
        self.amount = amount
        self.timestamp = timestamp
    }
}

// MARK: - ViewModel principal
@Observable
class HydrationViewModel {
    
    private let dailyGoal: Double = 2000 // 2 litros como meta diaria
    private let storageKey = "water_entries"
    
    var entries: [WaterEntry] = []
    
    var todayEntries: [WaterEntry] {
        let calendar = Calendar.current
        return entries.filter { calendar.isDateInToday($0.timestamp) }
    }
    
    var totalConsumedToday: Double {
        todayEntries.reduce(0) { $0 + $1.amount }
    }
    
    var progress: Double {
        min(totalConsumedToday / dailyGoal, 1.0)
    }
    
    var glassesCount: Int {
        todayEntries.count
    }
    
    var remainingML: Double {
        max(dailyGoal - totalConsumedToday, 0)
    }
    
    var goalReached: Bool {
        totalConsumedToday >= dailyGoal
    }
    
    init() {
        loadEntries()
    }
    
    // MARK: - Acciones
    
    func addWater(amount: Double = 250) {
        let entry = WaterEntry(amount: amount)
        entries.append(entry)
        saveEntries()
    }
    
    func removeLastEntry() {
        guard let lastTodayEntry = todayEntries.last else { return }
        entries.removeAll { $0.id == lastTodayEntry.id }
        saveEntries()
    }
    
    func resetToday() {
        let calendar = Calendar.current
        entries.removeAll { calendar.isDateInToday($0.timestamp) }
        saveEntries()
    }
    
    // MARK: - Persistencia con UserDefaults
    
    private func saveEntries() {
        if let data = try? JSONEncoder().encode(entries) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
    
    private func loadEntries() {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([WaterEntry].self, from: data) else {
            return
        }
        entries = decoded
    }
}
```

### Puntos clave del modelo

- Usamos `@Observable` (disponible desde watchOS 10) en lugar de `ObservableObject` para simplificar el código reactivo.
- La persistencia se hace con `UserDefaults` y `Codable`, suficiente para una app sencilla.
- El cálculo de progreso se limita a `1.0` para evitar que la barra de progreso se desborde visualmente.

## Paso 3: Construir la Interfaz Principal

Reemplaza el contenido de `ContentView.swift` con lo siguiente:

```swift
import SwiftUI

struct ContentView: View {
    
    @State private var viewModel = HydrationViewModel()
    @State private var showingConfirmation = false
    @State private var animateProgress = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 12) {
                    // MARK: - Indicador circular de progreso
                    ProgressSection(
                        progress: viewModel.progress,
                        consumed: viewModel.totalConsumedToday,
                        remaining: viewModel.remainingML,
                        goalReached: viewModel.goalReached
                    )
                    
                    // MARK: - Botones de acción rápida
                    QuickActionButtons(viewModel: viewModel)
                    
                    // MARK: - Historial del día
                    if !viewModel.todayEntries.isEmpty {
                        TodayHistorySection(
                            entries: viewModel.todayEntries,
                            onReset: { showingConfirmation = true }
                        )
                    }
                }
                .padding(.horizontal, 4)
            }
            .navigationTitle("💧 Hidratación")
            .confirmationDialog(
                "¿Reiniciar el conteo de hoy?",
                isPresented: $showingConfirmation,
                titleVisibility: .visible
            ) {
                Button("Reiniciar", role: .destructive) {
                    viewModel.resetToday()
                }
                Button("Cancelar", role: .cancel) {}
            }
        }
    }
}

// MARK: - Sección de progreso circular

struct ProgressSection: View {
    let progress: Double
    let consumed: Double
    let remaining: Double
    let goalReached: Bool
    
    var body: some View {
        ZStack {
            // Fondo del círculo
            Circle()
                .stroke(Color.blue.opacity(0.2), lineWidth: 8)
            
            // Progreso animado
            Circle()
                .trim(from: 0, to: progress)
                .stroke(
                    goalReached ? Color.green : Color.blue,
                    style: StrokeStyle(lineWidth: 8, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 0.5), value: progress)
            
            // Contenido central
            VStack(spacing: 2) {
                if goalReached {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundStyle(.green)
                    Text("¡Meta cumplida!")
                        .font(.caption2)
                        .foregroundStyle(.green)
                } else {
                    Text("\(Int(consumed))")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundStyle(.blue)
                    Text("de 2000 ml")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .frame(height: 120)
        .padding(.top, 4)
    }
}

// MARK: - Botones de acción rápida

struct QuickActionButtons: View {
    let viewModel: HydrationViewModel
    
    private let waterAmounts: [(label: String, ml: Double)] = [
        ("🥤 150ml", 150),
        ("🥛 250ml", 250),
        ("🍶 500ml", 500)
    ]
    
    var body: some View {
        VStack(spacing: 6) {
            Text("Agregar agua")
                .font(.caption)
                .foregroundStyle(.secondary)
            
            ForEach(waterAmounts, id: \.ml) { option in
                Button(action: {
                    WKInterfaceDevice.current().play(.click)
                    viewModel.addWater(amount: option.ml)
                }) {
                    Text(option.label)
                        .frame(maxWidth: .infinity)
                }
                .tint(.blue)
            }
            
            if !viewModel.todayEntries.isEmpty {
                Button(action: {
                    viewModel.removeLastEntry()
                }) {
                    Label("Deshacer último", systemImage: "arrow.uturn.backward")
                        .font(.caption2)
                        .frame(maxWidth: .infinity)
                }
                .tint(.orange)
            }
        }
    }
}

// MARK: - Historial del día

struct TodayHistorySection: View {
    let entries: [WaterEntry]
    let onReset: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("Hoy: \(entries.count) registros")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                
                Spacer()
                
                Button("Reiniciar", action: onReset)
                    .font(.caption2)
                    .foregroundStyle(.red)
            }
            
            ForEach(entries.suffix(5).reversed()) { entry in
                HStack {
                    Image(systemName: "drop.fill")
                        .font(.caption2)
                        .foregroundStyle(.blue)
                    
                    Text("\(Int(entry.amount)) ml")
                        .font(.caption2)
                    
                    Spacer()
                    
                    Text(entry.timestamp, style: .time)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(.top, 8)
    }
}

#Preview {
    ContentView()
}
```

## Paso 4: Configurar el Entry Point

Asegúrate de que `HydrationTrackerApp.swift` tenga la configuración correcta:

```swift
import SwiftUI

@main
struct HydrationTrackerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Paso 5: Agregar Haptic Feedback

Una de las características más importantes del Apple Watch es la retroalimentación háptica. Ya incluimos `WKInterfaceDevice.current().play(.click)` en los botones, pero podemos mejorar la experiencia:

```swift
import WatchKit

// MARK: - Extensión de utilidad para haptics
extension WKInterfaceDevice {
    static func haptic(_ type: WKHapticType) {
        WKInterfaceDevice.current().play(type)
    }
}

// Uso en diferentes contextos:
// Al agregar agua:
WKInterfaceDevice.haptic(.click)

// Al alcanzar la meta diaria:
WKInterfaceDevice.haptic(.success)

// Al reiniciar el conteo:
WKInterfaceDevice.haptic(.failure)

// Al deshacer una acción:
WKInterfaceDevice.haptic(.retry)
```

## Paso 6: Agregar una Complicación (Bonus)

Las **complicaciones** son widgets que aparecen en la carátula del reloj. Para agregar una complicación básica que muestre el progreso de hidratación, crea un archivo `HydrationWidget.swift`:

```swift
import WidgetKit
import SwiftUI

// MARK: - Timeline Provider
struct HydrationTimelineProvider: TimelineProvider {
    
    func placeholder(in context: Context) -> HydrationTimelineEntry {
        HydrationTimelineEntry(date: .now, consumed: 1250, goal: 2000)
    }
    
    func getSnapshot(in context: Context, completion: @escaping (HydrationTimelineEntry) -> Void) {
        let entry = HydrationTimelineEntry(date: .now, consumed: 1250, goal: 2000)
        completion(entry)
    }
    
    func getTimeline(in context: Context, completion: @escaping (Timeline<HydrationTimelineEntry>) -> Void) {
        // Leer datos actuales de UserDefaults
        let consumed = getCurrentConsumption()
        let entry = HydrationTimelineEntry(date: .now, consumed: consumed, goal: 2000)
        
        // Actualizar cada 30 minutos
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 30, to: .now)!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }
    
    private func getCurrentConsumption() -> Double {
        guard let data = UserDefaults.standard.data(forKey: "water_entries"),
              let entries = try? JSONDecoder().decode([WaterEntry].self, from: data) else {
            return 0
        }
        let calendar = Calendar.current
        return entries
            .filter { calendar.isDateInToday($0.timestamp) }
            .reduce(0) { $0 + $1.amount }
    