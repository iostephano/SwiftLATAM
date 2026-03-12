---
sidebar_position: 1
title: Healthtech Ios
---

# HealthTech en iOS: Desarrollo de Aplicaciones de Salud

## ¿Qué es HealthTech en el contexto iOS?

HealthTech (tecnología de salud) en iOS abarca el desarrollo de aplicaciones que interactúan con datos de salud del usuario, dispositivos médicos, wearables y servicios de telemedicina. Apple ha construido un ecosistema robusto alrededor de la salud con frameworks como **HealthKit**, **CareKit**, **ResearchKit** y la integración nativa con **Apple Watch**.

Como desarrollador iOS especializado en HealthTech, trabajas en la intersección entre tecnología y bienestar humano: desde apps que monitorean la frecuencia cardíaca hasta plataformas completas de telemedicina que conectan pacientes con profesionales de salud.

## ¿Por qué es importante para un dev iOS en LATAM?

La industria HealthTech en Latinoamérica está experimentando un crecimiento explosivo. Estas son las razones clave:

- **Demanda creciente**: La pandemia de COVID-19 aceleró la adopción de telemedicina en toda la región. Países como México, Colombia, Brasil y Argentina han visto surgir startups de salud digital que necesitan talento iOS.
- **Brecha de talento especializado**: Pocos desarrolladores en LATAM dominan HealthKit y los estándares de salud digital (HL7 FHIR, HIPAA). Esto representa una ventaja competitiva enorme.
- **Salarios premium**: Las posiciones en HealthTech suelen pagar entre un 20-40% más que el desarrollo iOS generalista, especialmente en empresas estadounidenses que contratan remotamente en LATAM.
- **Impacto social real**: En regiones donde el acceso a servicios médicos es limitado, las apps de salud pueden transformar literalmente la vida de millones de personas.
- **Regulación en evolución**: México (COFEPRIS), Colombia (INVIMA) y otros países están creando marcos regulatorios para salud digital, lo que profesionaliza el sector.

## Frameworks fundamentales del ecosistema Apple Health

### 1. HealthKit — El pilar central

HealthKit es el framework que permite leer y escribir datos de salud almacenados en la app **Salud** (Health) del iPhone.

```swift
import HealthKit

class HealthKitManager {
    
    let healthStore = HKHealthStore()
    
    // MARK: - Verificar disponibilidad
    func isHealthDataAvailable() -> Bool {
        return HKHealthStore.isHealthDataAvailable()
    }
    
    // MARK: - Solicitar permisos
    func requestAuthorization() async throws {
        // Tipos de datos que queremos LEER
        let readTypes: Set<HKObjectType> = [
            HKQuantityType(.heartRate),
            HKQuantityType(.stepCount),
            HKQuantityType(.bloodGlucose),
            HKQuantityType(.bodyMass),
            HKQuantityType(.bloodPressureSystolic),
            HKQuantityType(.bloodPressureDiastolic),
            HKCategoryType(.sleepAnalysis)
        ]
        
        // Tipos de datos que queremos ESCRIBIR
        let writeTypes: Set<HKSampleType> = [
            HKQuantityType(.stepCount),
            HKQuantityType(.bodyMass)
        ]
        
        try await healthStore.requestAuthorization(
            toShare: writeTypes,
            read: readTypes
        )
    }
}
```

> ⚠️ **Nota importante**: Apple es extremadamente estricto con los permisos de HealthKit durante el proceso de revisión en App Store. Debes justificar **cada tipo de dato** que solicitas y tu app será rechazada si pides permisos innecesarios.

### 2. Lectura de datos — Pasos diarios

```swift
extension HealthKitManager {
    
    /// Obtiene el conteo total de pasos del día actual
    func fetchTodayStepCount() async throws -> Double {
        let stepType = HKQuantityType(.stepCount)
        
        let now = Date()
        let startOfDay = Calendar.current.startOfDay(for: now)
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: now,
            options: .strictStartDate
        )
        
        let descriptor = HKStatisticsQueryDescriptor(
            predicate: HKSamplePredicate.quantitySample(
                type: stepType,
                predicate: predicate
            ),
            options: .cumulativeSum
        )
        
        let result = try await descriptor.result(for: healthStore)
        
        guard let quantity = result?.sumQuantity() else {
            return 0
        }
        
        return quantity.doubleValue(for: HKUnit.count())
    }
}
```

