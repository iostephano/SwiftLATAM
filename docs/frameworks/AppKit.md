---
sidebar_position: 1
title: AppKit
---

# AppKit

## ¿Qué es AppKit?

AppKit es el framework fundamental de Apple para construir aplicaciones de escritorio en **macOS**. Es el equivalente de UIKit en iOS, pero diseñado específicamente para la experiencia de usuario del Mac, incluyendo ventanas redimensionables, barras de menú, eventos de teclado y ratón, drag & drop, y todo el ecosistema de interacción que caracteriza a las aplicaciones nativas de escritorio. AppKit existe desde los orígenes de macOS (anteriormente OS X) y tiene sus raíces en el framework de NeXTSTEP, lo que lo convierte en uno de los frameworks más maduros y robustos del ecosistema Apple.

AppKit proporciona las clases esenciales para gestionar ventanas (`NSWindow`), vistas (`NSView`), controles de interfaz (`NSButton`, `NSTextField`, `NSTableView`), menús (`NSMenu`), eventos del sistema, gestión del portapapeles, impresión, accesibilidad y mucho más. Cualquier aplicación macOS que necesite una interfaz gráfica rica y nativa depende directa o indirectamente de AppKit, incluso cuando se utiliza SwiftUI como capa de presentación.

Se recomienda utilizar AppKit cuando se necesita **control total** sobre la experiencia de usuario en macOS, cuando se trabaja con funcionalidades específicas del escritorio que SwiftUI aún no cubre completamente, o cuando se mantiene una aplicación macOS existente. También es indispensable al crear extensiones del sistema, plugins, aplicaciones que manipulan ventanas de forma avanzada o que requieren integración profunda con tecnologías exclusivas de macOS como AppleScript, Services o la Touch Bar.

## Casos de uso principales

- **Aplicaciones de productividad de escritorio**: Editores de texto, hojas de cálculo, gestores de archivos y herramientas profesionales que requieren barras de menú complejas, múltiples ventanas y atajos de teclado avanzados.

- **Editores gráficos y multimedia**: Aplicaciones de diseño, edición de imagen/vídeo o audio que necesitan vistas personalizadas con renderizado por píxel, soporte de drag & drop y paneles flotantes.

- **Aplicaciones basadas en documentos**: Apps que implementan el patrón `NSDocument` para gestionar la apertura, edición, guardado y versionado de archivos, como procesadores de texto o editores de código.

- **Herramientas de desarrollo y utilidades del sistema**: IDEs, inspectores de procesos, monitores de red y utilidades que interactúan estrechamente con las APIs del sistema operativo.

- **Preferencias del sistema y extensiones**: Paneles de preferencias, extensiones de Finder, Quick Look previews y otros componentes que se integran directamente con macOS.

- **Aplicaciones con interfaz híbrida SwiftUI/AppKit**: Proyectos modernos que utilizan SwiftUI como interfaz principal pero recurren a AppKit para funcionalidades que SwiftUI aún no soporta de forma nativa.

## Instalación y configuración

AppKit viene incluido de forma nativa en macOS y no requiere instalación adicional mediante Swift Package Manager, CocoaPods ni ningún gestor de dependencias. Está disponible automáticamente en cualquier proyecto macOS.

### Crear un proyecto con AppKit

En Xcode, selecciona **File → New → Project → macOS → App**. En la sección "Interface", elige **XIB** o **Storyboard** para una aplicación AppKit pura, o **SwiftUI** si deseas una app híbrida.

### Import necesario

```swift
import AppKit
```

En la mayoría de los archivos de un proyecto macOS, Cocoa ya incluye AppKit:

```swift
import Cocoa // Incluye AppKit, Foundation y CoreData
```

### Estructura mínima del Info.plist

Para aplicaciones AppKit estándar, el `Info.plist` generado automáticamente incluye las claves necesarias. Sin embargo, según las funcionalidades que utilices, podrías necesitar declarar permisos adicionales:

```xml
<!-- Acceso a la cámara -->
<key>NSCameraUsageDescription</key>
<string>La app necesita acceso a la cámara para videollamadas</string>

<!-- Acceso al micrófono -->
<key>NSMicrophoneUsageDescription</key>
<string>La app necesita acceso al micrófono para grabación de audio</string>

<!-- Acceso a archivos del usuario (sandboxed apps) -->
<key>com.apple.security.files.user-selected.read-write</key>
<true/>

<!-- Acceso a red -->
<key>com.apple.security.network.client</key>
<true/>
```

