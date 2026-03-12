---
sidebar_position: 1
title: CoreMotion
---

# CoreMotion

## ¿Qué es CoreMotion?

CoreMotion es el framework de Apple que proporciona acceso a los datos de los sensores de movimiento integrados en los dispositivos iOS, iPadOS y watchOS. A través de este framework, los desarrolladores pueden obtener información del **acelerómetro**, **giroscopio**, **magnetómetro**, **podómetro**, **altímetro barométrico** y el sistema de **reconocimiento de actividad del usuario**. CoreMotion se encarga de fusionar los datos crudos de múltiples sensores para ofrecer mediciones procesadas y de alta precisión.

Este framework es esencial cuando tu aplicación necesita comprender cómo se mueve el dispositivo en el espacio tridimensional o cómo se mueve el usuario que lo lleva consigo. Desde detectar si el usuario está caminando, corriendo o conduciendo, hasta medir pasos, distancias recorridas, pisos subidos, o incluso la orientación precisa del dispositivo, CoreMotion expone toda esta información de manera eficiente y con bajo consumo energético.

Es importante destacar que CoreMotion procesa los datos directamente en el **coprocesador de movimiento** (serie M) de Apple, lo que permite recopilar datos históricos de actividad sin mantener la aplicación activa constantemente. Esto lo convierte en una herramienta fundamental para aplicaciones de salud, fitness, realidad aumentada, juegos, navegación y cualquier experiencia que dependa del contexto físico del usuario.

## Casos de uso principales

- **Aplicaciones de fitness y salud**: Conteo de pasos, distancia recorrida, pisos subidos y calorías estimadas. CoreMotion alimenta directamente funcionalidades similares a las de Apple Health, permitiendo crear podómetros personalizados y rastreadores de actividad.

- **Juegos con control por movimiento**: Utilizar la inclinación y rotación del dispositivo como mecanismo de entrada. Juegos de carreras donde inclinas el iPhone como un volante, o juegos de equilibrio que responden al giroscopio en tiempo real.

- **Realidad aumentada y navegación inercial**: Complementar ARKit con datos de orientación precisa del dispositivo. CoreMotion proporciona la actitud (attitude) del dispositivo, esencial para sistemas de navegación interior donde el GPS no está disponible.

- **Detección de contexto del usuario**: Reconocer automáticamente si el usuario está estático, caminando, corriendo, en bicicleta o en un vehículo. Esto permite adaptar la interfaz, notificaciones o funcionalidades según la actividad actual.

- **Aplicaciones de accesibilidad**: Crear interfaces alternativas basadas en movimiento para usuarios con necesidades específicas. Por ejemplo, detectar gestos de agitación (shake) o inclinaciones como mecanismos de interacción.

- **Instrumentos de medición**: Desarrollar niveles digitales, brújulas avanzadas, inclinómetros o herramientas de medición angular aprovechando la precisión de los sensores fusionados.

## Instalación y configuración

### Agregar el framework al proyecto

CoreMotion viene incluido en el SDK de iOS, por lo que **no requiere instalación adicional** mediante Swift Package Manager, CocoaPods ni Carthage. Simplemente necesitas importarlo en los archivos donde lo utilices:

```swift
import CoreMotion
```

### Permisos en Info.plist

CoreMotion requiere permisos específicos dependiendo de las funcionalidades que utilices:

#### Para datos de movimiento y fitness (podómetro, actividad)

Agrega la clave `NSMotionUsageDescription` en tu archivo `Info.plist`:

```xml
<key>NSMotionUsageDescription</key>
<string>Necesitamos acceder a los datos de movimiento para contar tus pasos y registrar tu actividad física.</string>
```

> **Nota importante**: Sin esta clave, tu aplicación se cerrará inmediatamente al intentar acceder a datos del podómetro o actividad del usuario en iOS 11 y posteriores.

#### Para el altímetro (cambios de presión atmosférica)

A partir de iOS 15, si usas `CMAltimeter` para datos absolutos de altitud:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para calibrar las mediciones de altitud.</string>
```

### Verificación de disponibilidad de sensores

Siempre verifica la disponibilidad antes de usar cualquier sensor:

```swift
let motionManager = CMMotionManager()

// Verificar sensores individuales
print("Acelerómetro disponible: \(motionManager.isAccelerometerAvailable)")
print("Giroscopio disponible: \(motionManager.isGyroAvailable)")
print("Magnetómetro disponible: \(motionManager.isMagnetometerAvailable)")
print("Device Motion disponible: \(motionManager.isDeviceMotionAvailable)")