### 3. Escritura de datos — Registrar peso corporal

```swift
extension HealthKitManager {
    
    /// Guarda una medición de peso en HealthKit
    func saveBodyMass(kilograms: Double, date: Date = Date()) async throws {
        let quantityType = HKQuantityType(.bodyMass)
        let quantity = HKQuantity(unit: .gramUnit(with: .kilo), doubleValue: kilograms)
        
        let sample = HKQuantitySample(
            type: quantityType,
            quantity: quantity,
            start: date,
            end: date
        )
        
        try await healthStore.save(sample)
    }
}
```

### 4. Lectura de frecuencia cardíaca con observación en tiempo real

```swift
extension HealthKitManager {
    
    /// Observa cambios en la frecuencia cardíaca en tiempo real
    func observeHeartRate(
        updateHandler: @escaping (Double) -> Void
    ) -> HKObserverQuery {
        let heartRateType = HKQuantityType(.heartRate)
        
        let query = HKObserverQuery(
            sampleType: heartRateType,
            predicate: nil
        ) { [weak self] _, completionHandler, error in
            guard error == nil else {
                completionHandler()
                return
            }
            
            Task {
                if let latestHeartRate = try? await self?.fetchLatestHeartRate() {
                    updateHandler(latestHeartRate)
                }
                completionHandler()
            }
        }
        
        healthStore.execute(query)
        return query
    }
    
    /// Obtiene la medición más reciente de frecuencia cardíaca
    private func fetchLatestHeartRate() async throws -> Double {
        let heartRateType = HKQuantityType(.heartRate)
        let sortDescriptor = SortDescriptor(\HKQuantitySample.startDate, order: .reverse)
        
        let descriptor = HKSampleQueryDescriptor(
            predicates: [.quantitySample(type: heartRateType)],
            sortDescriptors: [sortDescriptor],
            limit: 1
        )
        
        let results = try await descriptor.result(for: healthStore)
        
        guard let sample = results.first else {
            throw HealthKitError.noDataAvailable
        }
        
        let heartRateUnit = HKUnit.count().unitDivided(by: .minute())
        return sample.quantity.doubleValue(for: heartRateUnit)
    }
}

enum HealthKitError: LocalizedError {
    case noDataAvailable
    case authorizationDenied
    case deviceNotSupported
    
    var errorDescription: String? {
        switch self {
        case .noDataAvailable:
            return "No hay datos de salud disponibles"
        case .authorizationDenied:
            return "Permisos de salud denegados por el usuario"
        case .deviceNotSupported:
            return "Este dispositivo no soporta HealthKit"
        }
    }
}
```

## Integración con SwiftUI — Dashboard de Salud

```swift
import SwiftUI
import HealthKit

struct HealthDashboardView: View {
    
    @StateObject private var viewModel = HealthDashboardViewModel()
    
    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(
                    columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ],
                    spacing: 16
                ) {
                    HealthMetricCard(
                        title: "Pasos",
                        value: viewModel.formattedSteps,
                        icon: "figure.walk",
                        color: .green
                    )
                    
                    HealthMetricCard(
                        title: "Frecuencia Cardíaca",
                        value: viewModel.formattedHeartRate,
                        icon: "heart.fill",
                        color: .red
                    )
                    
                    HealthMetricCard(
                        title: "Peso",
                        value: viewModel.formattedWeight,
                        icon: "scalemass",
                        color: .blue
                    )
                    
                    HealthMetricCard(
                        title: "Sueño",
                        value: viewModel.formattedSleep,
                        icon: "moon.fill",
                        color: .purple
                    )
                }
                .padding()
            }
            .navigationTitle("Mi Salud")
            .task {
                await viewModel.loadHealthData()
            }
            .refreshable {
                await viewModel.loadHealthData()
            }
        }
    }
}

struct HealthMetricCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundStyle(color)
                
                Spacer()
            }
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundStyle(.primary)
            
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(color.opacity(0.1))
        )
    }
}
```

### ViewModel del Dashboard