### Punto de entrada de la aplicación

En proyectos AppKit modernos con Swift, el punto de entrada se define típicamente así:

```swift
// main.swift (si no usas @NSApplicationMain o @main)
import AppKit

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
```

O con el atributo de clase:

```swift
@main
class AppDelegate: NSObject, NSApplicationDelegate {
    // Punto de entrada automático
}
```

## Conceptos clave

### 1. NSApplication

`NSApplication` es el objeto singleton que representa la aplicación en ejecución. Gestiona el ciclo de vida principal, el bucle de eventos (event loop), la barra de menú global y la comunicación con el sistema operativo. Toda aplicación AppKit tiene exactamente una instancia accesible mediante `NSApplication.shared` (o `NSApp`).

### 2. NSWindow y NSWindowController

`NSWindow` representa una ventana individual en pantalla. A diferencia de iOS donde una app normalmente tiene una sola ventana, en macOS una aplicación puede tener múltiples ventanas simultáneas. `NSWindowController` es el controlador que gestiona el ciclo de vida de una ventana, su carga desde un NIB/Storyboard y su configuración. Es el equivalente conceptual a `UIWindowScene` en iPadOS, pero mucho más flexible.

### 3. NSView y NSViewController

`NSView` es la clase base para todos los elementos visuales en pantalla: botones, campos de texto, tablas, vistas personalizadas, etc. `NSViewController` gestiona una jerarquía de vistas y su ciclo de vida (`viewDidLoad`, `viewWillAppear`, `viewDidAppear`, etc.), de forma similar a `UIViewController` en UIKit.

### 4. Responder Chain (Cadena de respuesta)

La Responder Chain es el mecanismo fundamental de AppKit para el manejo de eventos. Los eventos (clics, pulsaciones de teclado, acciones de menú) viajan por una cadena de objetos `NSResponder` — desde la vista que tiene el foco hasta la ventana, el window controller, el app delegate — hasta que alguno los maneja. Este patrón permite que los menús y atajos de teclado funcionen de forma contextual sin acoplamiento directo.

### 5. NSDocument Architecture

AppKit incluye una arquitectura completa para aplicaciones basadas en documentos. `NSDocument` representa un archivo abierto, `NSDocumentController` gestiona todos los documentos abiertos, y la integración con el sistema de archivos (abrir, guardar, guardar como, revertir, auto-guardado, versiones) viene implementada de forma automática.

### 6. Bindings y Cocoa Bindings

Cocoa Bindings es un sistema declarativo que permite conectar propiedades de objetos del modelo directamente con elementos de la interfaz, reduciendo drásticamente el código "glue". Aunque ha perdido protagonismo frente a Combine y SwiftUI, sigue siendo poderoso para desarrollo rápido con Interface Builder.

## Ejemplo básico

```swift
import AppKit

// MARK: - Delegado de la aplicación
// Este ejemplo crea una ventana simple con un botón y una etiqueta

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    
    // Referencia fuerte a la ventana para evitar que se libere
    var window: NSWindow!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Crear la ventana principal
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 480, height: 320),
            styleMask: [.titled, .closable, .resizable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Mi Primera App AppKit"
        window.center() // Centrar en la pantalla
        
        // Crear una etiqueta de bienvenida
        let etiqueta = NSTextField(labelWithString: "¡Hola, macOS!")
        etiqueta.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        etiqueta.alignment = .center
        etiqueta.frame = NSRect(x: 40, y: 180, width: 400, height: 40)
        
        // Crear un botón interactivo
        let boton = NSButton(
            title: "Pulsar aquí",
            target: self,
            action: #selector(botonPulsado)
        )
        boton.bezelStyle = .rounded
        boton.frame = NSRect(x: 180, y: 100, width: 120, height: 32)
        
        // Añadir los elementos a la ventana
        window.contentView?.addSubview(etiqueta)
        window.contentView?.addSubview(boton)
        
        // Mostrar la ventana y traerla al frente
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    
    @objc func botonPulsado() {
        // Mostrar una alerta nativa de macOS
        let alerta = NSAlert()
        alerta.messageText = "¡Funciona!"
        alerta.informativeText = "Has pulsado el botón correctamente."
        alerta.alertStyle = .informational
        alerta.addButton(withTitle: "Aceptar")
        alerta.runModal()
    }
    
    // Permitir que la app termine al cerrar la última ventana
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}
```