// Verificar podómetro
print("Conteo de pasos disponible: \(CMPedometer.isStepCountingAvailable())")
print("Distancia disponible: \(CMPedometer.isDistanceAvailable())")
print("Conteo de pisos disponible: \(CMPedometer.isFloorCountingAvailable())")

// Verificar reconocimiento de actividad
print("Actividad disponible: \(CMMotionActivityManager.isActivityAvailable())")
```

## Conceptos clave

### 1. CMMotionManager — El punto central de acceso

`CMMotionManager` es la clase principal del framework y actúa como puerta de entrada a los datos de los sensores de movimiento. Apple recomienda enfáticamente **crear una única instancia** de esta clase por aplicación, ya que múltiples instancias pueden afectar la frecuencia de recepción de datos. Ofrece dos modalidades de acceso: **pull** (consultar datos bajo demanda) y **push** (recibir actualizaciones continuas mediante un handler).

### 2. Device Motion — Datos fusionados de sensores

`CMDeviceMotion` representa el resultado de la **fusión de sensores** (sensor fusion), combinando datos del acelerómetro, giroscopio y magnetómetro para producir mediciones más precisas y estables. Proporciona la actitud del dispositivo (orientación en el espacio 3D), la velocidad de rotación filtrada, la aceleración del usuario separada de la gravedad, y el campo magnético calibrado. Es la fuente de datos más útil para la mayoría de aplicaciones.

### 3. CMAttitude — Orientación en el espacio

`CMAttitude` describe la orientación del dispositivo relativa a un marco de referencia. Se puede expresar en múltiples formatos matemáticos: **ángulos de Euler** (roll, pitch, yaw), **cuaterniones** y **matriz de rotación**. Los cuaterniones son preferidos para cálculos continuos porque evitan el problema del *gimbal lock* que afecta a los ángulos de Euler. El marco de referencia se configura al iniciar Device Motion y puede ser relativo a la gravedad, al norte magnético o al norte verdadero.

### 4. CMPedometer — Podómetro inteligente

`CMPedometer` accede al coprocesador de movimiento para proporcionar datos de actividad ambulatoria: número de pasos, distancia estimada, pisos subidos y bajados, ritmo (cadence) y velocidad media. Puede consultar datos **históricos** almacenados (hasta 7 días) o recibir **actualizaciones en tiempo real**. El procesamiento ocurre en hardware dedicado, por lo que tiene un impacto mínimo en la batería.

### 5. CMMotionActivityManager — Reconocimiento de actividad

Esta clase utiliza algoritmos de machine learning ejecutados en el coprocesador de movimiento para clasificar automáticamente la actividad del usuario. Puede distinguir entre estados: **estacionario**, **caminando**, **corriendo**, **en bicicleta**, **en vehículo automotor** y **desconocido**. Cada resultado incluye un nivel de **confianza** (bajo, medio, alto) para que la aplicación pueda tomar decisiones informadas.

### 6. CMAltimeter — Altímetro barométrico

`CMAltimeter` proporciona datos de cambios de altitud relativos basados en el sensor de presión barométrica. A partir de iOS 15, también puede ofrecer **altitud absoluta** mediante `CMAbsoluteAltitudeData`. Es importante comprender que los datos barométricos miden cambios relativos de altitud con alta precisión, pero la altitud absoluta requiere calibración adicional.

## Ejemplo básico

```swift
import CoreMotion

// MARK: - Ejemplo básico: Lectura de datos del acelerómetro
// Este ejemplo muestra cómo obtener actualizaciones continuas del acelerómetro

class AccelerometerBasicExample {
    
    // Instancia única del motion manager (Apple recomienda solo una por app)
    private let motionManager = CMMotionManager()
    
    func iniciarLecturaAcelerometro() {
        // 1. Verificar que el acelerómetro está disponible en este dispositivo
        guard motionManager.isAccelerometerAvailable else {
            print("❌ El acelerómetro no está disponible en este dispositivo")
            return
        }
        
        // 2. Configurar el intervalo de actualización (en segundos)
        // 1/60 = ~60 Hz, suficiente para la mayoría de aplicaciones
        motionManager.accelerometerUpdateInterval = 1.0 / 60.0
        
        // 3. Iniciar actualizaciones en una cola de operaciones dedicada
        // NUNCA usar OperationQueue.main para procesamiento intensivo de sensores
        let colaSensores = OperationQueue()
        colaSensores.name = "com.miapp.acelerometro"
        colaSensores.maxConcurrentOperationCount = 1
        
        motionManager.startAccelerometerUpdates(to: colaSensores) { [weak self] datos, error in
            // 4. Verificar que no hay errores
            if let error = error {
                print("❌ Error del acelerómetro: \(error.localizedDescription)")
                self?.detenerLectura()
                return
            }
            
            // 5. Extraer los datos de aceleración
            guard let aceleracion = datos?.acceleration else { return }
            
            // Los valores están en unidades G (gravedad terrestre ≈ 9.81 m/s²)
            // x: lateral (izquierda/derecha)
            // y: longitudinal (arriba/abajo)
            // z: perpendicular a la pantalla (hacia/desde el usuario)
            let x = aceleracion.x
            let y = aceleracion.y
            let z = aceleracion.z
            
            // 6. Calcular la magnitud total de la aceleración
            let magnitud = sqrt(x * x + y * y + z * z)
            
            // En reposo, la magnitud debería ser ≈ 1.0 G (solo gravedad)
            print("📱 Aceleración - X: \(String(format: "%.3f", x)) " +
                  "Y: \(String(format: "%.3f", y)) " +
                  "Z: \(String(format: "%.3f", z)) " +
                  "Magnitud: \(String(format: "%.3f", magnitud)) G")
        }
        
        print("✅ Lectura del acelerómetro iniciada")
    }
    