```swift
import Foundation
import HealthKit

@MainActor
class HealthDashboardViewModel: ObservableObject {
    
    @Published var steps: Double = 0
    @Published var heartRate: Double = 0
    @Published var weight: Double = 0
    @Published var sleepHours: Double = 0
    @Published var isAuthorized = false
    @Published var errorMessage: String?
    
    private let healthManager = HealthKitManager()
    
    var formattedSteps: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.locale = Locale(identifier: "es_MX")
        return formatter.string(from: NSNumber(value: steps)) ?? "0"
    }
    
    var formattedHeartRate: String {
        return heartRate > 0 ? "\(Int(heartRate)) bpm" : "-- bpm"
    }
    
    var formattedWeight: String {
        return weight > 0 ? String(format: "%.1f kg", weight) : "-- kg"
    }
    
    var formattedSleep: String {
        return sleepHours > 0 ? String(format: "%.1f hrs", sleepHours) : "-- hrs"
    }
    
    func loadHealthData() async {
        guard healthManager.isHealthDataAvailable() else {
            errorMessage = "HealthKit no está disponible en este dispositivo"
            return
        }
        
        do {
            try await healthManager.requestAuthorization()
            isAuthorized = true
            
            // Cargar datos en paralelo
            async let stepsResult = healthManager.fetchTodayStepCount()
            async let heartRateResult = fetchHeartRateSafely()
            
            steps = try await stepsResult
            heartRate = await heartRateResult
            
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    private func fetchHeartRateSafely() async -> Double {
        do {
            return try await healthManager.fetchLatestHeartRate()
        } catch {
            return 0
        }
    }
}
```

## CareKit — Planes de cuidado médico

CareKit permite crear apps de seguimiento de tratamientos y planes de cuidado del paciente.

```swift
import CareKit
import CareKitStore

class CareKitManager {
    
    let store = OCKStore(
        name: "MiAppSaludStore",
        type: .onDisk
    )
    
    /// Crear una tarea de medicación
    func createMedicationTask() async throws {
        // Definir el horario: cada 8 horas
        let schedule = OCKSchedule(
            composing: [
                OCKScheduleElement(
                    start: Calendar.current.startOfDay(for: Date()),
                    end: nil,
                    interval: DateComponents(hour: 8)
                )
            ]
        )
        
        var task = OCKTask(
            id: "metformina_500mg",
            title: "Metformina 500mg",
            carePlanUUID: nil,
            schedule: schedule
        )
        
        task.instructions = "Tomar con alimentos. No saltar dosis."
        task.impactsAdherence = true
        
        try await store.addTask(task)
    }
    
    /// Registrar que el paciente tomó su medicamento
    func markTaskCompleted(taskID: String, occurenceIndex: Int) async throws {
        var query = OCKTaskQuery(for: Date())
        query.ids = [taskID]
        
        let tasks = try await store.fetchTasks(query: query)
        
        guard let task = tasks.first else {
            throw CareKitError.taskNotFound
        }
        
        let event = try await store.fetchEvent(
            forTask: task,
            occurrence: occurenceIndex
        )
        
        var outcome = OCKOutcome(
            taskUUID: task.uuid,
            taskOccurrenceIndex: occurenceIndex,
            values: [
                OCKOutcomeValue(true, units: "completado")
            ]
        )
        
        try await store.addOutcome(outcome)
    }
}

enum CareKitError: Error {
    case taskNotFound
}
```

## Telemedicina — Integración con videollamadas

Un componente esencial de HealthTech en LATAM es la telemedicina. Aquí un ejemplo de arquitectura para una consulta virtual:

```swift
import Foundation

// MARK: - Modelos de dominio
struct Appointment: Identifiable, Codable {
    let id: UUID
    let patientID: String
    let doctorID: String
    let scheduledDate: Date
    let specialty: MedicalSpecialty
    var status: AppointmentStatus
    var videoRoomID: String?
    var notes: String?
    
    enum AppointmentStatus: String, Codable {
        case scheduled = "programada"
        case inProgress = "en_curso"
        case completed = "completada"
        case cancelled = "cancelada"
    }
}

enum MedicalSpecialty: String, Codable, CaseIterable {
    case generalMedicine = "Medicina General"
    case cardiology = "Cardiología"
    case dermatology = "Dermatología"
    case endocrinology = "Endocrinología"
    case pediatrics = "Pediatría"
    case psychiatry = "Psiquiat