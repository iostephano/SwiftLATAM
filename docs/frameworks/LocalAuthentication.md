---
sidebar_position: 1
title: LocalAuthentication
---

# LocalAuthentication

## ¿Qué es LocalAuthentication?

**LocalAuthentication** es un framework nativo de Apple que permite autenticar a los usuarios de forma local en el dispositivo mediante mecanismos biométricos (Face ID o Touch ID) o mediante el código de acceso del dispositivo (passcode). Este framework actúa como una capa de seguridad que aprovecha el hardware seguro del dispositivo (Secure Enclave) sin que los datos biométricos abandonen jamás el dispositivo ni sean accesibles para la aplicación.

El propósito principal de LocalAuthentication es ofrecer una experiencia de autenticación rápida, segura y familiar para el usuario. En lugar de solicitar contraseñas complejas cada vez que se necesita verificar la identidad, el framework permite que un simple vistazo a la cámara (Face ID) o una huella dactilar (Touch ID) sean suficientes para desbloquear funcionalidades protegidas dentro de la aplicación.

Este framework es esencial en cualquier aplicación que maneje información sensible: aplicaciones bancarias, gestores de contraseñas, aplicaciones de salud, billeteras digitales o cualquier escenario donde se requiera confirmar que el usuario que interactúa con el dispositivo es legítimo. Su API es relativamente sencilla, pero comprender sus matices — políticas de evaluación, manejo de errores, fallbacks y reutilización de contextos — es fundamental para implementar una autenticación robusta y una experiencia de usuario impecable.

## Casos de uso principales

- **Desbloqueo de aplicaciones sensibles**: Bancos, apps de inversión y billeteras digitales que requieren verificación de identidad al abrir la aplicación o tras un período de inactividad.

- **Autorización de transacciones críticas**: Confirmar transferencias bancarias, compras in-app o cambios de configuración importantes mediante biometría antes de ejecutar la operación.

- **Acceso a datos protegidos**: Desbloquear secciones específicas de la app que contienen información confidencial, como notas privadas, fotos ocultas, historiales médicos o documentos legales.

- **Autologin seguro**: Recuperar credenciales almacenadas en el Keychain protegidas con biometría para iniciar sesión automáticamente sin que el usuario escriba su contraseña.

- **Firma y aprobación de documentos**: Verificar la identidad del usuario antes de firmar digitalmente un contrato o aprobar un flujo de trabajo empresarial.

- **Protección de funcionalidades administrativas**: En aplicaciones empresariales o de gestión, restringir el acceso a paneles de administración, configuración avanzada o datos de otros usuarios.

## Instalación y configuración

### Agregar el framework al proyecto

LocalAuthentication viene incluido en el SDK de iOS, macOS, watchOS y tvOS. No es necesario instalar dependencias externas ni usar gestores de paquetes.

**En Xcode:**

1. Selecciona tu proyecto en el navegador de archivos.
2. Ve a la pestaña **General** del target.
3. En la sección **Frameworks, Libraries, and Embedded Content**, pulsa el botón **+**.
4. Busca `LocalAuthentication.framework` y agrégalo.

> **Nota:** En proyectos modernos con Swift Package Manager o que usen imports directos, Xcode enlaza automáticamente el framework al detectar el `import`. No obstante, añadirlo explícitamente garantiza claridad en las dependencias.

### Configuración de Info.plist

Para utilizar Face ID, es **obligatorio** incluir la clave `NSFaceIDUsageDescription` en el archivo `Info.plist`. Sin esta clave, la aplicación se cerrará de forma inesperada al intentar evaluar la biometría en dispositivos con Face ID.

```xml
<key>NSFaceIDUsageDescription</key>
<string>Necesitamos Face ID para proteger el acceso a tu cuenta y datos personales.</string>
```

> **Importante:** Touch ID no requiere una clave específica en Info.plist, pero Face ID sí. Apple rechazará tu app en revisión si falta esta descripción.

### Import necesario

```swift
import LocalAuthentication
```

### Plataformas soportadas

| Plataforma | Versión mínima | Biometría disponible |
|------------|---------------|----------------------|
| iOS        | 8.0+          | Touch ID / Face ID / Optic ID |
| macOS      | 10.12.2+      | Touch ID (MacBook Pro / teclado externo) |
| watchOS    | 3.0+          | Código de acceso del reloj |
| visionOS   | 1.0+          | Optic ID |

## Conceptos clave

### 1. LAContext — El contexto de autenticación