## Ejemplo intermedio

```swift
import AppKit

// MARK: - Modelo de datos
// Representa una tarea en una lista de pendientes

struct Tarea: Identifiable {
    let id = UUID()
    var titulo: String
    var completada: Bool = false
    var fechaCreacion: Date = Date()
    
    var descripcionEstado: String {
        completada ? "✅ Completada" : "⏳ Pendiente"
    }
}

// MARK: - ViewController principal con NSTableView
// Gestiona una lista de tareas con operaciones CRUD

class TareasViewController: NSViewController {
    
    // MARK: - Propiedades
    private var tareas: [Tarea] = [
        Tarea(titulo: "Configurar proyecto Xcode"),
        Tarea(titulo: "Diseñar la interfaz de usuario"),
        Tarea(titulo: "Implementar la lógica de negocio"),
        Tarea(titulo: "Escribir pruebas unitarias"),
        Tarea(titulo: "Preparar build de distribución")
    ]
    
    // MARK: - UI Elements
    private let tableView = NSTableView()
    private let scrollView = NSScrollView()
    private let campoTexto = NSTextField()
    private let botonAgregar = NSButton()
    private let botonEliminar = NSButton()
    private let botonToggle = NSButton()
    
    // MARK: - Ciclo de vida
    
    override func loadView() {
        // Crear la vista raíz manualmente (sin NIB)
        self.view = NSView(frame: NSRect(x: 0, y: 0, width: 600, height: 450))
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarTabla()
        configurarControles()
        configurarLayout()
    }
    
    // MARK: - Configuración de la interfaz
    
    private func configurarTabla() {
        // Columna de título
        let columnaTitulo = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("titulo"))
        columnaTitulo.title = "Tarea"
        columnaTitulo.width = 350
        tableView.addTableColumn(columnaTitulo)
        
        // Columna de estado
        let columnaEstado = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("estado"))
        columnaEstado.title = "Estado"
        columnaEstado.width = 150
        tableView.addTableColumn(columnaEstado)
        
        // Configurar delegado y data source
        tableView.delegate = self
        tableView.dataSource = self
        tableView.usesAlternatingRowBackgroundColors = true
        tableView.allowsMultipleSelection = false
        
        // Configurar el scroll view contenedor
        scrollView.documentView = tableView
        scrollView.hasVerticalScroller = true
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
    }
    
    private func configurarControles() {
        // Campo de texto para nuevas tareas
        campoTexto.placeholderString = "Escribe una nueva tarea..."
        campoTexto.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(campoTexto)
        
        // Botón agregar
        botonAgregar.title = "➕ Agregar"
        botonAgregar.bezelStyle = .rounded
        botonAgregar.target = self
        botonAgregar.action = #selector(agregarTarea)
        botonAgregar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(botonAgregar)
        
        // Botón eliminar
        botonEliminar.title = "🗑 Eliminar"
        botonEliminar.bezelStyle = .rounded
        botonEliminar.target = self
        botonEliminar.action = #selector(eliminarTarea)
        botonEliminar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(botonEliminar)
        
        // Botón alternar estado
        botonToggle.title = "🔄 Cambiar Estado"
        botonToggle.bezelStyle = .rounded
        botonToggle.target = self
        botonToggle.action = #selector(toggleEstado)
        botonToggle.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(botonToggle)
    }
    
    private func configurarLayout() {
        NSLayoutConstraint.activate([
            // Campo de texto en la parte superior
            campoTexto.topAnchor.constraint(equalTo: view.topAnchor, constant: 12),
            campoTexto.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),
            campoTexto.trailingAnchor.constraint(equalTo: botonAgregar.leadingAnchor, constant: -8),
            campoTexto.heightAnchor.constraint(equalToConstant: 28),
            
            // Botón agregar
            botonAgregar.topAnchor.constraint(equalTo: view.topAnchor, constant: 12),
            botonAgregar.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -12),
            botonAgregar.widthAnchor.constraint(equalToConstant: 100),
            
            // Tabla central
            