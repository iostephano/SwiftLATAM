---
sidebar_position: 1
title: HealthKit
---

# HealthKit

## ¿Qué es HealthKit?

HealthKit es el framework de Apple que proporciona un repositorio centralizado y seguro para almacenar, acceder y compartir datos de salud y actividad física del usuario en dispositivos iOS y watchOS. Actúa como una base de datos unificada donde múltiples aplicaciones pueden leer y escribir información relacionada con la salud, desde pasos diarios y frecuencia cardíaca hasta registros de glucosa en sangre, patrones de sueño y datos de nutrición.

El framework fue introducido en iOS 8 y desde entonces ha evolucionado significativamente, incorporando soporte para cientos de tipos de datos de salud. HealthKit no solo almacena datos, sino que también gestiona las unidades de medida, las fuentes de datos y, de forma crítica, los permisos de acceso granulares que el usuario otorga a cada aplicación. Toda la información se cifra y se almacena localmente en el dispositivo, respetando la privacidad del usuario como pilar fundamental.

Es importante entender que HealthKit **no está disponible en iPad ni en macOS** (salvo Mac Catalyst con limitaciones). Su uso es ideal cuando tu aplicación necesita interactuar con datos de salud que el usuario ya recopila mediante el Apple Watch, iPhone u otras aplicaciones de terceros, o cuando deseas contribuir datos propios al ecosistema de salud del dispositivo.

## Casos de uso principales

- **Aplicaciones de fitness y ejercicio**: Registrar entrenamientos, calorías quemadas, distancia recorrida y frecuencia cardíaca durante actividades físicas. Permite sincronizar datos con el Apple Watch y mostrar estadísticas consolidadas.

- **Monitoreo de salud crónica**: Aplicaciones para pacientes con diabetes que registran niveles de glucosa, presión arterial o medicamentos, integrándose con dispositivos médicos certificados y compartiendo datos con profesionales de salud.

- **Seguimiento de nutrición y dieta**: Registrar ingesta calórica, macronutrientes (proteínas, carbohidratos, grasas), consumo de agua y micronutrientes. Estos datos se consolidan en la app Salud del sistema.

- **Análisis del sueño**: Leer y escribir datos de patrones de sueño, incluyendo las distintas fases (REM, sueño profundo, sueño ligero) disponibles a partir de watchOS 9 y iOS 16.

- **Aplicaciones de salud femenina**: Seguimiento del ciclo menstrual, predicción de ovulación y registro de síntomas asociados, integrándose con los datos que Apple Health ya recopila.

- **Investigación médica y estudios clínicos**: Plataformas como ResearchKit utilizan HealthKit para recopilar datos de salud de participantes en estudios de investigación de manera ética y controlada.

## Instalación y configuración

### 1. Habilitar la capacidad en Xcode

Primero, debes activar HealthKit en las capacidades de tu proyecto:

1. Selecciona tu **target** en Xcode.
2. Ve a la pestaña **Signing & Capabilities**.
3. Haz clic en **+ Capability**.
4. Busca y añade **HealthKit**.
5. Si tu app necesita datos de series clínicas, marca también **Clinical Health Records**.

Esto añadirá automáticamente el entitlement `com.apple.developer.healthkit` a tu proyecto.

### 2. Configurar Info.plist

Debes proporcionar descripciones claras de por qué tu aplicación necesita acceder a datos de salud. Estas descripciones se muestran al usuario en el diálogo de permisos:

```xml
<!-- Info.plist -->

<!-- Obligatorio si lees datos de salud -->
<key>NSHealthShareUsageDescription</key>
<string>Necesitamos leer tus datos de salud para mostrarte estadísticas personalizadas de actividad física y frecuencia cardíaca.</string>

<!-- Obligatorio si escribes datos de salud -->
<key>NSHealthUpdateUsageDescription</key>
<string>Necesitamos registrar tus entrenamientos y métricas de salud en la app Salud para que puedas tener un historial completo.</string>

<!-- Solo si accedes a registros clínicos (FHIR) -->
<key>NSHealthClinicalHealthRecordsShareUsageDescription</key>
<string>Necesitamos acceder a tus registros clínicos para ofrecerte recomendaciones personalizadas basadas en tu historial médico.</string>
```

### 3. Imports necesarios

```swift
import HealthKit
```

### 4. Verificar disponibilidad

```swift
// HealthKit NO está disponible en iPad ni en todos los dispositivos
guard HKHealthStore.isHealthDataAvailable() else {
    print("HealthKit no está disponible en este dispositivo")
    return
}
```

### 5. Consideraciones para watchOS

