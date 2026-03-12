---
sidebar_position: 1
title: Swiftui Intro
---

# Introducción a SwiftUI: El Futuro del Desarrollo iOS

## ¿Qué es SwiftUI?

SwiftUI es el **framework declarativo** de Apple para construir interfaces de usuario en todas sus plataformas: iOS, iPadOS, macOS, watchOS y tvOS. Fue presentado en la WWDC 2019 y representa un cambio de paradigma radical respecto a UIKit, el framework imperativo que dominó el desarrollo iOS durante más de una década.

En lugar de decirle al sistema **cómo** construir la interfaz paso a paso (enfoque imperativo), con SwiftUI le describes **qué** quieres mostrar (enfoque declarativo), y el framework se encarga del resto.

```swift
// UIKit (imperativo): le dices CÓMO hacerlo
let label = UILabel()
label.text = "Hola, LATAM"
label.font = .boldSystemFont(ofSize: 24)
label.textColor = .blue
label.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(label)
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
])

// SwiftUI (declarativo): le dices QUÉ quieres
Text("Hola, LATAM")
    .font(.title.bold())
    .foregroundColor(.blue)
```

La diferencia es evidente. Menos código, más legible, más mantenible.

---

## ¿Por qué SwiftUI es importante para devs iOS en LATAM?

El mercado de desarrollo iOS en Latinoamérica está en plena expansión. Empresas como Rappi, Mercado Libre, Nubank, Kavak y cientos de startups buscan activamente desarrolladores iOS. Aquí te explico por qué SwiftUI debe estar en tu arsenal:

### 1. **Demanda laboral creciente**
Las empresas de la región están migrando sus aplicaciones a SwiftUI. Tanto para roles locales como para trabajo remoto con empresas de Estados Unidos y Europa (muy común en LATAM), SwiftUI es cada vez más un requisito, no un "nice to have".

### 2. **Curva de aprendizaje más amigable**
Si estás empezando en iOS, SwiftUI es significativamente más fácil de aprender que UIKit. No necesitas entender el ciclo de vida complejo de los ViewControllers, Auto Layout con constraints, ni el patrón delegate desde el primer día.

### 3. **Productividad multiplicada**
Con SwiftUI escribes menos código para lograr más. Esto es crítico cuando trabajas en equipos pequeños (algo muy común en startups latinoamericanas) donde un solo desarrollador iOS lleva gran parte de la aplicación.

### 4. **Multiplataforma desde el día uno**
Con una sola base de código puedes crear aplicaciones para iPhone, iPad, Apple Watch y Mac. Esto es un diferenciador enorme para freelancers y consultores en la región.

### 5. **Apple apuesta todo por SwiftUI**
Cada año en la WWDC, las nuevas APIs llegan primero (y a veces exclusivamente) para SwiftUI. El futuro del ecosistema Apple está aquí.

---

## Conceptos Fundamentales

Antes de escribir tu primera app, necesitas entender cinco pilares de SwiftUI:

### 1. Vistas (Views)

En SwiftUI, **todo es una View**. Un texto, un botón, una imagen, una lista, incluso la pantalla completa. Cada vista es un `struct` que conforma el protocolo `View`:

```swift
struct SaludoView: View {
    var body: some View {
        Text("¡Bienvenido al desarrollo iOS!")
    }
}
```

El protocolo `View` solo requiere una propiedad computada llamada `body` que retorna `some View`. Esa palabra clave `some` es un **tipo opaco** (opaque type), que básicamente le dice al compilador: "te voy a devolver algún tipo que conforma `View`, pero no necesitas saber cuál exactamente".

### 2. Modificadores (Modifiers)

Los modificadores son métodos que aplicas a las vistas para cambiar su apariencia o comportamiento. Se encadenan uno tras otro:

```swift
struct TarjetaProductoView: View {
    var body: some View {
        Text("Tacos al Pastor - $45 MXN")
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .background(Color.green)
            .cornerRadius(12)
            .shadow(color: .gray.opacity(0.4), radius: 5, x: 0, y: 3)
    }
}
```

> **⚠️ Importante:** El orden de los modificadores importa. Cada modificador envuelve la vista anterior en una nueva vista. No es lo mismo aplicar `padding` antes de `background` que después.

```swift
// El padding está DENTRO del fondo verde
Text("Opción A")
    .padding()
    .background(Color.green)

// El padding está FUERA del fondo verde
Text("Opción B")
    .background(Color.green)
    .padding()
```

