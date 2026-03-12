---
sidebar_position: 1
title: Watchos
---

# watchOS — Desarrollo para Apple Watch

## ¿Qué es watchOS?

watchOS es el sistema operativo que impulsa el Apple Watch. Desde su lanzamiento en 2015, ha evolucionado de ser una simple extensión del iPhone a convertirse en una **plataforma independiente** capaz de ejecutar aplicaciones nativas, conectarse a redes Wi-Fi y celulares, y gestionar datos de salud en tiempo real.

Para un desarrollador iOS, dominar watchOS significa ampliar tu alcance a la muñeca del usuario, donde la **inmediatez** y la **brevedad** de la interacción son las reglas fundamentales de diseño.

## ¿Por qué es importante para un dev iOS en LATAM?

El mercado de wearables en Latinoamérica crece de forma sostenida. Países como México, Brasil, Colombia y Argentina reportan un incremento anual en la adopción de Apple Watch, impulsado principalmente por:

- **Aplicaciones de salud y fitness**: La pandemia aceleró la demanda de monitoreo de salud personal. Clínicas, aseguradoras y startups de healthtech buscan desarrolladores que integren HealthKit y datos de sensores.
- **Banca móvil y fintech**: Empresas como Nubank, Mercado Pago y bancos tradicionales exploran notificaciones transaccionales y autenticación desde el reloj.
- **Diferenciación profesional**: Pocos desarrolladores en la región dominan watchOS. Esto representa una ventaja competitiva enorme al aplicar a posiciones remotas o freelance para empresas internacionales.
- **Aplicaciones empresariales**: Logística, manufactura y retail usan apps de reloj para notificaciones operativas en tiempo real.

## Arquitectura de una App para watchOS

Desde watchOS 7+, las aplicaciones pueden ser **completamente independientes** del iPhone. La arquitectura moderna se basa en **SwiftUI**, que es el framework principal y recomendado por Apple para el desarrollo en el reloj.

```
📦 MiProyecto
├── 📂 MiApp (iOS)
│   └── ContentView.swift
├── 📂 MiApp Watch App (watchOS)
│   ├── MiAppApp.swift          ← Entry point
│   ├── ContentView.swift       ← Vista principal
│   ├── NotificationView.swift
│   └── Assets.xcassets
└── 📂 Shared
    └── Models.swift            ← Código compartido
```

### Creación del proyecto

En Xcode 15+, al crear un nuevo proyecto puedes seleccionar directamente **watchOS App** o añadir un target de watchOS a un proyecto iOS existente.

## Ejemplo práctico: App de monitoreo de frecuencia cardíaca

Vamos a construir una aplicación funcional que lea la frecuencia cardíaca en tiempo real usando **HealthKit**.

### Paso 1: Configurar permisos

En el archivo `Info.plist` del target de watchOS, agrega:

```xml
<key>NSHealthShareUsageDescription</key>
<string>Necesitamos acceso a tus datos de salud para mostrar tu frecuencia cardíaca.</string>
<key>NSHealthUpdateUsageDescription</key>
<string>Necesitamos permisos para registrar datos de entrenamiento.</string>
```

### Paso 2: Crear el modelo de datos de salud

