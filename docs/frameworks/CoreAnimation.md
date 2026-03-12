---
sidebar_position: 1
title: CoreAnimation
---

# CoreAnimation

## ¿Qué es CoreAnimation?

Core Animation es el framework de renderizado gráfico y animación que constituye la columna vertebral del sistema visual de iOS y macOS. Actúa como una capa intermedia entre el código de la aplicación y el hardware gráfico (GPU), permitiendo crear animaciones fluidas de alto rendimiento sin necesidad de gestionar directamente los ciclos de dibujo ni los hilos de renderizado. Cada vista que se muestra en pantalla, ya sea en UIKit o en SwiftUI, está respaldada internamente por un objeto `CALayer` gestionado por Core Animation.

A diferencia de los enfoques de animación basados en temporizadores manuales, Core Animation emplea un modelo declarativo: el desarrollador define el estado inicial y final de las propiedades que desea animar (posición, opacidad, escala, rotación, etc.) y el framework se encarga de interpolar los valores intermedios, ejecutar la animación en un hilo de renderizado independiente y componer los fotogramas directamente en la GPU. Esto libera al hilo principal de la aplicación y garantiza una tasa de refresco estable de 60 o 120 fps según el dispositivo.

Core Animation resulta esencial cuando se necesitan animaciones que van más allá de las APIs de conveniencia de UIKit o SwiftUI: animaciones de partículas, transiciones complejas con múltiples capas, animaciones sincronizadas con rutas Bézier, efectos de enmascaramiento avanzado, réplicas de capas o control preciso del timing. Es el pilar sobre el que se construyen frameworks de nivel superior como UIView.animate y las transiciones de SwiftUI, por lo que comprenderlo a fondo otorga al desarrollador un control total sobre la experiencia visual de su aplicación.

## Casos de uso principales

- **Animaciones de interfaz de usuario personalizadas**: Transiciones de pantalla, botones con feedback animado, indicadores de carga personalizados y animaciones de estado que no se logran fácilmente con `UIView.animate`.

- **Animaciones a lo largo de rutas (keypath animations)**: Mover elementos a lo largo de curvas Bézier arbitrarias, ideal para onboardings interactivos, tutoriales animados o efectos de gamificación.

- **Efectos de partículas y replicación**: Mediante `CAEmitterLayer` y `CAReplicatorLayer` se crean efectos de confeti, lluvia, nieve, ecualizadores visuales y patrones repetitivos de forma eficiente.

- **Transiciones personalizadas entre vistas y controladores**: Usando `CATransition` o animaciones coordinadas de múltiples capas para crear flujos de navegación únicos.

- **Gráficos vectoriales animados**: Con `CAShapeLayer` se dibujan y animan trazados vectoriales en tiempo real, útil para gráficas de datos, indicadores de progreso circular y logotipos animados.

- **Renderizado de contenido en capas con composición avanzada**: Sombras, bordes redondeados, máscaras, gradientes (`CAGradientLayer`) y transformaciones 3D que se componen en la GPU para mantener el rendimiento.

## Instalación y configuración

Core Animation forma parte del framework **QuartzCore**, que viene incluido en el SDK de iOS y macOS, por lo que **no requiere instalación adicional** mediante gestores de dependencias como SPM o CocoaPods.

### Import necesario

```swift
import QuartzCore
```

> **Nota:** Si ya importas `UIKit` o `SwiftUI`, el acceso a las clases de Core Animation está disponible implícitamente, ya que UIKit reexporta QuartzCore. Sin embargo, es buena práctica incluir el import explícito cuando se trabaja intensivamente con capas.

### Configuración en el proyecto

No se requieren permisos en `Info.plist` ni entitlements especiales. Core Animation funciona directamente sobre cualquier proyecto iOS/macOS. Para habilitar el perfilado avanzado de animaciones, puedes activar las opciones de depuración en el simulador:

```
Debug → Color Blended Layers
Debug → Color Off-screen Rendered
Debug → Color Hits Green and Misses Red
```

Estas herramientas, combinadas con **Instruments → Core Animation**, permiten detectar cuellos de botella en el renderizado.

## Conceptos clave

### 1. CALayer — La unidad fundamental de composición

`CALayer` es la clase base del sistema de capas. Cada `UIView` posee un `layer` subyacente que almacena las propiedades visuales (contenido bitmap, geometría, transformaciones, opacidad). A diferencia de las vistas, las capas **no manejan eventos de usuario** y son más ligeras, lo que permite crear jerarquías complejas con mejor rendimiento.