### 3. Composición de Vistas

SwiftUI fomenta la composición: construyes interfaces complejas combinando vistas pequeñas y reutilizables. Los contenedores principales son:

```swift
struct MenuRestauranteView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Contenido vertical
            Text("🍽️ Menú del Día")
                .font(.largeTitle.bold())
            
            HStack(spacing: 8) {
                // Contenido horizontal
                Image(systemName: "star.fill")
                    .foregroundColor(.yellow)
                Text("4.8")
                    .font(.subheadline)
                Text("(234 reseñas)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            ZStack {
                // Contenido superpuesto (uno encima de otro)
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.orange.opacity(0.2))
                    .frame(height: 100)
                
                Text("Promoción: 2x1 en bebidas 🥤")
                    .font(.title3.bold())
                    .foregroundColor(.orange)
            }
        }
        .padding()
    }
}
```

- **`VStack`**: apila vistas verticalmente (de arriba a abajo)
- **`HStack`**: apila vistas horizontalmente (de izquierda a derecha)
- **`ZStack`**: apila vistas en profundidad (una sobre otra)

### 4. Estado y Reactividad

Este es el **superpoder** de SwiftUI. Cuando el estado cambia, la interfaz se actualiza automáticamente. No más `reloadData()`, no más `setNeedsLayout()`:

```swift
struct ContadorView: View {
    @State private var contador: Int = 0
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Has tocado \(contador) veces")
                .font(.title2)
            
            Button(action: {
                contador += 1
            }) {
                HStack {
                    Image(systemName: "hand.tap.fill")
                    Text("Tocar")
                }
                .font(.headline)
                .foregroundColor(.white)
                .padding(.horizontal, 32)
                .padding(.vertical, 16)
                .background(Color.blue)
                .cornerRadius(12)
            }
            
            if contador >= 10 {
                Text("🎉 ¡Ya eres un experto tocando botones!")
                    .font(.caption)
                    .foregroundColor(.green)
                    .transition(.scale.combined(with: .opacity))
            }
        }
        .animation(.easeInOut, value: contador)
    }
}
```

El property wrapper `@State` le dice a SwiftUI: "vigila esta variable. Cuando cambie, recalcula el `body` y actualiza la pantalla". Esto elimina una cantidad enorme de bugs relacionados con estados desincronizados.

### 5. Preview en Tiempo Real

Una de las funcionalidades más potentes de SwiftUI es el **Canvas de Xcode**, que te muestra una vista previa en tiempo real mientras escribes código:

```swift
#Preview {
    ContadorView()
}
```

Esto acelera el ciclo de desarrollo enormemente. Ya no necesitas compilar y ejecutar en el simulador cada vez que cambias un color o un padding.

---

## Tu Primera App Completa en SwiftUI

Vamos a construir una mini app de lista de tareas que integra todos los conceptos anteriores:

```swift
import SwiftUI

// Modelo de datos
struct Tarea: Identifiable {
    let id = UUID()
    var titulo: String
    var completada: Bool = false
}

// Vista principal
struct ListaTareasView: View {
    @State private var tareas: [Tarea] = [
        Tarea(titulo: "Estudiar SwiftUI"),
        Tarea(titulo: "Practicar con proyectos personales"),
        Tarea(titulo: "Aplicar a empleos iOS en LATAM"),
        Tarea(titulo: "Contribuir a open source")
    ]
    @State private var nuevaTarea: String = ""
    
    var body: some View {
        NavigationStack {
            VStack {
                // Campo para agregar tareas
                HStack {
                    TextField("Nueva tarea...", text: $nuevaTarea)
                        .textFieldStyle(.roundedBorder)
                    
                    Button(action: agregarTarea) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                            .foregroundColor(.blue)
                    }
                    .disabled(nuevaTarea.trimmingCharacters(in: .whitespaces).isEmpty)
                }
                .padding(.horizontal)
                
                // Lista de tareas
                List {
                    ForEach($tareas) { $tarea in
                        HStack {
                            Image(systemName: tarea.completada ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(tarea.completada ? .green : .gray)
                                .onTapGesture {
                                    withAnimation {
                                        tarea.completada.toggle()
                                    }
                                }
                            
                            Text(tarea.titulo)
                                .strikethrough(tarea.completada)
                                .foregroundColor(tarea.completada ? .secondary : .primary)
                        }
                    }
                    .onDelete(perform: eliminarTarea)
                }
                
                // Resumen
                Text("\(tareasCompletadas) de \(tareas.count) completadas")
                    .font(.footnote)
                    .foregroundColor(.secondary)
                    .padding(.bottom, 8)
            }
            .navigationTitle("Mis Tareas 📋")
        }
    }
    
    // MARK: - Propiedades computadas
    
    private var tareasCompletadas: Int {
        tareas.filter { $0.completada }.count
    }
    
    // MARK: - Métodos
    
    private func agregarTarea() {
        let textoLimpio = nuevaTarea.trimmingCharacters(in: .whitespaces)
        guard !textoLimpio.isEmpty else { return }
        
        withAnimation {
            tareas.append(Tarea(titulo: textoLimpio))
        }
        nuevaTarea = ""
    }
    
    private func eliminarTarea(at offsets: IndexSet) {
        withAnimation {
            tareas.remove(atOffsets: offsets)
        }
    }
}

#Preview {
    ListaTareasView()
}
```