```swift
import Foundation
import HealthKit
import Combine

class HeartRateManager: NSObject, ObservableObject {
    
    private let healthStore = HKHealthStore()
    private var heartRateQuery: HKAnchoredObjectQuery?
    
    @Published var currentHeartRate: Double = 0.0
    @Published var isAuthorized: Bool = false
    
    // Tipo de dato que vamos a leer
    private let heartRateType = HKQuantityType.quantityType(
        forIdentifier: .heartRate
    )!
    
    // MARK: - Solicitar autorización
    func requestAuthorization() {
        let typesToRead: Set<HKObjectType> = [heartRateType]
        
        guard HKHealthStore.isHealthDataAvailable() else {
            print("HealthKit no está disponible en este dispositivo")
            return
        }
        
        healthStore.requestAuthorization(
            toShare: nil,
            read: typesToRead
        ) { [weak self] success, error in
            DispatchQueue.main.async {
                self?.isAuthorized = success
                if success {
                    self?.startHeartRateQuery()
                }
            }
            
            if let error = error {
                print("Error de autorización: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Consulta en tiempo real
    func startHeartRateQuery() {
        let datePredicate = HKQuery.predicateForSamples(
            withStart: Date().addingTimeInterval(-3600), // Última hora
            end: nil,
            options: .strictStartDate
        )
        
        let query = HKAnchoredObjectQuery(
            type: heartRateType,
            predicate: datePredicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { [weak self] _, samples, _, _, error in
            self?.processHeartRateSamples(samples)
        }
        
        // Handler para actualizaciones en tiempo real
        query.updateHandler = { [weak self] _, samples, _, _, error in
            self?.processHeartRateSamples(samples)
        }
        
        heartRateQuery = query
        healthStore.execute(query)
    }
    
    // MARK: - Procesar muestras
    private func processHeartRateSamples(_ samples: [HKSample]?) {
        guard let heartRateSamples = samples as? [HKQuantitySample],
              let mostRecent = heartRateSamples.last else {
            return
        }
        
        let heartRateUnit = HKUnit.count().unitDivided(by: .minute())
        let value = mostRecent.quantity.doubleValue(for: heartRateUnit)
        
        DispatchQueue.main.async {
            self.currentHeartRate = value
        }
    }
    
    // MARK: - Detener consulta
    func stopHeartRateQuery() {
        if let query = heartRateQuery {
            healthStore.stop(query)
            heartRateQuery = nil
        }
    }
    
    deinit {
        stopHeartRateQuery()
    }
}
```

### Paso 3: Construir la interfaz con SwiftUI

```swift
import SwiftUI

struct HeartRateView: View {
    
    @StateObject private var heartRateManager = HeartRateManager()
    @State private var isAnimating = false
    
    var body: some View {
        VStack(spacing: 12) {
            // Ícono animado del corazón
            Image(systemName: "heart.fill")
                .font(.system(size: 50))
                .foregroundColor(.red)
                .scaleEffect(isAnimating ? 1.2 : 1.0)
                .animation(
                    .easeInOut(duration: 0.5)
                    .repeatForever(autoreverses: true),
                    value: isAnimating
                )
            
            if heartRateManager.isAuthorized {
                // Valor de frecuencia cardíaca
                Text("\(Int(heartRateManager.currentHeartRate))")
                    .font(.system(size: 48, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                
                Text("BPM")
                    .font(.caption)
                    .foregroundColor(.gray)
                
                // Indicador de estado
                HStack {
                    Circle()
                        .fill(heartRateStatusColor)
                        .frame(width: 8, height: 8)
                    Text(heartRateStatusText)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            } else {
                Button("Permitir acceso") {
                    heartRateManager.requestAuthorization()
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
            }
        }
        .onAppear {
            isAnimating = true
            heartRateManager.requestAuthorization()
        }
        .onDisappear {
            heartRateManager.stopHeartRateQuery()
        }
    }
    
    // MARK: - Helpers de estado
    private var heartRateStatusColor: Color {
        let bpm = heartRateManager.currentHeartRate
        switch bpm {
        case 0:
            return .gray
        case 1..<60:
            return .blue
        case 60..<100:
            return .green
        case 100..<140:
            return .yellow
        default:
            return .red
        }
    }
    
    private var heartRateStatusText: String {
        let bpm = heartRateManager.currentHeartRate
        switch bpm {
        case 0:
            return "Sin datos"
        case 1..<60:
            return "En reposo"
        case 60..<100:
            return "Normal"
        case 100..<140:
            return "Elevado"
        default:
            return "Intenso"
        }
    }
}
```

### Paso 4: Entry point de la app

```swift
import SwiftUI

@main
struct HeartRateWatchApp: App {
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                HeartRateView()
                    .navigationTitle("Mi Ritmo")
            }
        }
    }
}
```

## Complicaciones: Tu app en la carátula del reloj

Las **complicaciones** (Complications) son widgets que aparecen directamente en la carátula del Apple Watch. Son el punto de entrada más poderoso porque el usuario ve tu información **sin abrir la app**.