    func detenerLectura() {
        // IMPORTANTE: Siempre detener las actualizaciones cuando no las necesites
        // para conservar batería
        motionManager.stopAccelerometerUpdates()
        print("🛑 Lectura del acelerómetro detenida")
    }
    
    deinit {
        detenerLectura()
    }
}
```

## Ejemplo intermedio

```swift
import CoreMotion
import Foundation

// MARK: - Ejemplo intermedio: Podómetro completo con historial y tiempo real
// Caso de uso real: pantalla de actividad diaria en una app de fitness

class PodometroManager {
    
    private let pedometer = CMPedometer()
    private let activityManager = CMMotionActivityManager()
    
    // MARK: - Datos en tiempo real
    
    /// Inicia el conteo de pasos en tiempo real desde este momento
    func iniciarConteoPasos(actualizacion: @escaping (DatosActividad) -> Void) {
        // Verificar permisos y disponibilidad
        guard CMPedometer.isStepCountingAvailable() else {
            print("❌ El conteo de pasos no está disponible")
            return
        }
        
        // Iniciar actualizaciones desde el momento actual
        pedometer.startUpdates(from: Date()) { datos, error in
            if let error = error {
                print("❌ Error del podómetro: \(error.localizedDescription)")
                return
            }
            
            guard let datos = datos else { return }
            
            // Construir modelo de datos
            let actividad = DatosActividad(
                pasos: datos.numberOfSteps.intValue,
                distanciaMetros: datos.distance?.doubleValue,
                pisosSubidos: datos.floorsAscended?.intValue,
                pisosBajados: datos.floorsDescended?.intValue,
                ritmo: datos.currentPace?.doubleValue, // segundos por metro
                cadencia: datos.currentCadence?.doubleValue, // pasos por segundo
                fechaInicio: datos.startDate,
                fechaFin: datos.endDate
            )
            
            // Despachar al hilo principal para actualizar la UI
            DispatchQueue.main.async {
                actualizacion(actividad)
            }
        }
        
        print("✅ Podómetro en tiempo real iniciado")
    }
    
    // MARK: - Consulta de datos históricos
    
    /// Obtiene los datos de actividad de hoy (desde las 00:00)
    func obtenerDatosDeHoy(completado: @escaping (Result<DatosActividad, Error>) -> Void) {
        guard CMPedometer.isStepCountingAvailable() else {
            completado(.failure(PodometroError.noDisponible))
            return
        }
        
        // Calcular el inicio del día actual
        let calendario = Calendar.current
        let inicioDelDia = calendario.startOfDay(for: Date())
        
        pedometer.queryPedometerData(from: inicioDelDia, to: Date()) { datos, error in
            DispatchQueue.main.async {
                if let error = error {
                    completado(.failure(error))
                    return
                }
                
                guard let datos = datos else {
                    completado(.failure(PodometroError.sinDatos))
                    return
                }
                
                let actividad = DatosActividad(
                    pasos: datos.numberOfSteps.intValue,
                    distanciaMetros: datos.distance?.doubleValue,
                    pisosSubidos: datos.floorsAscended?.intValue,
                    pisosBajados: datos.floorsDescended?.intValue,
                    ritmo: datos.averageActivePace?.doubleValue,
                    cadencia: nil,
                    fechaInicio: datos.startDate,
                    fechaFin: datos.endDate
                )
                
                completado(.success(actividad))
            }
        }
    }
    
    /// Obtiene el historial de pasos por hora de los últimos 7 días
    func obtenerHistorialSemanal(completado: @escaping ([DatosActividad]) -> Void) {
        let calendario = Calendar.current
        let ahora = Date