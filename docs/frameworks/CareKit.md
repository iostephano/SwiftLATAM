---
sidebar_position: 1
title: CareKit
---

# CareKit

## ¿Qué es CareKit?

CareKit es un framework open-source desarrollado por Apple que permite a los desarrolladores crear aplicaciones de salud centradas en el **cuidado y seguimiento del paciente**. Proporciona una arquitectura modular compuesta por vistas preconstruidas, un almacén de datos persistente y herramientas para gestionar planes de cuidado, tareas médicas y el seguimiento de resultados clínicos. CareKit se diseñó con la filosofía de que las aplicaciones de salud deben ser fáciles de construir, mantener y personalizar.

A diferencia de HealthKit, que se enfoca en la recopilación de datos biométricos del dispositivo, CareKit se centra en la **experiencia del plan de cuidado**: definir tareas que el paciente debe realizar (tomar medicamentos, hacer ejercicios, registrar síntomas), presentarlas en una interfaz clara y almacenar el progreso. Esto lo convierte en la base ideal para aplicaciones de gestión de enfermedades crónicas, rehabilitación postoperatoria, salud mental y bienestar general.

CareKit se compone de tres módulos principales: **CareKitStore** (capa de persistencia y modelos de datos), **CareKitUI** (componentes visuales reutilizables) y **CareKit** propiamente dicho (la capa que conecta la lógica de datos con las vistas). Esta separación modular permite utilizar solo las partes que se necesiten: por ejemplo, usar únicamente CareKitUI para obtener tarjetas de interfaz bonitas sin adoptar el almacén de datos completo.

## Casos de uso principales

- **Gestión de medicamentos**: Crear planes con horarios de tomas, dosis y recordatorios. El paciente puede marcar cada toma como completada y el médico revisar la adherencia al tratamiento.

- **Rehabilitación física y postoperatoria**: Definir rutinas de ejercicios diarios con instrucciones paso a paso, permitiendo al paciente registrar el cumplimiento y niveles de dolor después de cada sesión.

- **Seguimiento de enfermedades crónicas**: Pacientes con diabetes, hipertensión o asma pueden registrar síntomas, mediciones y cumplimiento de tratamientos de forma estructurada a lo largo del tiempo.

- **Salud mental y bienestar**: Aplicaciones que guían al usuario en prácticas de mindfulness, registro de estado de ánimo diario, ejercicios de terapia cognitivo-conductual y seguimiento de hábitos saludables.

- **Monitorización remota de pacientes**: Combinado con HealthKit y conectividad con servidores remotos, permite que profesionales de salud supervisen el progreso de sus pacientes a distancia.

- **Ensayos clínicos y estudios de investigación**: Junto con ResearchKit, facilita la recopilación estructurada de datos de participantes en estudios médicos, con tareas programadas y cuestionarios periódicos.

## Instalación y configuración

### Mediante Swift Package Manager (recomendado)

En Xcode, ve a **File → Add Package Dependencies** y añade la URL del repositorio oficial:

```
https://github.com/carekit-apple/CareKit.git
```

Selecciona la versión deseada (se recomienda la última estable, actualmente 2.1+). Puedes elegir qué módulos incluir:

| Módulo | Descripción |
|---|---|
| `CareKit` | Framework completo (vistas + store + sincronización) |
| `CareKitUI` | Solo componentes visuales |
| `CareKitStore` | Solo capa de datos y modelos |

### Mediante CocoaPods

```ruby
# Podfile
platform :ios, '15.0'

target 'MiAppSalud' do
  use_frameworks!
  
  pod 'CareKit', '~> 2.1'
  # O individualmente:
  # pod 'CareKitUI', '~> 2.1'
  # pod 'CareKitStore', '~> 2.1'
end
```

### Imports necesarios

```swift
import CareKit        // Framework completo
import CareKitStore   // Modelos y almacén de datos
import CareKitUI      // Componentes de interfaz
```

### Permisos en Info.plist

CareKit por sí solo **no requiere permisos especiales** en `Info.plist`. Sin embargo, si se integra con HealthKit para leer datos de salud, se deben añadir:

```xml
<key>NSHealthShareUsageDescription</key>
<string>Necesitamos acceder a tus datos de salud para personalizar tu plan de cuidado.</string>
<key>NSHealthUpdateUsageDescription</key>
<string>Registraremos datos de salud relacionados con tu tratamiento.</string>
```