`LAContext` es la clase central del framework. Representa una sesión de autenticación y mantiene el estado de la evaluación. Cada instancia de `LAContext` es independiente: puedes crear múltiples contextos para diferentes propósitos dentro de la misma aplicación.

```swift
let context = LAContext()
```

Un aspecto fundamental es que **un contexto autenticado exitosamente puede reutilizarse** durante un período de tiempo configurable, evitando solicitar la biometría repetidamente al usuario.

### 2. LAPolicy — Políticas de evaluación

Las políticas definen qué mecanismos de autenticación se permiten:

- **`.deviceOwnerAuthenticationWithBiometrics`**: Solo permite autenticación biométrica (Face ID / Touch ID). Si la biometría falla o no está disponible, no ofrece fallback al código del dispositivo.

- **`.deviceOwnerAuthentication`**: Permite biometría Y ofrece fallback automático al código de acceso del dispositivo. Es la opción más flexible y recomendada para la mayoría de escenarios.

### 3. canEvaluatePolicy — Verificación de disponibilidad

Antes de solicitar autenticación, **siempre** debes verificar si el dispositivo es capaz de evaluar la política deseada. Este método comprueba si el hardware biométrico existe, si hay datos biométricos enrollados y si no hay restricciones activas.

```swift
var error: NSError?
let disponible = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
```

### 4. evaluatePolicy — Ejecutar la autenticación

Este método presenta el diálogo de autenticación al usuario y devuelve el resultado de forma asíncrona. Es la llamada que efectivamente muestra la interfaz de Face ID o Touch ID.

### 5. LABiometryType — Tipo de biometría disponible

Permite identificar qué tipo de sensor biométrico tiene el dispositivo para personalizar la interfaz:

```swift
switch context.biometryType {
case .faceID:    print("Face ID disponible")
case .touchID:   print("Touch ID disponible")
case .opticID:   print("Optic ID disponible")
case .none:      print("Sin biometría")
@unknown default: print("Tipo desconocido")
}
```

### 6. touchIDAuthenticationAllowableReuseDuration — Reutilización del contexto

Esta propiedad permite configurar un período (en segundos) durante el cual una autenticación exitosa previa se considera válida, evitando solicitar la biometría repetidamente:

```swift
context.touchIDAuthenticationAllowableReuseDuration = 30 // 30 segundos
```

La constante `LATouchIDAuthenticationMaximumAllowableReuseDuration` define el máximo permitido por el sistema (actualmente 5 minutos).

## Ejemplo básico

```swift
import LocalAuthentication

/// Ejemplo básico: autenticación biométrica simple
func autenticarUsuario() {
    // 1. Crear un nuevo contexto de autenticación
    let contexto = LAContext()
    var error: NSError?
    
    // 2. Verificar si la biometría está disponible en el dispositivo
    guard contexto.canEvaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        error: &error
    ) else {
        // La biometría no está disponible
        print("Biometría no disponible: \(error?.localizedDescription ?? "Error desconocido")")
        return
    }
    
    // 3. Solicitar autenticación biométrica al usuario
    contexto.evaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        localizedReason: "Inicia sesión con tu huella o rostro"
    ) { exito, error in
        // 4. El callback se ejecuta en un hilo secundario
        DispatchQueue.main.async {
            if exito {
                print("✅ Autenticación exitosa")
                // Proceder a mostrar contenido protegido
            } else {
                print("❌ Autenticación fallida: \(error?.localizedDescription ?? "")")
            }
        }
    }
}
```

## Ejemplo intermedio

