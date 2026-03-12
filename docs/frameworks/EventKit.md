---
sidebar_position: 1
title: EventKit
---

# EventKit

## ¿Qué es EventKit?

EventKit es el framework de Apple que proporciona acceso programático a los datos de **calendario** y **recordatorios** del usuario en dispositivos iOS, macOS, watchOS y visionOS. A través de su API, los desarrolladores pueden crear, leer, modificar y eliminar eventos del calendario, así como recordatorios, sin necesidad de abandonar la aplicación. EventKit actúa como puente entre tu aplicación y las bases de datos de Calendar y Reminders del sistema operativo.

Este framework trabaja directamente con el almacén de eventos del sistema (`EKEventStore`), que centraliza el acceso a todas las cuentas de calendario configuradas por el usuario (iCloud, Google, Exchange, CalDAV, etc.). Esto significa que cualquier cambio realizado mediante EventKit se refleja automáticamente en la app nativa de Calendario o Recordatorios, y viceversa. La sincronización es transparente y bidireccional.

EventKit es especialmente relevante cuando tu aplicación necesita integrar funcionalidades de planificación, gestión de citas, seguimiento de tareas o cualquier tipo de programación temporal. Desde apps médicas que agendan consultas hasta aplicaciones de productividad que sincronizan tareas, EventKit ofrece una solución robusta, nativa y respetuosa con la privacidad del usuario, ya que requiere autorización explícita para acceder a los datos.

## Casos de uso principales

- **Gestión de citas y reservas**: Aplicaciones de salud, belleza o servicios profesionales que permiten al usuario agendar citas directamente en su calendario del dispositivo, incluyendo alertas y recurrencias.

- **Aplicaciones de productividad y tareas**: Apps estilo "to-do" que crean recordatorios con fechas de vencimiento, prioridades y alarmas, sincronizados con la app Recordatorios nativa del sistema.

- **Planificadores de viaje**: Aplicaciones que crean eventos con ubicación, zona horaria, notas detalladas y múltiples alarmas para itinerarios de vuelos, hoteles y actividades turísticas.

- **Apps educativas y académicas**: Plataformas de e-learning que programan clases, exámenes y entregas de trabajos como eventos del calendario, permitiendo al estudiante tener todo centralizado.

- **Redes sociales y eventos comunitarios**: Apps que permiten a los usuarios agregar eventos sociales (meetups, conferencias, conciertos) a su calendario personal con un solo toque.

- **Seguimiento de hábitos y salud**: Aplicaciones que crean recordatorios recurrentes para medicamentos, rutinas de ejercicio o hábitos diarios, aprovechando el sistema de notificaciones nativo.

## Instalación y configuración

### Agregar el framework al proyecto

EventKit está incluido de forma nativa en el SDK de iOS, por lo que **no requiere dependencias externas** ni gestores de paquetes. Simplemente importa el módulo donde lo necesites:

```swift
import EventKit
// Para la interfaz visual predefinida (opcional):
import EventKitUI
```

### Configurar permisos en Info.plist

EventKit requiere permisos explícitos del usuario. Debes agregar las claves correspondientes en tu archivo `Info.plist` según la funcionalidad que utilices:

```xml
<!-- Permiso para acceder al Calendario -->
<key>NSCalendarsUsageDescription</key>
<string>Necesitamos acceso a tu calendario para crear y gestionar tus citas.</string>

<!-- Permiso para acceder al Calendario (solo escritura, iOS 17+) -->
<key>NSCalendarsWriteOnlyAccessUsageDescription</key>
<string>Necesitamos agregar eventos a tu calendario.</string>

<!-- Permiso para acceder a Recordatorios -->
<key>NSRemindersUsageDescription</key>
<string>Necesitamos acceso a tus recordatorios para gestionar tus tareas pendientes.</string>
```

### Configuración en Xcode

1. Selecciona tu target en Xcode.
2. Ve a la pestaña **Signing & Capabilities**.
3. No se requiere una capability adicional específica, pero asegúrate de que los permisos estén declarados en `Info.plist`.

> **Nota importante (iOS 17+):** Apple introdujo permisos granulares para calendario. Ahora puedes solicitar acceso **completo** (`fullAccess`) o **solo escritura** (`writeOnly`). Planifica tu estrategia de permisos según las necesidades reales de tu app.

## Conceptos clave

### 1. EKEventStore

Es el **punto de entrada principal** al framework. Representa la conexión con la base de datos de eventos y recordatorios del sistema. Debes crear una única instancia y reutilizarla durante todo el ciclo de vida de la aplicación, ya que su inicialización es costosa.

```swift
let eventStore = EKEventStore()
```

### 2. EKEvent