```swift
let capa = CALayer()
capa.frame = CGRect(x: 0, y: 0, width: 100, height: 100)
capa.backgroundColor = UIColor.systemBlue.cgColor
capa.cornerRadius = 16
view.layer.addSublayer(capa)
```

### 2. Model Layer vs Presentation Layer

Core Animation mantiene dos copias del árbol de capas. El **model layer** (`layer`) refleja los valores finales asignados por el desarrollador. El **presentation layer** (`layer.presentation()`) refleja los valores interpolados en el instante actual de una animación en curso. Entender esta dualidad es clave para realizar hit-testing durante animaciones.

### 3. CAAnimation y sus subclases

La jerarquía de animaciones parte de `CAAnimation` (abstracta) y se ramifica en:

| Clase | Propósito |
|---|---|
| `CABasicAnimation` | Anima una propiedad de un valor A a un valor B |
| `CAKeyframeAnimation` | Anima a través de múltiples valores clave |
| `CASpringAnimation` | Animación con dinámica de resorte |
| `CAAnimationGroup` | Agrupa varias animaciones para ejecutarlas de forma sincronizada |
| `CATransition` | Transiciones predefinidas entre estados de contenido |

### 4. Timing — CAMediaTimingFunction

El timing define la curva de aceleración de una animación. Core Animation ofrece funciones predefinidas (`.linear`, `.easeIn`, `.easeOut`, `.easeInEaseOut`) y permite curvas Bézier cúbicas personalizadas para control total del ritmo.

### 5. Capas especializadas

Core Animation proporciona subclases de `CALayer` diseñadas para tareas específicas:

- **`CAShapeLayer`**: Renderiza rutas `CGPath` con relleno y trazo configurable.
- **`CAGradientLayer`**: Dibuja gradientes de color.
- **`CATextLayer`**: Renderiza texto de forma eficiente.
- **`CAEmitterLayer`**: Sistema de partículas 2D.
- **`CAReplicatorLayer`**: Replica y transforma copias de sus subcapas.
- **`CAScrollLayer`**: Gestiona scroll de contenido dentro de la capa.

### 6. Transacciones implícitas y explícitas — CATransaction

Toda modificación de propiedades animables de un `CALayer` standalone desencadena una **animación implícita**. `CATransaction` permite agrupar cambios, personalizar la duración o **desactivar** las animaciones implícitas cuando no se desean.

```swift
CATransaction.begin()
CATransaction.setDisableActions(true) // Sin animación
capa.position = nuevaPosición
CATransaction.commit()
```

## Ejemplo básico

Este ejemplo anima la opacidad de una capa con una `CABasicAnimation`:

```swift
import UIKit
import QuartzCore

class AnimacionBasicaViewController: UIViewController {

    // Capa que vamos a animar
    private let circulo = CAShapeLayer()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        configurarCirculo()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        animarOpacidad()
    }

    private func configurarCirculo() {
        // Definir un círculo de 120 puntos de diámetro
        let diametro: CGFloat = 120
        let origen = CGPoint(
            x: view.bounds.midX - diametro / 2,
            y: view.bounds.midY - diametro / 2
        )
        let rect = CGRect(origin: origen, size: CGSize(width: diametro, height: diametro))

        circulo.path = UIBezierPath(ovalIn: rect).cgPath
        circulo.fillColor = UIColor.systemIndigo.cgColor
        view.layer.addSublayer(circulo)
    }

    private func animarOpacidad() {
        // Crear animación básica sobre la propiedad "opacity"
        let animacion = CABasicAnimation(keyPath: "opacity")
        animacion.fromValue = 1.0           // Valor inicial
        animacion.toValue = 0.1             // Valor final
        animacion.duration = 1.5            // Duración en segundos
        animacion.autoreverses = true        // Ida y vuelta
        animacion.repeatCount = .infinity    // Repetir indefinidamente

        // Función de timing suave
        animacion.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)

        // Agregar la animación a la capa
        circulo.add(animacion, forKey: "pulsarOpacidad")
    }
}
```

## Ejemplo intermedio

Indicador de progreso circular animado usando `CAShapeLayer` con animación de trazado:

```swift
import UIKit
import QuartzCore

/// Vista reutilizable que muestra un indicador de progreso circular animado.
final class IndicadorProgresoCircular: UIView {

    // MARK: - Capas

    /// Capa de fondo (track gris)
    private let capaFondo = CAShapeLayer()

    /// Capa de progreso (arco de color)
    private let capaProgreso = CAShapeLayer()

    // MARK: - Propiedades públicas

    /// Color del arco de progreso
    var colorProgreso: UIColor = .systemBlue {
        didSet { capaProgreso.strokeColor = colorProgreso.cgColor }
    }

    /// Grosor de la línea
    var grosorLinea: CGFloat = 8 {
        didSet {
            capaFondo.lineWidth = grosorLinea
            capaProgreso.lineWidth = grosorLinea
        }
    }

    // MARK: - Inicializadores

    override init(frame: CGRect) {
        super.init(frame: frame)
        configurarCapas()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        configurarCapas()
    }

    // MARK: - Layout

    override func layoutSubviews() {
        super.layoutSubviews()
        let ruta = crearRutaCircular()
        capaFondo.path = ruta.cgPath
        capaProgreso.path = ruta.cgPath

        // Centrar las capas
        capaFondo.frame = bounds
        capaProgreso.frame = bounds
    }

    // MARK: - Configuración privada

    private func configurarCapas() {
        // Capa de fondo
        capaFondo.fillColor = UIColor.clear.cgColor
        capaFondo.strokeColor = UIColor.systemGray5.cgColor
        capaFondo.lineWidth = grosorLinea
        capaFondo.lineCap = .round
        layer.addSublayer(capaFondo)

        // Capa de progreso
        capaProgreso.fillColor = UIColor.clear.cgColor
        capaProgreso.strokeColor = colorProgreso.cgColor
        capaProgreso.lineWidth = grosorLinea
        capaProgreso.lineCap = .round
        capaProgreso.strokeEnd = 0 // Inicialmente sin progreso
        layer.addSublayer(capaProgreso)
    }

    private func crearRutaCircular() -> UIBezierPath {
        let centro = CGPoint(x: bounds.midX, y: bounds.midY)
        let radio = (min(bounds.width, bounds.height) - grosorLinea) / 2
        return UIBezierPath(
            arcCenter: centro,
            radius: radio,
            startAngle: -.pi / 2,           // 12 en punto
            endAngle: .pi * 1.5,             // Vuelta completa
            clockwise: true
        )
    }

    // MARK: - API pública

    /// Anima el progreso desde el valor actual hasta el valor destino (0.0 - 1.0).
    func establecerProgreso(_ progreso: CGFloat, duracion: CFTimeInterval = 0.8) {
        let valorActual = capaProgreso.presentation()?.strokeEnd ?? capaProgreso.strokeEnd

        // Animación de strokeEnd para dibujar el arco gradualmente
        let animacion = CABasicAnimation(keyPath: "strokeEnd")
        animacion.fromValue = valorActual
        animacion.toValue = max(0, min(progreso, 1.0))
        animacion.duration = duracion
        animacion.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        animacion.fillMode = .forwards
        animacion.isRemovedOnCompletion = false

        // Actualizar el model layer
        capaProgreso.strokeEnd = max(0, min(progreso, 1.0))
        capaProgreso.add(animacion, forKey: "animarProgreso")
    }

    /// Inicia una animación de carga indeterminada con rotación continua.
    func iniciarCargaIndeterminada() {
        capaProgreso.strokeEnd = 0.75

        // Rotación continua
        let rotacion = CABasicAnimation(keyPath: "transform.rotation.z")
        rotacion.fromValue = 0
        rotacion.toValue = CGFloat.pi * 2
        rotacion.duration = 1.0
        rotacion.repeatCount = .infinity

        // Animación de trazo pulsante
        let pulso = CABasicAnimation(keyPath: "strokeEnd")
        pulso.fromValue = 0.2
        pulso.toValue = 0.85
        pulso.duration = 0.8
        pulso.autoreverses = true
        pulso.repeatCount = .infinity
        pulso.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)

        capaProgreso.add(rotacion, forKey: "rotacionContinua")
        capaProgreso.add(pulso, forKey: "pulsoCarga")
    }

    /// Detiene todas las animaciones.
    func detenerAnimaciones() {
        capaProgreso.removeAllAnimations()
    }
}

// MARK: - Uso en un ViewController

class ProgresoViewController: UIViewController {

    private let indicador = IndicadorProgresoCircular()
    private var progresoActual: CGFloat = 0.0

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground

        // Configurar el indicador
        indicador.frame = CGRect(x: 0, y: 0, width: 150, height: 150)
        indicador.center = view.center
        indicador.colorProgreso = .systemGreen
        indicador.grosorLinea = 10
        view.addSubview(indicador)

        // Botón para incrementar progreso
        let boton = UIButton(type: .system)
        boton.setTitle("Incrementar 25%", for: .normal)
        boton.titleLabel?.font = .systemFont(ofSize: