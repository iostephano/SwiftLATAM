---
sidebar_position: 1
title: Accessibility
---

# Accessibility

## ¿Qué es Accessibility?

Accessibility (Accesibilidad) es el conjunto de APIs, protocolos y herramientas proporcionadas por Apple que permiten a los desarrolladores crear aplicaciones utilizables por **todas las personas**, independientemente de sus capacidades físicas, sensoriales o cognitivas. Este framework abarca desde la compatibilidad con lectores de pantalla como VoiceOver, hasta el soporte para Dynamic Type, Switch Control, Voice Control y tecnologías de asistencia adicionales.

En el ecosistema Apple, la accesibilidad no es una característica opcional sino un **pilar fundamental** del diseño de interfaces. Las APIs de accesibilidad están integradas profundamente tanto en UIKit como en SwiftUI, permitiendo que los elementos de la interfaz expongan información semántica (etiquetas, valores, acciones, traits) al sistema operativo, que a su vez la comunica a las tecnologías de asistencia. Esto incluye el protocolo `UIAccessibility` en UIKit y los modificadores `.accessibility*` en SwiftUI.

Utilizar correctamente el framework de Accessibility no solo beneficia a usuarios con discapacidades: mejora la experiencia general de la aplicación, facilita la automatización de pruebas (las propiedades de accesibilidad se usan en UI Testing), y en muchas jurisdicciones es un **requisito legal** (como la ADA en Estados Unidos o la normativa europea EN 301 549). Además, Apple revisa activamente la accesibilidad de las apps en el proceso de revisión del App Store.

## Casos de uso principales

1. **Compatibilidad con VoiceOver**: Asegurar que cada elemento interactivo de la pantalla tenga una etiqueta descriptiva, un valor actualizado y traits correctos para que usuarios con discapacidad visual puedan navegar la app completamente con el lector de pantalla.

2. **Soporte para Dynamic Type**: Permitir que los textos de la aplicación escalen automáticamente según las preferencias de tamaño de texto del usuario, garantizando legibilidad sin romper el diseño.

3. **Adaptación a preferencias del sistema**: Respetar configuraciones como "Reducir movimiento" (`UIAccessibility.isReduceMotionEnabled`), "Aumentar contraste" (`UIAccessibility.isDarkerSystemColorsEnabled`) y "Diferenciar sin color" para ofrecer una experiencia adaptada.

4. **Acciones personalizadas para controles complejos**: Implementar `UIAccessibilityCustomAction` para elementos que tienen múltiples acciones (por ejemplo, una celda que se puede eliminar, compartir o editar) de modo que sean accesibles sin depender de gestos complejos.

5. **Navegación por contenedores**: Agrupar y ordenar lógicamente los elementos de accesibilidad mediante contenedores (`accessibilityElements`, `accessibilityContainerType`) para que la navegación con VoiceOver sea intuitiva y eficiente.

6. **Notificaciones de cambios en pantalla**: Utilizar `UIAccessibility.post(notification:argument:)` para informar a las tecnologías asistivas sobre cambios dinámicos en la interfaz, como la aparición de un alert, la carga de nuevo contenido o cambios en un formulario.

## Instalación y configuración

Accessibility está integrado de forma nativa en iOS, iPadOS, macOS, watchOS y tvOS. **No requiere instalar dependencias externas ni agregar frameworks adicionales**.

### Imports necesarios

```swift
// En UIKit, las APIs de accesibilidad están disponibles automáticamente
import UIKit

// En SwiftUI, también están integradas
import SwiftUI

// Para funcionalidades avanzadas de inspección de accesibilidad (testing)
import XCTest // Incluye APIs de accessibility para UI Testing
```

### Permisos en Info.plist

No se requieren permisos especiales en `Info.plist` para utilizar las APIs de accesibilidad. Sin embargo, hay claves informativas opcionales:

```xml
<!-- Opcional: Declarar soporte explícito para funciones de accesibilidad -->
<key>UIAccessibilityPerformEscapeAction</key>
<true/>
```

### Configuración del proyecto

Para verificar la accesibilidad durante el desarrollo:

1. **Accessibility Inspector**: Abre desde Xcode → Open Developer Tool → Accessibility Inspector
2. **VoiceOver en Simulador**: Actívalo desde Settings → Accessibility → VoiceOver en el simulador
3. **Audit de accesibilidad**: Usa el botón "Audit" en Accessibility Inspector para detectar problemas automáticamente
4. **Environment Overrides**: En Xcode, usa el botón de Environment Overrides durante la depuración para simular Dynamic Type, aumentar contraste y otras configuraciones

## Conceptos clave

### 1. Accessibility Label (`accessibilityLabel`)

Es la etiqueta descriptiva que VoiceOver lee en voz alta cuando el usuario se posiciona sobre un elemento. Debe ser **concisa, localizada y descriptiva**. No debe incluir el tipo de control (VoiceOver ya anuncia que es un botón, imagen, etc.).

```swift
// Correcto: describe qué hace
boton.accessibilityLabel = "Agregar al carrito"

// Incorrecto: incluye el tipo de control
boton.accessibilityLabel = "Botón agregar al carrito"
```

### 2. Accessibility Traits (`accessibilityTraits`)

Los traits definen el **comportamiento y naturaleza** de un elemento. Le indican a VoiceOver si el elemento es un botón, un enlace, un encabezado, si está seleccionado, si se actualiza frecuentemente, etc. Pueden combinarse.

```swift
// Un elemento que es botón y encabezado a la vez
elemento.accessibilityTraits = [.button, .header]

// Un elemento deshabilitado
elemento.accessibilityTraits.insert(.notEnabled)
```

### 3. Accessibility Value (`accessibilityValue`)

Representa el **valor actual** de un control. Es fundamental en sliders, switches, campos de texto y cualquier elemento cuyo estado cambia. Se debe actualizar cada vez que el valor cambie.

```swift
slider.accessibilityValue = "75 por ciento de volumen"
toggle.accessibilityValue = toggle.isOn ? "activado" : "desactivado"
```

### 4. Accessibility Hint (`accessibilityHint`)

Es una descripción opcional que explica **qué sucederá** al interactuar con el elemento. El usuario puede desactivar los hints en sus preferencias, por lo que no deben contener información crítica.

```swift
boton.accessibilityHint = "Toca dos veces para añadir este producto a tu carrito de compras"
```

### 5. Agrupación y orden de elementos

Controlar qué elementos son visibles para VoiceOver y en qué orden se navegan es fundamental para una experiencia coherente. Se puede agrupar información relacionada en un único elemento accesible o definir un orden de navegación personalizado.

### 6. Notificaciones de accesibilidad

Permiten informar a las tecnologías asistivas sobre cambios dinámicos. Las más comunes son `.screenChanged` (cuando la pantalla cambia completamente), `.layoutChanged` (cuando cambia la disposición) y `.announcement` (para anuncios personalizados).

## Ejemplo básico

```swift
import UIKit

/// Ejemplo básico: Configurar accesibilidad en elementos UIKit comunes
class ProductoViewController: UIViewController {
    
    // MARK: - Outlets
    @IBOutlet weak var imagenProducto: UIImageView!
    @IBOutlet weak var nombreLabel: UILabel!
    @IBOutlet weak var precioLabel: UILabel!
    @IBOutlet weak var botonComprar: UIButton!
    @IBOutlet weak var botonFavorito: UIButton!
    
    // MARK: - Propiedades
    private var esFavorito = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarAccesibilidad()
    }
    
    private func configurarAccesibilidad() {
        // La imagen del producto debe describir lo que muestra
        imagenProducto.isAccessibilityElement = true
        imagenProducto.accessibilityLabel = "Fotografía del producto: Zapatillas deportivas Nike Air Max"
        imagenProducto.accessibilityTraits = .image
        
        // El nombre ya es accesible por defecto al ser un UILabel,
        // pero lo marcamos como encabezado para facilitar la navegación
        nombreLabel.accessibilityTraits = .header
        
        // El precio es accesible por defecto, pero mejoramos la lectura
        // En lugar de leer "$1.299,99" de forma confusa, lo aclaramos
        precioLabel.accessibilityLabel = "Precio: mil doscientos noventa y nueve pesos con noventa y nueve centavos"
        
        // El botón de comprar ya tiene buen texto visible,
        // agregamos un hint para dar contexto adicional
        botonComprar.accessibilityHint = "Toca dos veces para iniciar el proceso de compra"
        
        // El botón de favorito usa solo un ícono de corazón,
        // necesita una etiqueta descriptiva
        actualizarAccesibilidadFavorito()
    }
    
    @IBAction func toggleFavorito(_ sender: UIButton) {
        esFavorito.toggle()
        actualizarAccesibilidadFavorito()
        
        // Anunciar el cambio de estado a VoiceOver
        let mensaje = esFavorito ? "Añadido a favoritos" : "Eliminado de favoritos"
        UIAccessibility.post(notification: .announcement, argument: mensaje)
    }
    
    private func actualizarAccesibilidadFavorito() {
        botonFavorito.accessibilityLabel = esFavorito
            ? "Eliminar de favoritos"
            : "Agregar a favoritos"
        botonFavorito.accessibilityValue = esFavorito
            ? "En favoritos"
            : "No está en favoritos"
    }
}
```