En menos de 90 líneas de código tienes una app funcional con:
- ✅ Navegación
- ✅ Lista dinámica con datos
- ✅ Agregar elementos
- ✅ Eliminar con deslizar
- ✅ Marcar como completado
- ✅ Animaciones
- ✅ Binding bidireccional con `$`

Intenta hacer esto con UIKit y necesitarás al menos el triple de código, un UITableViewDataSource, un UITableViewDelegate, un UINavigationController, y mucho más boilerplate.

---

## Pasos Accionables para Empezar Hoy

### Paso 1: Configura tu entorno
- Descarga **Xcode** desde la Mac App Store (es gratis)
- Necesitas macOS Ventura o posterior para las versiones más recientes
- Crea un nuevo proyecto: **File → New → Project → App** y asegúrate de seleccionar **SwiftUI** como interfaz

### Paso 2: Experimenta con el Canvas
- Abre cualquier archivo de vista SwiftUI
- Activa el Canvas con **Cmd + Option + Enter**
- Modifica el código y observa los cambios en tiempo real
- Usa **Cmd + Click** sobre cualquier vista para ver opciones contextuales

### Paso 3: Construye 3 pantallas básicas
Practica construyendo estas pantallas comunes en apps latinoamericanas:

1. **Pantalla de perfil de usuario** (foto, nombre, datos personales)
2. **Lista de productos** (imagen, nombre, precio en moneda local)
3. **Formulario de registro** (campos de texto, selectores, botón de envío)

### Paso 4: Domina el flujo de datos
Aprende los property wrappers en este orden:
1. `@State` → estado local de una vista
2. `@Binding` → compartir estado con vista hija
3. `@StateObject` / `@ObservedObject` → objetos observables
4. `@EnvironmentObject` → estado global de la app

### Paso 5: Publica algo
No esperes a tener la app perfecta. Sube tu primer proyecto a GitHub, escribe sobre lo que aprendiste en Twitter/X o en un blog. La comunidad iOS de LATAM es muy activa y solidaria.

---

## Comparativa Rápida: SwiftUI vs UIKit

| Aspecto | SwiftUI | UIKit |
|---|---|---|
| **Paradigma** | Declarativo | Imperativo |
| **Lenguaje** | Solo Swift | Swift / Objective-C |
| **Curva de aprendizaje** | Más suave | Más pronunciada |
| **Soporte mínimo** | iOS 13+ (recomendado iOS 15+) | iOS 2+ |
| **Storyboards** | No los necesita | Opcionales |
| **Vistas previas** | Canvas en tiempo real | Storyboard / simulador |
| **Madurez** | En crecimiento (desde 2019) | Muy maduro (desde 2008) |
| **Ofertas laborales** | Creciendo rápidamente | Aún dominante |
| **Recomendación** | Proyectos nuevos | Proyectos legacy |

> **💡 Consejo profesional:** No ignores UIKit por completo. Muchas empresas en LATAM tienen apps que combinan ambos frameworks. Conocer UIKit te hace más versátil y empleable. Pero si estás empezando desde cero, comienza con SwiftUI.

---

## Recursos Recomendados

### Gratuitos
- 📚 [Documentación oficial de SwiftUI](https://developer.apple.com/documentation/swiftui/) — La referencia definitiva de Apple
- 🎓 [100 Days of SwiftUI](https://www.