```swift
import LocalAuthentication

/// Servicio de autenticación biométrica con manejo completo de errores
final class ServicioAutenticacion {
    
    // MARK: - Tipos
    
    /// Resultado posible de la autenticación
    enum ResultadoAutenticacion {
        case exitosa
        case fallida(String)
        case biometriaNoDisponible(String)
        case canceladaPorUsuario
        case bloqueada
    }
    
    /// Información sobre la biometría del dispositivo
    struct InfoBiometria {
        let tipo: LABiometryType
        let disponible: Bool
        let nombre: String
    }
    
    // MARK: - Propiedades
    
    private var contexto: LAContext
    
    // MARK: - Inicialización
    
    init() {
        self.contexto = LAContext()
        configurarContexto()
    }
    
    // MARK: - Configuración
    
    private func configurarContexto() {
        // Texto personalizado para el botón de fallback
        contexto.localizedFallbackTitle = "Usar contraseña"
        
        // Texto para el botón de cancelar
        contexto.localizedCancelTitle = "Cancelar"
        
        // Permitir reutilización durante 60 segundos
        contexto.touchIDAuthenticationAllowableReuseDuration = 60
    }
    
    /// Renueva el contexto para una nueva sesión de autenticación
    private func renovarContexto() {
        contexto = LAContext()
        configurarContexto()
    }
    
    // MARK: - Consulta de biometría
    
    /// Obtiene información sobre la biometría disponible en el dispositivo
    func obtenerInfoBiometria() -> InfoBiometria {
        var error: NSError?
        let disponible = contexto.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        )
        
        let nombre: String
        switch contexto.biometryType {
        case .faceID:
            nombre = "Face ID"
        case .touchID:
            nombre = "Touch ID"
        case .opticID:
            nombre = "Optic ID"
        case .none:
            nombre = "No disponible"
        @unknown default:
            nombre = "Desconocido"
        }
        
        return InfoBiometria(
            tipo: contexto.biometryType,
            disponible: disponible,
            nombre: nombre
        )
    }
    
    // MARK: - Autenticación
    
    /// Ejecuta la autenticación biométrica con manejo completo de errores
    /// - Parameters:
    ///   - razon: Motivo que se muestra al usuario en el diálogo de autenticación
    ///   - permitirFallback: Si es true, permite usar el código del dispositivo como alternativa
    ///   - completar: Closure con el resultado de la autenticación
    func autenticar(
        razon: String,
        permitirFallback: Bool = true,
        completar: @escaping (ResultadoAutenticacion) -> Void
    ) {
        // Renovar el contexto para evitar reutilizar estados previos
        renovarContexto()
        
        // Elegir la política según si se permite fallback
        let politica: LAPolicy = permitirFallback
            ? .deviceOwnerAuthentication
            : .deviceOwnerAuthenticationWithBiometrics
        
        // Verificar disponibilidad
        var error: NSError?
        guard contexto.canEvaluatePolicy(politica, error: &error) else {
            let mensaje = interpretarError(error)
            DispatchQueue.main.async {
                completar(.biometriaNoDisponible(mensaje))
            }
            return
        }
        
        // Ejecutar autenticación
        contexto.evaluatePolicy(politica, localizedReason: razon) { [weak self] exito, error in
            DispatchQueue.main.async {
                if exito {
                    completar(.exitosa)
                } else {
                    let resultado = self?.procesarError(error) ?? .fallida("Error desconocido")
                    completar(resultado)
                }
            }
        }
    }
    
    // MARK: - Manejo de errores
    
    /// Procesa el error de autenticación y devuelve un resultado tipado
    private func procesarError(_ error: Error?) -> ResultadoAutenticacion {
        guard let laError = error as? LAError else {
            return .fallida(error?.localizedDescription ?? "Error desconocido")
        }
        
        switch laError.code {
        case .userCancel, .appCancel, .systemCancel:
            return .canceladaPorUsuario
            
        case .biometryLockout:
            return .bloqueada
            
        case .authenticationFailed:
            return .fallida("No se pudo verificar tu identidad. Intenta nuevamente.")
            
        case .userFallback:
            return .fallida("El usuario prefirió usar contraseña.")
            
        case .biometryNotAvailable:
            return .biometriaNoDisponible("La biometría no está disponible en este dispositivo.")
            
        case .biometryNotEnrolled:
            return .biometriaNoDisponible(
                "No hay datos biométricos registrados. Configúralos en Ajustes."
            )
            
        case .passcodeNotSet:
            return .biometriaNoDisponible(
                "No hay código de acceso configurado en el dispositivo."
            )
            
        default:
            return .fallida("Error inesperado: \(laError.localizedDescription)")
        }
    }
    
    /// Interpreta un NSError de canEvaluatePolicy en texto legible
    private func interpretarError(_ error: NSError?) -> String {
        guard let error = error else { return "Error desconocido" }
        
        switch LAError.Code(rawValue: error.code) {
        case .biometryNotAvailable:
            return "Este dispositivo no soporta autenticación biométrica."
        case .biometryNotEnrolled:
            return "No se han registrado datos biométricos. Ve a Ajustes > Face ID y código."
        case .passcodeNotSet:
            return "Debes configurar un código de acceso en el dispositivo."
        default:
            return error.localizedDescription
        }
    }
}

// MARK: - Uso del servicio

let servicio = ServicioAutenticacion()

// Consultar tipo de biometría
let info = servicio.obtenerInfoBiometria()
print("Biometría: \(info.nombre), Disponible: \(info.disponible)")

// Autenticar
servicio.autenticar(razon: "Accede a tu cuenta bancaria") { resultado in
    switch resultado {
    case .exit