## Ejemplo intermedio

```swift
import SwiftUI

/// Ejemplo intermedio: Vista de lista de tareas con accesibilidad completa en SwiftUI
struct Tarea: Identifiable {
    let id = UUID()
    var titulo: String
    var descripcion: String
    var prioridad: Prioridad
    var completada: Bool
    var fechaLimite: Date
    
    enum Prioridad: String, CaseIterable {
        case alta = "Alta"
        case media = "Media"
        case baja = "Baja"
        
        /// Descripción accesible de la prioridad
        var descripcionAccesible: String {
            switch self {
            case .alta: return "prioridad alta"
            case .media: return "prioridad media"
            case .baja: return "prioridad baja"
            }
        }
    }
}

struct ListaTareasView: View {
    @State private var tareas: [Tarea] = [
        Tarea(
            titulo: "Revisar pull request",
            descripcion: "Revisar PR #234 del módulo de pagos",
            prioridad: .alta,
            completada: false,
            fechaLimite: Date().addingTimeInterval(3600)
        ),
        Tarea(
            titulo: "Actualizar dependencias",
            descripcion: "Actualizar CocoaPods y SPM packages",
            prioridad: .media,
            completada: true,
            fechaLimite: Date().addingTimeInterval(86400)
        ),
        Tarea(
            titulo: "Escribir tests unitarios",
            descripcion: "Agregar tests para el ViewModel de login",
            prioridad: .baja,
            completada: false,
            fechaLimite: Date().addingTimeInterval(172800)
        )
    ]
    
    var body: some View {
        NavigationStack {
            List {
                // Sección con encabezado accesible
                Section {
                    ForEach($tareas) { $tarea in
                        TareaRowView(tarea: $tarea)
                    }
                } header: {
                    Text("Mis Tareas")
                        // El header ya se marca como encabezado automáticamente en SwiftUI
                }
            }
            .navigationTitle("Tareas")
        }
    }
}

struct TareaRowView: View {
    @Binding var tarea: Tarea
    
    /// Formateador de fechas para accesibilidad
    private var fechaFormateada: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "es_ES")
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: tarea.fechaLimite)
    }
    
    var body: some View {
        HStack(spacing: 12) {
            // Indicador visual de prioridad (solo color, necesita alternativa textual)
            Circle()
                .fill(colorPrioridad)
                .frame(width: 12, height: 12)
                // Ocultamos el círculo de accesibilidad porque su info
                // se incluye en la etiqueta combinada del contenedor
                .accessibilityHidden(true)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(tarea.titulo)
                    .strikethrough(tarea.completada)
                    .font(.headline)
                
                Text("Fecha límite: \(fechaFormateada)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Indicador de completada
            Image(systemName: tarea.completada ? "checkmark.circle.fill" : "circle")
                .foregroundColor(tarea.completada ? .green : .gray)
                .font(.title2)
                // Ocultamos porque la acción se maneja a nivel de fila
                .accessibilityHidden(true)
        }
        .padding(.vertical, 4)
        // AGRUPAMOS toda la fila en un único elemento accesible
        .accessibilityElement(children: .combine)
        // Etiqueta combinada que da contexto completo
        .accessibilityLabel(etiquetaAccesible)
        // Valor que indica el estado actual
        .accessibilityValue(tarea.completada ? "completada" : "pendiente")
        // Trait de botón porque la fila es interactiva
        .accessibilityAddTraits(.isButton)
        // Hint que indica qué pasará al interactuar
        .accessibilityHint("Toca dos veces para marcar como \(tarea.completada ? "pendiente" : "completada")")
        // Acciones personalizadas adicionales
        .accessibilityCustomContent("Prioridad", tarea.prioridad.rawValue)
        .accessibilityCustomContent("Fecha límite", fechaFormateada)
        // Acción de toggle accesible
        .accessibilityAction {
            tarea.completada.toggle()
        }
        // Acciones personalizadas para funcionalidad extendida
        .accessibilityAction(named: "Cambiar prioridad") {
            cambiarPrioridad()
        }
        .accessibilityAction(named: "Eliminar tarea") {
            // Lógica de eliminación
        }
        .onTapGesture {
            tarea.completada.toggle()
        }
    }
    
    /// Construye la etiqueta accesible completa para VoiceOver
    private var etiquetaAccesible: String {
        var partes: [String] = []
        partes.append(tarea.titulo)
        partes.append(tarea.prioridad.descripcionAccesible)
        partes.append("fecha límite: \(fechaFormateada)")
        return partes.joined(separator: ", ")