---
sidebar_position: 1
title: Demo Health Tracker
---

# Demo Health Tracker: Construyendo una App de Salud con Swift

## ¿Qué vamos a construir?

En esta demo construiremos paso a paso una **aplicación de seguimiento de salud** que integra HealthKit, arquitectura MVVM, SwiftUI y persistencia local. Esta app permitirá al usuario registrar sus pasos diarios, frecuencia cardíaca, horas de sueño y peso, visualizando su progreso con gráficas interactivas.

Este proyecto es mucho más que un ejercicio técnico: representa una **oportunidad real de mercado** para developers iOS en Latinoamérica.

---

## ¿Por qué una Health Tracker App es relevante para devs en LATAM?

El sector de salud digital en América Latina está en pleno crecimiento. Según reportes recientes, el mercado de **mHealth** (mobile health) en la región crece a tasas superiores al 25% anual. Sin embargo, la mayoría de aplicaciones de salud disponibles están diseñadas para mercados anglosajones, dejando necesidades específicas sin cubrir:

- **Sistemas de salud fragmentados**: En México, Colombia, Argentina y otros países, los usuarios necesitan gestionar su información de salud de forma personal porque no existe un expediente clínico electrónico unificado.
- **Prevención como prioridad**: Enfermedades crónicas como diabetes e hipertensión tienen altísima prevalencia en LATAM. Herramientas de automonitoreo pueden marcar la diferencia.
- **Apple Watch en crecimiento**: La adopción de wearables de Apple crece sostenidamente en la región, ampliando el mercado potencial.
- **Portafolio profesional diferenciado**: Dominar HealthKit y visualización de datos de salud te posiciona para roles en startups de health-tech, un sector que levanta cada vez más inversión en la región.

---

## Arquitectura del proyecto

```
HealthTracker/
├── App/
│   └── HealthTrackerApp.swift
├── Models/
│   ├── HealthMetric.swift
│   ├── DailyLog.swift
│   └── UserProfile.swift
├── ViewModels/
│   ├── DashboardViewModel.swift
│   ├── StepsViewModel.swift
│   ├── HeartRateViewModel.swift
│   └── ProfileViewModel.swift
├── Views/
│   ├── Dashboard/
│   │   ├── DashboardView.swift
│   │   └── MetricCardView.swift
│   ├── Steps/
│   │   ├── StepsDetailView.swift
│   │   └── StepsChartView.swift
│   ├── HeartRate/
│   │   └── HeartRateView.swift
│   ├── Profile/
│   │   └── ProfileView.swift
│   └── Shared/
│       ├── ChartView.swift
│       └── ProgressRingView.swift
├── Services/
│   ├── HealthKitManager.swift
│   ├── PersistenceManager.swift
│   └── NotificationManager.swift
├── Utilities/
│   ├── Extensions/
│   │   ├── Date+Extensions.swift
│   │   └── Color+Extensions.swift
│   └── Constants.swift
└── Resources/
    └── Assets.xcassets
```

Usaremos **MVVM** como patrón arquitectónico principal, aprovechando la reactividad nativa de SwiftUI con `@Observable` (iOS 17+) y como alternativa `ObservableObject` para compatibilidad con versiones anteriores.

---

## Paso 1: Configurar el modelo de datos

Comenzamos definiendo las estructuras que representan las métricas de salud:

```swift
import Foundation

enum MetricType: String, CaseIterable, Codable {
    case steps = "Pasos"
    case heartRate = "Frecuencia Cardíaca"
    case sleep = "Horas de Sueño"
    case weight = "Peso"
    
    var unit: String {
        switch self {
        case .steps: return "pasos"
        case .heartRate: return "bpm"
        case .sleep: return "hrs"
        case .weight: return "kg"
        }
    }
    
    var icon: String {
        switch self {
        case .steps: return "figure.walk"
        case .heartRate: return "heart.fill"
        case .sleep: return "moon.fill"
        case .weight: return "scalemass.fill"
        }
    }
    
    var dailyGoalDefault: Double {
        switch self {
        case .steps: return 10_000
        case .heartRate: return 0 // No aplica meta diaria
        case .sleep: return 8
        case .weight: return 0 // Meta personalizada
        }
    }
}

struct HealthMetric: Identifiable, Codable {
    let id: UUID
    let type: MetricType
    let value: Double
    let date: Date
    
    init(id: UUID = UUID(), type: MetricType, value: Double, date: Date = .now) {
        self.id = id
        self.type = type
        self.value = value
        self.date = date
    }
}

struct DailyLog: Identifiable, Codable {
    let id: UUID
    let date: Date
    var metrics: [HealthMetric]
    var notes: String
    
    init(id: UUID = UUID(), date: Date = .now, metrics: [HealthMetric] = [], notes: String = "") {
        self.id = id
        self.date = date
        self.metrics = metrics
        self.notes = notes
    }
    
    var stepsCount: Double? {
        metrics.first(where: { $0.type == .steps })?.value
    }
    
    var heartRate: Double? {
        metrics.first(where: { $0.type == .heartRate })?.value
    }
    
    var sleepHours: Double? {
        metrics.first(where: { $0.type == .sleep })?.value
    }
}

struct UserProfile: Codable {
    var name: String
    var age: Int
    var heightCm: Double
    var targetWeight: Double?
    var dailyStepsGoal: Double
    var dailySleepGoal: Double
    
    static let `default` = UserProfile(
        name: "",
        age: 25,
        heightCm: 170,
        targetWeight: nil,
        dailyStepsGoal: 10_000,
        dailySleepGoal: 8
    )
}
```

---

## Paso 2: Integrar HealthKit

HealthKit es el framework de Apple que permite leer y escribir datos de salud del usuario. **Es fundamental solicitar permisos de forma transparente y respetuosa** — algo que los usuarios latinoamericanos valoran especialmente dada la creciente conciencia sobre privacidad de datos.

### Configuración previa en Xcode

1. Ve a tu target → **Signing & Capabilities** → pulsa **+ Capability** → agrega **HealthKit**.
2. En tu archivo `Info.plist`, agrega las siguientes claves:

```xml
<key>NSHealthShareUsageDescription</key>
<string>Necesitamos acceder a tus datos de salud para mostrarte tu progreso diario.</string>
<key>NSHealthUpdateUsageDescription</key>
<string>Necesitamos escribir datos de salud para registrar tus métricas.</string>
```

### Implementación del servicio HealthKit

```swift
import HealthKit
import Foundation

final class HealthKitManager {
    
    static let shared = HealthKitManager()
    
    private let healthStore = HKHealthStore()
    
    private init() {}
    
    // MARK: - Verificar disponibilidad
    
    var isAvailable: Bool {
        HKHealthStore.isHealthDataAvailable()
    }
    
    // MARK: - Solicitar permisos
    
    func requestAuthorization() async throws {
        guard isAvailable else {
            throw HealthKitError.notAvailable
        }
        
        let readTypes: Set<HKObjectType> = [
            HKQuantityType(.stepCount),
            HKQuantityType(.heartRate),
            HKQuantityType(.bodyMass),
            HKCategoryType(.sleepAnalysis)
        ]
        
        let writeTypes: Set<HKSampleType> = [
            HKQuantityType(.bodyMass)
        ]
        
        try await healthStore.requestAuthorization(
            toShare: writeTypes,
            read: readTypes
        )
    }
    
    // MARK: - Obtener pasos del día
    
    func fetchTodaySteps() async throws -> Double {
        let stepsType = HKQuantityType(.stepCount)
        let predicate = HKQuery.predicateForSamples(
            withStart: Calendar.current.startOfDay(for: .now),
            end: .now,
            options: .strictStartDate
        )
        
        let descriptor = HKStatisticsQueryDescriptor(
            predicate: .quantitySample(type: stepsType, predicate: predicate),
            options: .cumulativeSum
        )
        
        let result = try await descriptor.result(for: healthStore)
        
        return result?.sumQuantity()?.doubleValue(for: .count()) ?? 0
    }
    
    // MARK: - Obtener pasos de la última semana
    
    func fetchWeeklySteps() async throws -> [HealthMetric] {
        let stepsType = HKQuantityType(.stepCount)
        let calendar = Calendar.current
        
        guard let startDate = calendar.date(byAdding: .day, value: -6, to: calendar.startOfDay(for: .now)) else {
            return []
        }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startDate,
            end: .now,
            options: .strictStartDate
        )
        
        let interval = DateComponents(day: 1)
        
        let query = HKStatisticsCollectionQueryDescriptor(
            predicate: .quantitySample(type: stepsType, predicate: predicate),
            options: .cumulativeSum,
            anchorDate: startDate,
            intervalComponents: interval
        )
        
        let collection = try await query.result(for: healthStore)
        
        var metrics: [HealthMetric] = []
        
        collection.enumerateStatistics(from: startDate, to: .now) { statistics, _ in
            let value = statistics.sumQuantity()?.doubleValue(for: .count()) ?? 0
            let metric = HealthMetric(
                type: .steps,
                value: value,
                date: statistics.startDate
            )
            metrics.append(metric)
        }
        
        return metrics
    }
    
    // MARK: - Obtener frecuencia cardíaca más reciente
    
    func fetchLatestHeartRate() async throws -> Double? {
        let heartRateType = HKQuantityType(.heartRate)
        
        let descriptor = HKSampleQueryDescriptor(
            predicates: [.quantitySample(type: heartRateType)],
            sortDescriptors: [SortDescriptor(\.endDate, order: .reverse)],
            limit: 1
        )
        
        let samples = try await descriptor.result(for: healthStore)
        
        guard let sample = samples.first else { return nil }
        
        let bpmUnit = HKUnit.count().unitDivided(by: .minute())
        return sample.quantity.doubleValue(for: bpmUnit)
    }
    
    // MARK: - Registrar peso
    
    func saveWeight(_ weightKg: Double, date: Date = .now) async throws {
        let weightType = HKQuantityType(.bodyMass)
        let quantity = HKQuantity(unit: .gramUnit(with: .kilo), doubleValue: weightKg)
        let sample = HKQuantitySample(type: weightType, quantity: quantity, start: date, end: date)
        
        try await healthStore.save(sample)
    }
    
    // MARK: - Errores
    
    enum HealthKitError: LocalizedError {
        case notAvailable
        case authorizationDenied
        
        var errorDescription: String? {
            switch self {
            case .notAvailable:
                return "HealthKit no está disponible en este dispositivo."
            case .authorizationDenied:
                return "No se otorgaron los permisos necesarios para acceder a los datos de salud."
            }
        }
    }
}
```

---

## Paso 3: Construir el ViewModel del Dashboard

```swift
import SwiftUI

@Observable
final class DashboardViewModel {
    
    // MARK: - Estado
    
    var todaySteps: Double = 0
    var latestHeartRate: Double?
    var weeklySteps: [HealthMetric] = []
    var sleepHours: Double = 0
    var isLoading = false
    var errorMessage: String?
    var hasHealthKitPermission = false
    
    // MARK: - Dependencias
    
    private let healthKit = HealthKitManager.shared
    
    // MARK: - Propiedades calculadas
    
    var stepsProgress: Double {
        min(todaySteps / 10_000, 1.0)
    }
    
    var stepsFormatted: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.locale = Locale(identifier: "es_MX")
        return formatter.string(from: NSNumber(value: todaySteps)) ?? "0"
    }
    
    var heartRateFormatted: String {
        guard let rate = latestHeartRate else { return "--" }
        return "\(Int(rate))"
    }
    
    var heartRateStatus: HeartRateStatus {
        guard let rate = latestHeartRate else { return .unknown }
        switch rate {
        case ..<60: return .low
        case 60...100: return .normal
        default: return .high
        }
    }
    
    // MARK: - Acciones
    
    func onAppear() async {
        await requestPermissions()
        await loadAllData()
    }
    
    func refresh() async {
        await loadAllData()
    }
    
    private func requestPermissions() async {
        guard healthKit.isAvailable else {
            errorMessage = "HealthKit no está disponible en este dispositivo."
            return
        }
        
        do {
            try await healthKit.requestAuthorization()
            hasHealthKitPermission = true
        } catch {
            errorMessage = "No pudimos acceder a tus datos de salud: \(error.localizedDescription)"
        }
    }
    
    private func loadAllData() async {
        isLoading = true
        errorMessage = nil
        
        do {
            async let steps = healthKit.fetchTodaySteps()
            async let heartRate = healthKit.fetchLatestHeartRate()
            async let weekly = healthKit.fetchWeeklySteps()
            
            todaySteps = try await steps
            latestHeartRate = try await heartRate
            weeklySteps = try await weekly
        } catch {
            errorMessage = "Error al cargar datos: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    // MARK: - Tipos auxiliares
    
    enum HeartRateStatus {
        case low, normal, high, unknown
        
        var color: Color {
            switch self {
            case .low: return .blue
            case .normal: return .green
            case .high: return .red
            case .unknown: return .gray
            }
        }
        
        var label: String {
            switch self {
            case .low: return "