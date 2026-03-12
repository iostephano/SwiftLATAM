---
sidebar_position: 1
title: GameplayKit
---

# GameplayKit

## ¿Qué es GameplayKit?

GameplayKit es un framework de Apple diseñado para proporcionar herramientas y algoritmos fundamentales que facilitan el desarrollo de la lógica de juegos y aplicaciones interactivas. A diferencia de frameworks de renderizado como SpriteKit o SceneKit, GameplayKit no se encarga de la parte visual, sino de la **inteligencia artificial, la toma de decisiones, la aleatorización controlada y la organización de la lógica del juego**. Fue introducido en iOS 9 y está disponible en todas las plataformas Apple.

Este framework es especialmente valioso porque abstrae patrones de diseño complejos que tradicionalmente los desarrolladores de juegos tenían que implementar desde cero. Incluye sistemas de entidades y componentes, máquinas de estados finitos, árboles de decisión, agentes autónomos con comportamientos de navegación, generadores de números aleatorios deterministas, grafos de búsqueda de caminos (pathfinding) y sistemas de reglas lógicas. Todo esto permite construir juegos más sofisticados con menos código y mejor arquitectura.

Aunque su nombre sugiere un uso exclusivo para videojuegos, GameplayKit puede aplicarse en cualquier aplicación que necesite aleatorización controlada, máquinas de estados, o lógica basada en reglas. Por ejemplo, aplicaciones de productividad con flujos complejos de estado, apps de simulación, herramientas educativas interactivas o incluso algoritmos de distribución procedural de contenido pueden beneficiarse enormemente de este framework.

## Casos de uso principales

- **Inteligencia artificial para enemigos y NPCs**: Implementar comportamientos inteligentes para personajes no jugables mediante árboles de decisión, máquinas de estados y sistemas de reglas que definen cómo reaccionan ante diferentes situaciones del juego.

- **Búsqueda de caminos (Pathfinding)**: Calcular rutas óptimas en mapas y escenarios de juego utilizando grafos y algoritmos como A*. Ideal para juegos de estrategia, tower defense o cualquier escenario con navegación por rejillas u obstáculos.

- **Aleatorización controlada y juusta**: Generar números aleatorios deterministas y distribuciones justas (como barajar cartas o distribuir recursos) usando generadores que permiten reproducibilidad para debugging y testing.

- **Máquinas de estados finitos**: Gestionar transiciones de estado complejas para personajes (idle, corriendo, atacando, muriendo), menús de interfaz o flujos de aplicación con validación automática de transiciones.

- **Sistemas de entidades y componentes (ECS)**: Organizar la lógica del juego siguiendo el patrón Entity-Component-System, favoreciendo la composición sobre la herencia y facilitando la reutilización de comportamientos entre diferentes tipos de entidades.

- **Agentes y comportamientos autónomos**: Crear entidades que navegan de forma autónoma siguiendo objetivos como perseguir, huir, patrullar, seguir caminos o moverse en formación, simulando comportamientos emergentes realistas.

## Instalación y configuración

GameplayKit viene incluido de forma nativa en el SDK de Apple, por lo que **no requiere instalación adicional** ni gestores de paquetes como CocoaPods o SPM.

### Plataformas compatibles

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS | 9.0+ |
| macOS | 10.11+ |
| tvOS | 9.0+ |
| watchOS | No disponible |
| visionOS | 1.0+ |

### Importación en el proyecto

```swift
import GameplayKit
```

Si estás trabajando con SpriteKit o SceneKit, simplemente añade el import de GameplayKit junto al del motor de renderizado:

```swift
import SpriteKit
import GameplayKit
```

### Configuración en Xcode

1. Abre tu proyecto en Xcode.
2. Selecciona tu target principal.
3. Ve a la pestaña **General** → **Frameworks, Libraries, and Embedded Content**.
4. Haz clic en **+** y busca `GameplayKit.framework`.
5. Añádelo con la opción **Do Not Embed** (es un framework del sistema).

> **Nota:** En proyectos modernos con SwiftUI, generalmente basta con el `import GameplayKit` y Xcode vinculará el framework automáticamente.

No se requieren permisos especiales en `Info.plist` ni entitlements adicionales.

## Conceptos clave

### 1. Entidades y Componentes (ECS)

El patrón **Entity-Component-System** es la columna vertebral arquitectónica de GameplayKit. Una `GKEntity` es un contenedor genérico que representa cualquier objeto del juego (jugador, enemigo, power-up). Los `GKComponent` son módulos de funcionalidad independientes que se añaden a las entidades. Este enfoque favorece la **composición sobre la herencia**: en lugar de crear jerarquías profundas de clases, combinas componentes reutilizables.