```swift
import WidgetKit
import SwiftUI

struct HeartRateComplication: Widget {
    let kind: String = "HeartRateComplication"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: kind,
            provider: HeartRateTimelineProvider()
        ) { entry in
            HeartRateComplicationView(entry: entry)
        }
        .configurationDisplayName("Frecuencia Cardíaca")
        .description("Muestra tu último registro de BPM")
        .supportedFamilies([
            .accessoryCircular,
            .accessoryCorner,
            .accessoryInline,
            .accessoryRectangular
        ])
    }
}

struct HeartRateEntry: TimelineEntry {
    let date: Date
    let heartRate: Int
}

struct HeartRateTimelineProvider: TimelineProvider {
    func placeholder(in context: Context) -> HeartRateEntry {
        HeartRateEntry(date: .now, heartRate: 72)
    }
    
    func getSnapshot(in context: Context, completion: @escaping (HeartRateEntry) -> Void) {
        completion(HeartRateEntry(date: .now, heartRate: 72))
    }
    
    func getTimeline(in context: Context, completion: @escaping (Timeline<HeartRateEntry>) -> Void) {
        let entry = HeartRateEntry(date: .now, heartRate: 75)
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 15, to: .now)!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }
}

struct HeartRateComplicationView: View {
    var entry: HeartRateEntry
    
    var body: some View {
        ZStack {
            AccessoryWidgetBackground()
            VStack(spacing: 2) {
                Image(systemName: "heart.fill")
                    .foregroundColor(.red)
                    .font(.caption)
                Text("\(entry.heartRate)")
                    .font(.system(.title3, design: .rounded))
                    .fontWeight(.bold)
            }
        }
    }
}
```

## Comunicación Watch ↔ iPhone con WatchConnectivity

Cuando tu app necesita sincronizar datos entre el reloj y el teléfono, usas **WatchConnectivity**:

```swift
import WatchConnectivity

class WatchConnectivityManager: NSObject, ObservableObject, WCSessionDelegate {
    
    static let shared = WatchConnectivityManager()
    
    @Published var receivedMessage: String = ""
    
    private override init() {
        super.init()
        if WCSession.isSupported() {
            let session = WCSession.default
            session.delegate = self
            session.activate()
        }
    }
    
    // MARK: - Enviar mensaje al iPhone/Watch
    func sendMessage(_ message: [String: Any]) {
        guard WCSession.default.isReachable else {
            // Si no está accesible, usar transferUserInfo para envío en background
            WCSession.default.transferUserInfo(message)
            return
        }
        
        WCSession.default.sendMessage(message, replyHandler: { reply in
            print("Respuesta recibida: \(reply)")
        }, errorHandler: { error in
            print("Error al enviar: \(error.localizedDescription)")
        })
    }
    
    // MARK: - Enviar datos de contexto (persisten hasta el próximo envío)
    func updateApplicationContext(_ context: [String: Any]) {
        do {
            try WCSession.default.updateApplicationContext(context)
        } catch {
            print("Error actualizando contexto: \(error.localizedDescription)")
        }
    }
    
    // MARK: - WCSessionDelegate
    func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        print("Sesión activada con estado: \(activationState.rawValue)")
    }
    
    func session(
        _ session: WCSession,
        didReceiveMessage message: [String: Any]
    ) {
        DispatchQueue.main.async {
            if let text = message["texto"] as? String {
                self.receivedMessage = text
            }
        }
    }
    
    // Solo necesario en el lado iOS
    #if os(iOS)
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }
    #endif
}
```

## Patrones de diseño específicos para watchOS

### 1. Navegación jerárquica vs. basada en páginas

```swift
// Navegación jerárquica (push/pop) — la más común
struct MainMenuView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Frecuencia Cardíaca") {
                    HeartRateView()
                }
                NavigationLink("Historial") {
                    HistoryView()
                }
                NavigationLink("Configuración") {
                    SettingsView()
                }
            }
            .navigationTitle("Mi Salud")
        }
    }
}

// Navegación basada en pestañas (TabView con páginas)
struct PageBasedView: View {
    var body: some View {
        TabView {
            HeartRateView()
                .tag(0)
            ActivityView()
                .tag(1)
            SettingsView()
                .tag(2)
        }
        .tabViewStyle(.verticalPage) // watchOS 10+
    }
}
```

### 2. Manejo de la Digital Crown

```swift
struct CrownInputView: View {
    @State private