Si desarrollas para Apple Watch, añade la capacidad HealthKit también en el target de watchOS. En watchOS puedes acceder a datos en tiempo real como frecuencia cardíaca durante entrenamientos.

## Conceptos clave

### HKHealthStore

Es el punto de entrada principal al framework. Representa la conexión con la base de datos de HealthKit. Debes crear **una sola instancia** y reutilizarla en toda tu aplicación. A través de ella solicitas permisos, ejecutas consultas, guardas muestras y configuras observadores.

```swift
let healthStore = HKHealthStore()
```

### HKObjectType y HKSampleType

HealthKit organiza los datos en **tipos**. Cada dato de salud tiene un tipo específico identificado por un `HKObjectType`. Los más comunes son:

- **HKQuantityType**: Datos numéricos con unidad (pasos, frecuencia cardíaca, peso, calorías).
- **HKCategoryType**: Datos categóricos (calidad del sueño, estado de ánimo).
- **HKWorkoutType**: Representa entrenamientos completos.
- **HKCorrelationType**: Agrupa datos relacionados (como presión arterial sistólica y diastólica).
- **HKCharacteristicType**: Datos estáticos del usuario (fecha de nacimiento, sexo biológico, tipo de sangre).

### HKSample y HKQuantitySample

Los datos individuales en HealthKit se representan como **muestras** (`HKSample`). Cada muestra tiene una fecha de inicio, una fecha de fin, un tipo, una fuente y metadatos opcionales. Las `HKQuantitySample` añaden un valor numérico con una unidad específica.

### HKUnit

Sistema robusto de unidades de medida que permite conversiones automáticas. Soporta unidades compuestas como `count/min` para frecuencia cardíaca o `kcal` para energía.

```swift
let bpm = HKUnit.count().unitDivided(by: .minute()) // latidos por minuto
let kilocalories = HKUnit.kilocalorie()
let kilograms = HKUnit.gramUnit(with: .kilo)
```

### HKQuery

Las consultas son el mecanismo para leer datos. HealthKit ofrece varios tipos:

- **HKSampleQuery**: Obtiene muestras puntuales con filtros y ordenamiento.
- **HKStatisticsQuery**: Calcula estadísticas (suma, promedio, mín, máx).
- **HKStatisticsCollectionQuery**: Estadísticas agrupadas por intervalos de tiempo.
- **HKObserverQuery**: Notifica cambios en tiempo real.
- **HKAnchoredObjectQuery**: Obtiene datos nuevos desde la última consulta (ideal para sincronización incremental).

### Autorización granular

El usuario controla **individualmente** qué tipos de datos puede leer y escribir cada aplicación. Tu app **nunca puede saber** si el usuario denegó el permiso de lectura (por privacidad, HealthKit simplemente devuelve datos vacíos). Sí puedes saber si se denegó la escritura.

## Ejemplo básico

Este ejemplo muestra cómo solicitar permisos y leer el conteo de pasos del día actual:

```swift
import HealthKit

class PasosBasicoManager {

    // Instancia única del HealthStore
    private let healthStore = HKHealthStore()

    /// Solicita permisos para leer pasos
    func solicitarPermisos() async throws {
        // Verificar disponibilidad del dispositivo
        guard HKHealthStore.isHealthDataAvailable() else {
            throw HealthError.noDisponible
        }

        // Definir los tipos de datos que necesitamos leer
        guard let tipoPasos = HKQuantityType.quantityType(
            forIdentifier: .stepCount
        ) else {
            throw HealthError.tipoNoDisponible
        }

        // Tipos que queremos leer
        let tiposLectura: Set<HKObjectType> = [tipoPasos]

        // Solicitar autorización al usuario
        // Esto muestra el diálogo nativo de permisos
        try await healthStore.requestAuthorization(
            toShare: [],           // No escribimos nada
            read: tiposLectura     // Solo leemos pasos
        )
    }

    /// Obtiene el total de pasos del día actual
    func obtenerPasosDeHoy() async throws -> Double {
        guard let tipoPasos = HKQuantityType.quantityType(
            forIdentifier: .stepCount
        ) else {
            throw HealthError.tipoNoDisponible
        }

        // Crear predicado para filtrar solo datos de hoy
        let inicioDelDia = Calendar.current.startOfDay(for: Date())
        let predicado = HKQuery.predicateForSamples(
            withStart: inicioDelDia,
            end: Date(),
            options: .strictStartDate
        )

        // Usar HKStatisticsQuery para obtener la suma total
        return try await withCheckedThrowingContinuation { continuation in
            let consulta = HKStatisticsQuery(
                quantityType: tipoPasos,
                quantitySamplePredicate: predicado,
                options: .cumulativeSum
            ) { _, resultado, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }

                // Extraer el valor en la unidad deseada (conteo)
                let pasos = resultado?
                    .sumQuantity()?
                    .doubleValue(for: .count()) ?? 0.0

                continuation.resume(returning: pasos)
            }

            // Ejecutar la consulta
            self.healthStore.execute(consulta)
        }
    }

    // Errores personalizados
    enum HealthError: LocalizedError {
        case noDisponible
        case tipoNoDisponible

        var errorDescription: String? {
            switch self {
            case .noDisponible:
                return "HealthKit no está disponible en este dispositivo"
            case .tipoNoDisponible:
                return "El tipo de dato solicitado no está disponible"
            }
        }
    }
}

// --- Uso ---
// let manager = PasosBasicoManager()
// try await manager.solicitarPermisos()
// let pasos = try await manager.obtenerPasosDeHoy()
// print("Pasos hoy: \(Int(pasos))")
```