También es necesario habilitar la capability **HealthKit** en el target del proyecto si se desea esta integración.

## Conceptos clave

### 1. OCKStore (Almacén de datos)

Es el corazón de la persistencia en CareKit. `OCKStore` es una base de datos local basada en Core Data que almacena pacientes, planes de cuidado, tareas y resultados. Implementa el protocolo `OCKStoreProtocol`, lo que permite reemplazarlo por implementaciones personalizadas o agregar sincronización remota.

### 2. OCKTask (Tarea)

Representa una actividad que el paciente debe realizar. Cada tarea tiene un identificador único, título, instrucciones y un **schedule** (programación) que define cuándo y con qué frecuencia debe completarse. Ejemplos: "Tomar ibuprofeno cada 8 horas", "Caminar 30 minutos al día".

### 3. OCKSchedule (Programación)

Define la cadencia temporal de una tarea. CareKit ofrece constructores convenientes para programaciones diarias, semanales o completamente personalizadas. Cada ocurrencia del schedule genera un **evento** que el paciente puede completar.

### 4. OCKOutcome (Resultado)

Registra que un evento específico fue completado. Contiene valores opcionales (`OCKOutcomeValue`) que pueden almacenar datos numéricos, textuales o booleanos asociados al cumplimiento: por ejemplo, el nivel de dolor reportado o la presión arterial medida.

### 5. OCKContact (Contacto)

Representa a un profesional de salud o persona de apoyo vinculada al plan de cuidado. Incluye información de contacto, rol y métodos de comunicación disponibles (teléfono, email, mensajes).

### 6. Vistas sincronizadas (Synchronized View Controllers)

CareKit proporciona controladores de vista que se **sincronizan automáticamente** con el store. Cuando los datos cambian, la interfaz se actualiza en tiempo real sin código adicional. Estas vistas incluyen tarjetas de tareas, gráficos de progreso y listas de contactos.

## Ejemplo básico

```swift
import CareKit
import CareKitStore
import UIKit

/// Ejemplo básico: Crear un store, añadir una tarea y mostrarla
class BasicCareViewController: UIViewController {
    
    // 1. Crear el almacén persistente de CareKit
    let store = OCKStore(
        name: "MiStoreSalud",
        type: .onDisk  // Persiste en disco; usar .inMemory para pruebas
    )
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        
        // 2. Poblar el store con una tarea de ejemplo
        poblarTareasIniciales()
    }
    
    func poblarTareasIniciales() {
        // Definir una programación: 3 veces al día (8:00, 14:00, 20:00)
        let manana = OCKScheduleElement(
            start: Calendar.current.startOfDay(for: Date()),
            end: nil,
            interval: DateComponents(day: 1),
            text: "Mañana",
            targetValues: [],
            duration: .allDay
        )
        
        // Programación simplificada: una vez al día, todos los días
        let scheduleDiario = OCKSchedule.dailyAtTime(
            hour: 8,
            minutes: 0,
            start: Date(),
            end: nil,
            text: "Tomar con el desayuno"
        )
        
        // Crear la tarea
        var tarea = OCKTask(
            id: "ibuprofeno",           // Identificador único
            title: "Ibuprofeno 400mg",  // Título visible
            carePlanUUID: nil,          // Sin plan de cuidado asociado
            schedule: scheduleDiario
        )
        tarea.instructions = "Tomar una pastilla con agua después del desayuno."
        tarea.impactsAdherence = true   // Afecta al cálculo de adherencia
        
        // 3. Guardar la tarea en el store
        store.addTask(tarea) { [weak self] result in
            switch result {
            case .success(let tareaGuardada):
                print("✅ Tarea creada: \(tareaGuardada.title ?? "")")
                DispatchQueue.main.async {
                    self?.mostrarTarjeta()
                }
            case .failure(let error):
                print("❌ Error al crear tarea: \(error.localizedDescription)")
            }
        }
    }
    
    func mostrarTarjeta() {
        // 4. Crear una vista de tarjeta sincronizada con el store
        let tarjetaTarea = OCKSimpleTaskViewController(
            taskID: "ibuprofeno",
            eventQuery: OCKEventQuery(for: Date()),
            storeManager: OCKSynchronizedStoreManager(wrapping: store)
        )
        
        // 5. Añadir como hijo al controlador actual
        addChild(tarjetaTarea)
        view.addSubview(tarjetaTarea.view)
        tarjetaTarea.view.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            tarjetaTarea.view.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            tarjetaTarea.view.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            tarjetaTarea.view.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16)
        ])
        
        tarjetaTarea.didMove(toParent: self)
    }
}
```