Representa un **evento del calendario**. Contiene propiedades como título, fechas de inicio y fin, ubicación, notas, alarmas, reglas de recurrencia y el calendario al que pertenece. Los eventos pueden ser de todo el día o tener horarios específicos.

### 3. EKReminder

Representa un **recordatorio** (tarea). A diferencia de los eventos, los recordatorios pueden tener una fecha de vencimiento opcional, prioridad, estado de completado y listas de completado. Se obtienen mediante predicados de búsqueda específicos.

### 4. EKCalendar

Representa un **calendario individual** dentro de una cuenta. Un usuario puede tener múltiples calendarios (Trabajo, Personal, Familia, etc.) en diferentes proveedores (iCloud, Google, Local). Cada evento o recordatorio pertenece a exactamente un calendario.

### 5. EKAlarm

Representa una **alarma o notificación** asociada a un evento o recordatorio. Puede configurarse como un offset relativo (por ejemplo, 15 minutos antes) o como una fecha/hora absoluta. Un evento puede tener múltiples alarmas.

### 6. EKRecurrenceRule

Define las **reglas de recurrencia** para eventos que se repiten. Soporta frecuencias diarias, semanales, mensuales y anuales, con configuraciones complejas como "cada 2 semanas los lunes y miércoles" o "el último viernes de cada mes".

## Ejemplo básico

Este ejemplo muestra cómo solicitar permisos y crear un evento simple en el calendario del usuario:

```swift
import EventKit

class CalendarioBasico {
    
    // Instancia única del event store (reutilizar siempre)
    private let eventStore = EKEventStore()
    
    /// Solicita permisos de acceso al calendario del usuario.
    /// En iOS 17+ se usa el nuevo método con granularidad.
    func solicitarPermisos() async -> Bool {
        do {
            // iOS 17+: solicitar acceso completo al calendario
            if #available(iOS 17.0, *) {
                return try await eventStore.requestFullAccessToEvents()
            } else {
                // iOS 16 y anteriores: método clásico
                return try await eventStore.requestAccess(to: .event)
            }
        } catch {
            print("Error al solicitar permisos: \(error.localizedDescription)")
            return false
        }
    }
    
    /// Crea un evento simple en el calendario predeterminado.
    /// - Parameters:
    ///   - titulo: El título del evento
    ///   - inicio: Fecha y hora de inicio
    ///   - fin: Fecha y hora de finalización
    /// - Returns: El identificador único del evento creado
    func crearEventoSimple(titulo: String, inicio: Date, fin: Date) throws -> String {
        // Crear el objeto evento asociado al event store
        let evento = EKEvent(eventStore: eventStore)
        
        // Configurar propiedades básicas
        evento.title = titulo
        evento.startDate = inicio
        evento.endDate = fin
        
        // Asignar al calendario predeterminado del usuario
        evento.calendar = eventStore.defaultCalendarForNewEvents
        
        // Agregar una alarma 30 minutos antes
        let alarma = EKAlarm(relativeOffset: -30 * 60) // segundos
        evento.addAlarm(alarma)
        
        // Guardar el evento en el almacén
        // El parámetro span indica si afecta solo a este evento o a toda la serie
        try eventStore.save(evento, span: .thisEvent)
        
        print("Evento creado exitosamente con ID: \(evento.eventIdentifier ?? "sin ID")")
        return evento.eventIdentifier ?? ""
    }
}

// MARK: - Uso
/*
 let calendario = CalendarioBasico()
 
 Task {
     let autorizado = await calendario.solicitarPermisos()
     guard autorizado else {
         print("Sin permisos para acceder al calendario")
         return
     }
     
     let ahora = Date()
     let enUnaHora = ahora.addingTimeInterval(3600)
     
     do {
         let id = try calendario.crearEventoSimple(
             titulo: "Reunión de equipo",
             inicio: ahora,
             fin: enUnaHora
         )
         print("Evento creado: \(id)")
     } catch {
         print("Error al crear evento: \(error)")
     }
 }
 */
```

## Ejemplo intermedio

Este ejemplo muestra un gestor de calendario más completo con operaciones CRUD, búsqueda por rango de fechas, eventos recurrentes y gestión de recordatorios:

```swift
import EventKit

/// Gestor integral de calendario y recordatorios.
/// Encapsula las operaciones más comunes de EventKit con manejo robusto de errores.
class GestorCalendario {
    
    // MARK: - Propiedades
    
    private let eventStore = EKEventStore()
    
    /// Estado actual de autorización para eventos
    var tieneAccesoCalendario: Bool {
        let estado = EKEventStore.authorizationStatus(for: .event)
        if #available(iOS 17.0, *) {
            return estado == .fullAccess
        }
        return estado == .authorized
    }
    
    /// Estado actual de autorización para recordatorios
    var tieneAccesoRecordatorios: Bool {
        let estado = EKEventStore.authorizationStatus(for: .reminder)
        if #available(iOS 17.0, *) {
            return estado == .fullAccess
        }
        return estado == .authorized
    }
    
    // MARK: - Permisos
    
    /// Solicita permisos tanto para calendario como para recordatorios.
    /// Retorna una tupla indicando el estado de cada permiso.
    func solicitarTodosLosPermisos() async -> (calendario: Bool, recordatorios: Bool) {
        let calendario: Bool
        let recordatorios: Bool
        
        do {
            if #available(iOS 17.0, *) {
                calendario = try await eventStore.requestFullAccessToEvents()
                recordatorios = try await eventStore.requestFullAccessToReminders()
            } else {
                calendario = try await eventStore.requestAccess(to: .event)
                recordatorios = try await eventStore.requestAccess(to: .reminder)
            }
        } catch {
            print("Error en permisos: \(error.localizedDescription)")
            return (false, false)
        }
        
        return (calendario, recordatorios)
    }
    
    // MARK: - Obtener calendarios disponibles
    
    /// Retorna todos los calendarios del usuario agrupados por tipo de fuente.
    func obtenerCalendarios() -> [EKSource: [EKCalendar]] {
        let calendarios = eventStore.calendars(for: .event)
        
        // Agrupar por fuente (iCloud, Local, Google, etc.)
        var agrupados: [EKSource: [EKCalendar]] = [:]
        for calendario in calendarios {
            if let fuente = calendario.source {
                agrupados[fuente, default: []].append(calendario)
            }
        }
        
        return agrupados
    }
    
    // MARK: - Buscar eventos
    
    /// Busca eventos en un rango de fechas determinado.
    /// - Parameters:
    ///   - inicio: Fecha de inicio del rango
    ///   - fin: Fecha de fin del rango
    ///   - calendarios: Calendarios específicos donde buscar (nil = todos)
    /// - Returns: Array de eventos encontrados, ordenados por fecha
    func buscarEventos(
        desde inicio: Date,
        hasta fin: Date,
        enCalendarios calendarios: [EKCalendar]? = nil
    ) -> [EKEvent] {
        // Crear predicado de búsqueda
        let predicado = eventStore.predicateForEvents(
            withStart: inicio,
            end: fin,
            calendars: calendarios
        )
        
        // Ejecutar búsqueda y ordenar por fecha de inicio
        let eventos = eventStore.events(matching: predicado)
        return eventos.sorted { $0.startDate < $1.startDate }
    }
    
    /// Obtiene los eventos del día actual.
    func eventosDeHoy() -> [EKEvent] {
        let calendario = Calendar.current
        let inicioDelDia = calendario.startOfDay(for: Date())
        guard let finDelDia = calendario.date(
            byAdding: .day, value: 1, to: inicioDelDia
        ) else {
            return []
        }
        return buscarEventos(desde: inicioDelDia, hasta: finDelDia)
    }
    
    /// Obtiene los eventos de la semana actual.
    func eventosDeLaSemana() -> [EKEvent] {
        let calendario = Calendar.current
        let hoy = calendario.startOfDay(for: Date())
        
        // Calcular inicio de la semana (lunes)
        guard let inicioSemana = calendario.date(
            from: calendario.dateComponents([.yearForWeekOfYear, .weekOfYear], from: hoy)
        ),
        let finSemana = calendario.date(
            byAdding: .day, value: 7, to: inicioSemana
        ) else {
            return []
        }
        
        return buscarEventos(desde: inicioSemana, hasta: finSemana)
    }
    
    // MARK: - Crear evento avanzado
    
    /// Crea un evento con todas las opciones disponibles.
    /// - Parameters:
    ///   - titulo: Título del evento
    ///   - inicio: Fecha de inicio
    ///   - fin: Fecha de fin
    ///   - ubicacion: Ubicación del evento (opcional)
    ///   - notas: Notas adicionales (opcional)
    ///   - calendario: Calendario destino (nil = predeterminado)
    ///   - todoElDia: Si es un evento de todo el día
    ///   - alarmas: Offsets de alarmas en minutos antes del evento
    ///   - recurrencia: Regla de recurrencia (opcional)
    ///   - url: URL asociada al evento (opcional)
    /// - Returns: El identificador del evento creado
    @discardableResult
    func crearEvento(
        titulo: String,
        inicio: Date,
        fin: Date,
        ubicacion: String? = nil,
        notas: String? = nil,
        calendario: EKCalendar? = nil,
        todoElDia: Bool = false,
        alarmas: [TimeInterval] = [-15 * 60], // 15 min antes por defecto
        recurrencia: EKRecurrenceRule? = nil,
        url: URL? = nil
    ) throws -> String {
        let evento = EKEvent(eventStore: eventStore