## Ejemplo intermedio

Este ejemplo muestra cómo registrar un entrenamiento completo con muestras de frecuencia cardíaca y consultar el historial de entrenamientos:

```swift
import HealthKit

class EntrenamientoManager {

    private let healthStore = HKHealthStore()

    // MARK: - Autorización

    /// Solicita permisos para leer y escribir datos de entrenamientos
    func solicitarPermisos() async throws {
        guard HKHealthStore.isHealthDataAvailable() else {
            throw NSError(
                domain: "HealthKit",
                code: -1,
                userInfo: [NSLocalizedDescriptionKey: "HealthKit no disponible"]
            )
        }

        // Tipos que queremos ESCRIBIR
        let tiposEscritura: Set<HKSampleType> = [
            HKWorkoutType.workoutType(),
            HKQuantityType.quantityType(forIdentifier: .heartRate)!,
            HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned)!,
            HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning)!
        ]

        // Tipos que queremos LEER
        let tiposLectura: Set<HKObjectType> = [
            HKWorkoutType.workoutType(),
            HKQuantityType.quantityType(forIdentifier: .heartRate)!,
            HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned)!,
            HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning)!
        ]

        try await healthStore.requestAuthorization(
            toShare: tiposEscritura,
            read: tiposLectura
        )
    }

    // MARK: - Guardar entrenamiento

    /// Guarda un entrenamiento de carrera con métricas asociadas
    func guardarEntrenamientoCarrera(
        inicio: Date,
        fin: Date,
        distanciaMetros: Double,
        caloriasKcal: Double,
        muestrasCardiacas: [(fecha: Date, bpm: Double)]
    ) async throws {

        // 1. Crear las muestras de frecuencia cardíaca
        let tipoCardiaco = HKQuantityType.quantityType(forIdentifier: .heartRate)!
        let unidadBPM = HKUnit.count().unitDivided(by: .minute())

        let muestrasHR: [HKQuantitySample] = muestrasCardiacas.map { muestra in
            let cantidad = HKQuantity(unit: unidadBPM, doubleValue: muestra.bpm)
            return HKQuantitySample(
                type: tipoCardiaco,
                quantity: cantidad,
                start: muestra.fecha,
                end: muestra.fecha
            )
        }

        // 2. Crear muestra de distancia
        let tipoDistancia = HKQuantityType.quantityType(
            forIdentifier: .distanceWalkingRunning
        )!
        let cantidadDistancia = HKQuantity(
            unit: .meter(),
            doubleValue: distanciaMetros
        )
        let muestraDistancia = HKQuantitySample(
            type: tipoDistancia,
            quantity: cantidadDistancia,
            start: inicio,
            end: fin
        )

        // 3. Crear muestra de calorías
        let tipoCalorias = HKQuantityType.quantityType(
            forIdentifier: .activeEnergyBurned
        )!
        let cantidadCalorias = HKQuantity(
            unit: .kilocalorie(),
            doubleValue: caloriasKcal
        )
        let muestraCalorias = HKQuantitySample(
            type: tipoCalorias,
            quantity: cantidadCalorias,
            start: inicio,
            end: fin
        )

        // 4. Construir el entrenamiento con HKWorkout
        let configuracion = HKWorkoutConfiguration()
        configuracion.activityType = .running
        configuracion.locationType = .outdoor

        let builder = HKWorkoutBuilder(
            healthStore: healthStore,
            configuration: configuracion,
            device: .local()
        )

        try await builder.beginCollection(at: inicio)

        // Añadir todas las muestras al builder
        var todasLasMuestras: [HKSample] =