---
sidebar_position: 1
title: EventKitUI
---

# EventKitUI

## ¿Qué es EventKitUI?

**EventKitUI** es un framework de Apple que proporciona controladores de vista predefinidos para mostrar, crear y editar eventos de calendario y recordatorios directamente dentro de tu aplicación iOS. Es la capa de interfaz de usuario que complementa al framework **EventKit**, el cual gestiona el acceso a los datos del calendario y recordatorios del sistema operativo.

Este framework resulta especialmente valioso porque elimina la necesidad de construir desde cero interfaces complejas para la gestión de eventos. Apple proporciona controladores nativos que respetan las convenciones de diseño del sistema, ofrecen una experiencia consistente al usuario y manejan internamente la validación de datos, zonas horarias, recurrencias y alarmas. Esto reduce drásticamente el tiempo de desarrollo y la probabilidad de errores.

EventKitUI debe utilizarse cuando tu aplicación necesita permitir al usuario interactuar con el calendario del dispositivo: ya sea para crear citas desde una app de salud, añadir eventos desde una app de conferencias, seleccionar calendarios específicos o editar recordatorios existentes. Es ideal para cualquier escenario donde la integración con el calendario nativo sea un requisito funcional sin necesidad de reinventar una interfaz completa de gestión de eventos.

## Casos de uso principales

- **Aplicaciones de reservas y citas**: Permitir al usuario guardar la fecha y hora de una cita médica, reserva de restaurante o sesión de peluquería directamente en su calendario nativo tras confirmar la reserva.

- **Apps de conferencias y eventos**: Mostrar el detalle de una charla o taller y ofrecer un botón "Añadir al calendario" que abra el editor de eventos precargado con título, ubicación, fecha y notas del evento.

- **Gestión de tareas y productividad**: Integrar la creación de recordatorios con fechas límite vinculados al sistema de Recordatorios de iOS, permitiendo que las notificaciones nativas se encarguen de alertar al usuario.

- **Aplicaciones educativas**: Programar sesiones de estudio, exámenes o entregas de trabajos como eventos recurrentes del calendario, aprovechando el soporte nativo de reglas de recurrencia.

- **Apps de fitness y salud**: Crear eventos para sesiones de entrenamiento, citas con nutricionistas o recordatorios de toma de medicamentos con alarmas personalizadas.

- **Selector de calendarios**: Permitir que el usuario elija en qué calendario específico desea guardar eventos generados por la aplicación, utilizando el controlador de selección de calendarios integrado.

## Instalación y configuración

### Agregar el framework al proyecto

EventKitUI viene incluido en el SDK de iOS, por lo que no necesitas gestores de paquetes externos. Simplemente importa ambos frameworks en los archivos donde los necesites:

```swift
import EventKit
import EventKitUI
```

Si utilizas **Xcode 15+** con un proyecto moderno, los frameworks se enlazan automáticamente. En proyectos más antiguos, verifica que `EventKit.framework` y `EventKitUI.framework` estén añadidos en **Build Phases → Link Binary With Libraries**.

### Permisos en Info.plist

Es **obligatorio** declarar las claves de privacidad correspondientes en tu archivo `Info.plist`. Sin estas claves, la app se cerrará inesperadamente al intentar acceder a los datos:

```xml
<!-- Para acceso al calendario -->
<key>NSCalendarsUsageDescription</key>
<string>Necesitamos acceder a tu calendario para crear y gestionar tus eventos.</string>

<!-- Para acceso completo al calendario (iOS 17+) -->
<key>NSCalendarsFullAccessUsageDescription</key>
<string>Necesitamos acceso completo a tu calendario para crear, editar y eliminar eventos.</string>

<!-- Para acceso a recordatorios -->
<key>NSRemindersUsageDescription</key>
<string>Necesitamos acceder a tus recordatorios para programar tareas.</string>

<!-- Para acceso completo a recordatorios (iOS 17+) -->
<key>NSRemindersFullAccessUsageDescription</key>
<string>Necesitamos acceso completo a tus recordatorios para gestionar tus tareas.</string>
```

> ⚠️ **Importante**: A partir de **iOS 17**, Apple introdujo niveles granulares de acceso al calendario (`writeOnly` y `fullAccess`). Asegúrate de solicitar únicamente el nivel de acceso que tu aplicación realmente necesita.

### Solicitud de permisos en tiempo de ejecución