## Ejemplo intermedio

```swift
import CareKit
import CareKitStore
import UIKit

/// Ejemplo intermedio: Plan de cuidado completo con múltiples tareas y contactos
class PlanCuidadoViewController: OCKDailyPageViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Mi Plan de Cuidado"
        
        // Poblar datos al inicio (normalmente se haría una sola vez)
        Task {
            await configurarPlanDeCuidado()
        }
    }
    
    // MARK: - Configuración del plan de cuidado
    
    private func configurarPlanDeCuidado() async {
        let store = self.store
        
        // Verificar si las tareas ya existen para no duplicar
        do {
            let tareasExistentes = try await store.fetchTasks(
                query: OCKTaskQuery(for: Date())
            )
            guard tareasExistentes.isEmpty else { return }
        } catch {
            print("Error consultando tareas: \(error)")
        }
        
        // --- TAREA 1: Medicamento ---
        let scheduleMedicamento = OCKSchedule(
            composing: [
                OCKScheduleElement(
                    start: horaHoy(8, 0),
                    end: nil,
                    interval: DateComponents(day: 1),
                    text: "Mañana"
                ),
                OCKScheduleElement(
                    start: horaHoy(20, 0),
                    end: nil,
                    interval: DateComponents(day: 1),
                    text: "Noche"
                )
            ]
        )
        
        var medicamento = OCKTask(
            id: "metformina",
            title: "Metformina 850mg",
            carePlanUUID: nil,
            schedule: scheduleMedicamento
        )
        medicamento.instructions = "Tomar con las comidas principales."
        medicamento.asset = "pills.fill" // Ícono SF Symbols
        
        // --- TAREA 2: Ejercicio ---
        let scheduleEjercicio = OCKSchedule.weeklyAtTime(
            weekday: 1, // Lunes
            hours: 7,
            minutes: 0,
            start: Date(),
            end: nil,
            targetValues: [
                OCKOutcomeValue(30, units: "minutos")
            ],
            text: "Sesión de caminata"
        )
        
        // Para que sea lunes, miércoles y viernes:
        let diasEjercicio = [2, 4, 6].map { dia in // Lun, Mié, Vie
            OCKScheduleElement(
                start: horaHoy(7, 0),
                end: nil,
                interval: DateComponents(weekOfYear: 1),
                text: "Caminata de 30 min",
                targetValues: [OCKOutcomeValue(30, units: "minutos")]
            )
        }
        
        let scheduleEjercicioCompleto = OCKSchedule.dailyAtTime(
            hour: 7, minutes: 0,
            start: Date(), end: nil,
            text: "Caminar 30 minutos"
        )
        
        var ejercicio = OCKTask(
            id: "caminata_diaria",
            title: "Caminata diaria",
            carePlanUUID: nil,
            schedule: scheduleEjercicioCompleto
        )
        ejercicio.instructions = "Caminar a paso moderado durante 30 minutos."
        ejercicio.asset = "figure.walk"
        
        // --- TAREA 3: Registro de síntomas (no afecta adherencia) ---
        let scheduleRegistro = OCKSchedule.dailyAtTime(
            hour: 21, minutes: 0,
            start: Date(), end: nil,
            text: "Registro nocturno"
        )
        
        var registroSintomas = OCKTask(
            id: "registro_dolor",
            title: "Nivel de dolor",
            carePlanUUID: nil,
            schedule: scheduleRegistro
        )
        registroSintomas.instructions = "Registra tu nivel de dolor del 1 al 10."
        registroSintomas.impactsAdherence = false // No afecta adherencia
        registroSintomas.asset = "heart.text.square"
        
        // --- CONTACTO ---
        var doctor = OCKContact(
            id: "dr_garcia",
            givenName: "María",
            familyName: "García",
            carePlanUUID: nil
        )
        doctor.title = "Endocrinóloga"
        doctor.role = "Médica tratante"
        doctor.emailAddresses = [OCKLabeledValue(
            label: CNLabelWork,
            value: "dra.garcia@clinica.com"
        )]
        doctor.phoneNumbers = [OCKLabeledValue(
            label: CNLabelWork,
            value: "+34 612 345 678"
        )]
        doctor.asset = "stethoscope"
        
        //