```
Entidad "Jugador" = ComponenteVida + ComponenteMovimiento + ComponenteRenderizado
Entidad "Enemigo" = ComponenteVida + ComponenteIA + ComponenteRenderizado
```

### 2. Máquinas de estados (State Machines)

`GKStateMachine` y `GKState` permiten modelar comportamientos como un conjunto finito de estados con transiciones controladas. Cada estado define qué transiciones son válidas, qué ocurre al entrar, al salir y en cada actualización. Esto elimina los temidos `if-else` o `switch` anidados que generan código frágil y difícil de mantener.

### 3. Generadores de números aleatorios

GameplayKit ofrece múltiples generadores (`GKLinearCongruentialRandomSource`, `GKMersenneTwisterRandomSource`, `GKARC4RandomSource`) y distribuciones (`GKRandomDistribution`, `GKGaussianDistribution`, `GKShuffledDistribution`). La clave es que son **deterministas**: con la misma semilla, producen la misma secuencia, lo cual es invaluable para testing y replays.

### 4. Pathfinding (Búsqueda de caminos)

Mediante `GKGraph`, `GKGridGraph` y `GKObstacleGraph`, puedes definir la topología navegable de tu escenario y usar el método `findPath(from:to:)` para calcular rutas óptimas. GameplayKit implementa internamente el algoritmo A*.

### 5. Agentes y Comportamientos

`GKAgent` es un componente especial que simula movimiento autónomo en 2D o 3D. Los agentes siguen `GKGoal` (objetivos como perseguir, huir, evitar obstáculos) agrupados en un `GKBehavior`. El sistema calcula automáticamente las fuerzas necesarias para cumplir los objetivos combinados.

### 6. Sistemas de reglas

`GKRuleSystem` permite evaluar conjuntos de reglas (`GKRule`) contra un estado (hechos/facts) para tomar decisiones complejas. Es ideal para lógica de IA donde múltiples condiciones deben evaluarse en conjunto, similar a un motor de inferencia ligero.

## Ejemplo básico

Este ejemplo muestra cómo usar los generadores de números aleatorios para crear un sistema de dado justo y una distribución gaussiana:

```swift
import GameplayKit

// MARK: - Ejemplo básico: Aleatorización controlada

// 1. Crear un generador de números aleatorios determinista
// Usar una semilla fija permite reproducir la misma secuencia
let randomSource = GKMersenneTwisterRandomSource(seed: 12345)

// 2. Generar un número aleatorio simple entre 1 y 6 (dado estándar)
let dado = GKRandomDistribution(
    randomSource: randomSource,
    lowestValue: 1,
    highestValue: 6
)

// Lanzar el dado 5 veces
for i in 1...5 {
    let resultado = dado.nextInt()
    print("Lanzamiento \(i): \(resultado)")
}

// 3. Distribución gaussiana (campana de Gauss)
// Útil para generar valores que se concentran cerca del promedio
let gaussiana = GKGaussianDistribution(
    randomSource: GKMersenneTwisterRandomSource(),
    lowestValue: 1,
    highestValue: 100
)

// Los valores tenderán a estar cerca de 50
for _ in 1...10 {
    print("Valor gaussiano: \(gaussiana.nextInt())")
}

// 4. Distribución mezclada (anti-repetición)
// Garantiza que no se repiten valores hasta agotar el rango
let baraja = GKShuffledDistribution(
    randomSource: GKMersenneTwisterRandomSource(),
    lowestValue: 1,
    highestValue: 6
)

// Nunca repetirá un número hasta haber sacado todos los del rango
print("\n--- Distribución sin repeticiones ---")
for i in 1...12 {
    print("Tirada \(i): \(baraja.nextInt())")
}

// 5. Mezclar un array de forma aleatoria (barajar cartas)
let cartas = ["As", "Rey", "Reina", "Jota", "10", "9", "8", "7"]
let cartasBarajadas = GKRandomSource.sharedRandom().arrayByShufflingObjects(in: cartas)
print("\nCartas barajadas: \(cartasBarajadas)")
```

## Ejemplo intermedio

Este ejemplo implementa una máquina de estados completa para un personaje de videojuego con transiciones controladas:

```swift
import GameplayKit

// MARK: - Ejemplo intermedio: Máquina de estados para un personaje

// 1. Definimos los estados del personaje heredando de GKState

/// Estado de reposo: el personaje está quieto
class EstadoReposo: GKState {
    
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        // Desde reposo se puede pasar a correr o saltar
        return stateClass == EstadoCorriendo.self || stateClass == EstadoSaltando.self
    }
    
    override func didEnter(from previousState: GKState?) {
        print("🧍 Personaje en reposo")
        // Aquí activarías la animación idle del sprite
    }
    
    override func update(deltaTime seconds: TimeInterval) {
        // Lógica de actualización por frame en estado reposo
        // Por ejemplo, recuperar energía gradualmente
    }
}

/// Estado de carrera: el personaje se mueve horizontalmente
class EstadoCorriendo: GKState {
    var velocidad: CGFloat = 200.0
    
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        // Desde corriendo se puede volver a reposo, saltar o recibir daño
        return stateClass == EstadoReposo.self ||
               stateClass == EstadoSaltando.self ||
               stateClass == EstadoRecibiendoDanio.self
    }
    
    override func didEnter(from previousState: GKState?) {
        print("🏃 Personaje corriendo a \(velocidad) pts/s")
    }
    
    override func willExit(to nextState: GKState) {
        print("🏃 Dejando de correr para ir a: \(type(of: nextState))")
    }
    
    override func update(deltaTime seconds: TimeInterval) {
        let desplazamiento = velocidad * CGFloat(seconds)
        // Aquí moverías el sprite del personaje
        print("  → Desplazamiento este frame: \(String(format: "%.2f", desplazamiento)) pts")
    }
}

/// Estado de salto: el personaje está en el aire
class EstadoSaltando: GKState {
    var tiempoEnAire: TimeInterval = 0
    let duracionMaxima: TimeInterval = 0.8
    
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        // Desde el salto solo se puede volver a reposo (aterrizar)
        // o recibir daño en el aire
        return stateClass == EstadoReposo.self ||
               stateClass == EstadoRecibiendoDanio.self
    }
    
    override func didEnter(from previousState: GKState?) {
        tiempoEnAire = 0
        print("🦘 Personaje saltando!")
    }
    
    override func update(deltaTime seconds: TimeInterval) {
        tiempoEnAire += seconds
        
        // Transición automática: si ya pasó el tiempo de salto, aterrizar
        if tiempoEnAire >= duracionMaxima {
            stateMachine?.enter(EstadoReposo.self)
        }
    }
}

/// Estado de daño: el personaje recibió un golpe
class EstadoRecibiendoDanio: GKState {
    var tiempoInvulnerable: TimeInterval = 0
    let duracionInvulnerabilidad: TimeInterval = 1.5
    
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        // Tras recibir daño, vuelve a reposo
        // NO puede recibir daño mientras ya está en este estado
        return stateClass == EstadoReposo.self
    }
    
    override func didEnter(from previousState: GKState?) {
        tiempoInvulnerable = 0
        print("💥 ¡Personaje recibió daño! Invulnerable por \(duracionInvulnerabilidad)s")
    }
    
    override func update(deltaTime seconds: TimeInterval) {
        tiempoInvulnerable += seconds
        
        if tiempoInvulnerable >= duracionInvulnerabilidad {
            stateMachine?.enter(EstadoReposo.self)
        }
    }
}

// 2. Crear la máquina de estados con todos los estados posibles
let maquinaEstados = GKStateMachine(states: [
    EstadoReposo(),
    EstadoCorriendo(),
    EstadoSaltando(),
    EstadoRecibiendoDanio()
])

// 3. Establecer el estado inicial
maquinaEstados.enter(EstadoReposo.self)

// 4. Simular transiciones del juego
print("\n--- Simulación de gameplay ---")

maquinaEstados.enter(EstadoCorriendo.self) // ✅ Válido: reposo → corriendo

// Simular algunos frames de actualización (16ms por frame ≈ 60fps)
maquinaEstados.update(deltaTime: 0.016)
maquinaEstados.update(deltaTime: 0.016)

maquinaEstados.enter(EstadoSaltando.self)  // ✅ Válido: corriendo → saltando

// Simular frames durante el salto
for _ in 1...60 {
    maquinaEstados.update(deltaTime: 0.016) // Aterrizará automáticamente
}

// Intentar una transición inválida
let resultado = maquinaEstados.enter(EstadoRecibiendoDanio.self)
print("¿Transición reposo → daño válida? \(resultado)") // false: no definida

maquinaEstados.enter(EstadoCorriendo.self)
maquinaEstados.enter(EstadoRecibiendoDanio.self) // ✅ Válido: corriendo → daño
```

##