```swift
import EventKit

let eventStore = EKEventStore()

// iOS 17+
if #available(iOS 17.0, *) {
    do {
        let granted = try await eventStore.requestFullAccessToEvents()
        if granted {
            print("Acceso completo al calendario concedido")
        }
    } catch {
        print("Error al solicitar acceso: \(error.localizedDescription)")
    }
} else {
    // iOS 16 y anteriores
    eventStore.requestAccess(to: .event) { granted, error in
        if granted {
            print("Acceso al calendario concedido")
        }
    }
}
```

## Conceptos clave

### 1. EKEventStore
Es el objeto central que actúa como puente entre tu aplicación y la base de datos de calendario del sistema. Debes crear **una sola instancia** y reutilizarla durante todo el ciclo de vida de la aplicación. Todas las operaciones de lectura, escritura y consulta de eventos y recordatorios pasan a través de este objeto.

### 2. EKEventEditViewController
Controlador de vista que presenta una interfaz completa para **crear o editar** un evento de calendario. Muestra campos para título, ubicación, fechas de inicio y fin, calendario destino, alarmas, notas y reglas de recurrencia. Es el componente que usarás con mayor frecuencia en EventKitUI.

### 3. EKEventViewController
Controlador de vista de **solo lectura** (con opción de edición) que muestra los detalles de un evento existente. Ideal para presentar la información completa de un evento ya guardado, con la posibilidad de permitir al usuario editarlo o eliminarlo desde la misma vista.

### 4. EKCalendarChooser
Controlador que presenta una lista de los calendarios disponibles en el dispositivo, permitiendo al usuario **seleccionar uno o varios** calendarios. Es útil cuando necesitas filtrar eventos por calendario o dejar que el usuario elija dónde guardar nuevos eventos.

### 5. Protocolos Delegate
EventKitUI se comunica con tu código a través de protocolos delegados (`EKEventEditViewDelegate`, `EKEventViewDelegate`, `EKCalendarChooserDelegate`). Implementar estos delegados es **obligatorio** para recibir notificaciones cuando el usuario completa, cancela o elimina una acción.

### 6. EKEvent y EKCalendar
`EKEvent` representa un evento individual con todas sus propiedades (título, fechas, ubicación, alarmas, recurrencia). `EKCalendar` representa un calendario específico del usuario (trabajo, personal, cumpleaños, etc.). Ambos pertenecen a EventKit pero son fundamentales para configurar los controladores de EventKitUI.

## Ejemplo básico

Este ejemplo muestra cómo presentar el editor de eventos para que el usuario cree un nuevo evento:

```swift
import UIKit
import EventKit
import EventKitUI

class BasicViewController: UIViewController {
    
    // MARK: - Propiedades
    
    /// Instancia única del store de eventos. 
    /// Debe mantenerse viva durante todo el ciclo de vida de la app.
    private let eventStore = EKEventStore()
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarBoton()
    }
    
    private func configurarBoton() {
        let boton = UIButton(type: .system)
        boton.setTitle("Crear evento", for: .normal)
        boton.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        boton.addTarget(self, action: #selector(crearEventoTapped), for: .touchUpInside)
        boton.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(boton)
        NSLayoutConstraint.activate([
            boton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            boton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    // MARK: - Acciones
    
    @objc private func crearEventoTapped() {
        solicitarAccesoYMostrarEditor()
    }
    
    private func solicitarAccesoYMostrarEditor() {
        // Solicitar acceso al calendario antes de mostrar el editor
        if #available(iOS 17.0, *) {
            Task {
                do {
                    let concedido = try await eventStore.requestFullAccessToEvents()
                    if concedido {
                        await MainActor.run { mostrarEditorDeEvento() }
                    } else {
                        await MainActor.run { mostrarAlertaPermisos() }
                    }
                } catch {
                    print("Error solicitando acceso: \(error)")
                }
            }
        } else {
            eventStore.requestAccess(to: .event) { [weak self] concedido, error in
                DispatchQueue.main.async {
                    if concedido {
                        self?.mostrarEditorDeEvento()
                    } else {
                        self?.mostrarAlertaPermisos()
                    }
                }
            }
        }
    }
    
    private func mostrarEditorDeEvento() {
        // Crear un evento nuevo precargado con datos
        let evento = EKEvent(eventStore: eventStore)
        evento.title = "Reunión de equipo"
        evento.startDate = Date().addingTimeInterval(3600) // En 1 hora
        evento.endDate = Date().addingTimeInterval(7200)   // Duración: 1 hora
        evento.notes = "Discutir los avances del sprint actual"
        
        // Configurar el controlador de edición
        let editorVC = EKEventEditViewController()
        editorVC.eventStore = eventStore
        editorVC.event = evento
        editorVC.editViewDelegate = self // Asignar el delegado
        
        // Presentar de forma modal
        present(editorVC, animated: true)
    }
    
    private func mostrarAlertaPermisos() {
        let alerta = UIAlertController(
            title: "Permiso requerido",
            message: "Necesitamos acceso al calendario para crear eventos. " +
                     "Ve a Ajustes para habilitarlo.",
            preferredStyle: .alert
        )
        alerta.addAction(UIAlertAction(title: "Aceptar", style: .default))
        present(alerta, animated: true)
    }
}

// MARK: - EKEventEditViewDelegate

extension BasicViewController: EKEventEditViewDelegate {
    
    /// Se llama cuando el usuario completa o cancela la edición
    func eventEditViewController(
        _ controller: EKEventEditViewController,
        didCompleteWith action: EKEventEditViewAction
    ) {
        switch action {
        case .saved:
            print("✅ Evento guardado exitosamente")
        case .canceled:
            print("❌ El usuario canceló la creación")
        case .deleted:
            print("🗑️ El usuario eliminó el evento")
        @unknown default:
            break
        }
        
        // IMPORTANTE: Siempre debes cerrar el controlador manualmente
        controller.dismiss(animated: true)
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra una aplicación más completa que gestiona la visualización de eventos existentes y la selección de calendarios:

```swift
import UIKit
import EventKit
import EventKitUI

/// Controlador que muestra eventos del calendario del usuario
/// y permite ver los detalles o crear nuevos eventos
class CalendarManagerViewController: UITableViewController {
    
    // MARK: - Propiedades
    
    private let eventStore = EKEventStore()
    private var eventos: [EKEvent] = []
    private var calendarioSeleccionado: EKCalendar?
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Mis Eventos"
        
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "EventoCell")
        
        configurarBarraNavegacion()
        verificarAccesoYCargarEventos()
        
        // Observar cambios en el store de eventos (cambios externos)
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(storeChanged),
            name: .EKEventStoreChanged,
            object: eventStore
        )
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Configuración
    
    private func configurarBarraNavegacion() {
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(agregarEvento)
        )
        
        navigationItem.leftBarButtonItem = UIBarButtonItem(
            title: "Calendarios",
            style: .plain,
            target: self,
            action: #selector(seleccionarCalendario)
        )
    }
    
    // MARK: - Gestión de acceso y carga de datos
    
    private func verificarAccesoYCargarEventos() {
        if #available(iOS 17.0, *) {
            Task {
                do {
                    let concedido = try await eventStore.requestFullAccessToEvents()
                    if concedido {
                        await MainActor.run { cargarEventosDelMes() }
                    }
                } catch {
                    print("Error: \(error.localizedDescription)")
                }
            }
        } else {
            let status = EKEventStore.authorizationStatus(for: .event)
            switch status {
            case .authorized:
                cargarEventosDelMes()
            case .notDetermined:
                eventStore.requestAccess(to: .event) { [weak self] ok, _ in
                    if ok {
                        DispatchQueue.main.async { self?.cargarEventosDelMes() }
                    }
                }
            default:
                mostrarAlertaPermisos()
            }
        }
    }
    
    /// Carga todos los eventos del mes actual
    private func cargarEventosDelMes() {
        let calendario = Calendar.current
        let inicioMes = calendario.date(
            from: calendario.dateComponents([.year, .month], from: Date())
        )!
        let finMes = calendario.date(byAdding: .month, value: 1, to: inicioMes)!
        
        // Crear un predicado para buscar eventos en el rango de fechas
        var calendariosParaBuscar: [EKCalendar]? = nil
        if let seleccionado = calendarioSeleccionado {
            calendariosParaBuscar = [seleccionado]
        }
        
        let predicado = eventStore.predicateForEvents(
            withStart: inicioMes,
            end: finMes,
            calendars: calendariosParaBuscar
        )
        
        // Obtener eventos y ordenarlos por fecha de inicio
        eventos = eventStore.events(matching: predicado)
            .sorted { $0.startDate < $1.start