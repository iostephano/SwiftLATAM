---
sidebar_position: 1
title: Publicar App
---

# Publicar tu App en el App Store

Llegaste al momento más emocionante (y a veces más frustrante) del desarrollo iOS: **publicar tu aplicación en el App Store**. Este proceso involucra mucho más que simplemente "subir" un archivo. Requiere preparación, configuración, paciencia y conocimiento del ecosistema de Apple.

En esta guía vas a aprender cada paso necesario para llevar tu app desde Xcode hasta las manos de millones de usuarios.

---

## ¿Por qué es importante dominar este proceso?

Para un desarrollador iOS en Latinoamérica, entender el proceso de publicación es **absolutamente crítico** por varias razones:

- **Clientes y empleadores lo esperan**: No basta con saber programar. Si no puedes publicar, el proyecto no está terminado.
- **El proceso tiene costos en dólares**: La membresía del Apple Developer Program cuesta **USD $99/año**. En muchos países de LATAM esto representa una inversión significativa, así que conviene hacer las cosas bien desde el primer intento.
- **Los rechazos cuestan tiempo**: Apple puede tardar entre 24 horas y varios días en revisar tu app. Un rechazo por errores evitables puede retrasar un lanzamiento semanas.
- **Disponibilidad regional**: Puedes elegir en qué países se distribuye tu app y configurar precios en monedas locales (pesos mexicanos, pesos colombianos, reales brasileños, etc.).

---

## Requisitos previos

Antes de comenzar, asegúrate de tener lo siguiente:

| Requisito | Detalle |
|---|---|
| **Apple Developer Account** | Cuenta activa con membresía paga ($99 USD/año) |
| **Mac con Xcode** | Versión más reciente recomendada |
| **App funcional y probada** | Sin crashes, bien testeada en dispositivos reales |
| **Íconos y screenshots** | En las resoluciones requeridas por Apple |
| **Política de privacidad** | URL pública accesible (obligatoria desde 2018) |
| **App ID y Bundle Identifier** | Configurados correctamente en el portal de Apple |

---

## Paso 1: Configurar tu proyecto en Xcode

Antes de subir cualquier cosa, tu proyecto necesita estar correctamente configurado.

### Bundle Identifier

```swift
// En tu archivo de proyecto, el Bundle Identifier debe ser único
// Formato recomendado: com.tuempresa.nombreapp
// Ejemplo: com.miempresa.deliveryapp
```

En Xcode, ve a **Target → General** y verifica:

- **Display Name**: El nombre que verán los usuarios.
- **Bundle Identifier**: Debe coincidir con el registrado en App Store Connect.
- **Version**: La versión pública (ej: `1.0.0`).
- **Build**: El número de compilación (ej: `1`). Debe incrementar con cada subida.

### Configuración del esquema de firma (Signing)

```
Target → Signing & Capabilities
├── Team: Tu cuenta de desarrollador
├── Bundle Identifier: com.tuempresa.app
├── Provisioning Profile: Automatic (recomendado)
└── Signing Certificate: Apple Distribution
```

Asegúrate de seleccionar **"Automatically manage signing"** si estás empezando. Xcode se encargará de crear los certificados y perfiles de aprovisionamiento necesarios.

---

## Paso 2: Crear el App Record en App Store Connect

1. Ingresa a [App Store Connect](https://appstoreconnect.apple.com).
2. Ve a **"My Apps"** → **"+"** → **"New App"**.
3. Completa la información:

```
Plataforma: iOS
Nombre: Mi App Increíble
Idioma principal: Spanish (Mexico) / Spanish (Spain)
Bundle ID: com.tuempresa.miapp
SKU: miapp-ios-001 (identificador interno único)
Acceso: Acceso completo
```

> **💡 Tip para LATAM**: Elige "Spanish (Mexico)" como idioma principal si tu audiencia objetivo está en Latinoamérica. Puedes agregar localizaciones adicionales después.

---

## Paso 3: Preparar los metadatos de la App Store

Esta es la parte que muchos desarrolladores subestiman. Los metadatos son **tan importantes como el código** porque determinan si los usuarios van a descargar tu app.

### Información requerida

- **Nombre** (máximo 30 caracteres): Claro, memorable y con keywords relevantes.
- **Subtítulo** (máximo 30 caracteres): Complementa el nombre con tu propuesta de valor.
- **Descripción** (máximo 4000 caracteres): Explica qué hace tu app, sus funcionalidades principales y por qué el usuario debería descargarla.
- **Keywords** (máximo 100 caracteres): Palabras clave separadas por comas. Investiga qué buscan tus usuarios.
- **Categoría**: Selecciona la categoría principal y una secundaria opcional.
- **URL de política de privacidad**: Obligatoria. Puedes usar servicios gratuitos como Flycricket o crear una página simple en tu sitio web.

### Screenshots y previews

Apple requiere screenshots para diferentes tamaños de dispositivo:

| Dispositivo | Resolución |
|---|---|
| iPhone 6.7" (iPhone 15 Pro Max) | 1290 × 2796 px |
| iPhone 6.5" (iPhone 11 Pro Max) | 1284 × 2778 px |
| iPhone 5.5" (iPhone 8 Plus) | 1242 × 2208 px |
| iPad Pro 12.9" (si aplica) | 2048 × 2732 px |

> **💡 Tip**: Herramientas como **Figma**, **Canva** o **Previewed** te permiten crear mockups profesionales con marcos de dispositivo sin necesidad de ser diseñador.

---

## Paso 4: Configurar la privacidad de la app

Desde diciembre de 2020, Apple exige que declares qué datos recopila tu aplicación. Esto se muestra como las **"etiquetas de privacidad"** (App Privacy Labels) en el App Store.

Deberás responder preguntas sobre:

- **Datos de contacto** (email, nombre, teléfono)
- **Datos de ubicación**
- **Identificadores** (User ID, Device ID)
- **Datos de uso**
- **Diagnósticos** (crash logs, datos de rendimiento)

### Ejemplo práctico

Si tu app usa Firebase Analytics y requiere login con email:

```
Datos recopilados:
├── Datos de contacto: Dirección de email (vinculada al usuario)
├── Identificadores: User ID (vinculado al usuario)
├── Datos de uso: Interacción con el producto (no vinculado)
└── Diagnósticos: Datos de crashes (no vinculado)
```

Sé honesto y preciso. Las declaraciones falsas pueden resultar en el **rechazo o eliminación** de tu app.

---

## Paso 5: Crear el Archive y subir el build

### Desde Xcode

1. Selecciona **"Any iOS Device (arm64)"** como destino de compilación (no un simulador).
2. Ve a **Product → Archive**.
3. Espera a que termine la compilación.
4. Se abrirá el **Organizer** automáticamente.
5. Selecciona tu archive y haz clic en **"Distribute App"**.
6. Elige **"App Store Connect"** → **"Upload"**.
7. Sigue el asistente, dejando las opciones por defecto.

### Verificar el build en App Store Connect

Después de subir, el build pasa por un **procesamiento automático** que puede tardar entre 10 y 30 minutos. Apple realizará verificaciones básicas y te notificará por correo si hay problemas.

```swift
// Tip: Antes de hacer archive, verifica que no tengas 
// prints de debug o datos hardcodeados

#if DEBUG
print("Este mensaje NO debería aparecer en producción")
#endif

// Usa configuraciones de compilación para manejar 
// ambientes correctamente
struct AppConfig {
    static var apiBaseURL: String {
        #if DEBUG
        return "https://api-staging.miempresa.com"
        #else
        return "https://api.miempresa.com"
        #endif
    }
}
```

---

## Paso 6: Enviar a revisión

Una vez que tu build esté procesado y todos los metadatos completos:

1. En App Store Connect, ve a tu app.
2. Selecciona el build que subiste.
3. Responde las preguntas adicionales:
   - **¿La app usa criptografía?** (Si solo usas HTTPS, la respuesta es "sí" pero estás exento con la declaración de exención).
   - **¿Hay contenido para mayores de edad?**
   - **Notas para el revisor**: Aquí puedes incluir credenciales de prueba si tu app requiere login.

```
Notas para el revisor:
───────────────────────
Usuario de prueba: test@miempresa.com
Contraseña: Review2024!

La funcionalidad de pagos está en modo sandbox.
Para probar la geolocalización, usar la ubicación 
predeterminada de Ciudad de México.
```

4. Haz clic en **"Submit for Review"**.

---

## Paso 7: El proceso de revisión de Apple

### ¿Cuánto tarda?

- **Promedio**: 24-48 horas.
- **Puede extenderse**: Hasta 5-7 días en temporadas altas (noviembre-diciembre).

### Razones comunes de rechazo (y cómo evitarlas)

Estas son las causas de rechazo más frecuentes que afectan a desarrolladores en LATAM:

#### 1. Crashes y bugs

```swift
// ❌ MAL: Force unwrapping peligroso
let name = userDict["name"] as! String

// ✅ BIEN: Manejo seguro de opcionales
guard let name = userDict["name"] as? String else {
    print("No se encontró el nombre del usuario")
    return
}
```

#### 2. Metadata incompleta o engañosa

```
❌ Nombre: "La Mejor App del Mundo #1"
✅ Nombre: "MiFinanzas - Control de Gastos"
```

#### 3. Pantallas de login sin opción de registro o demo

```swift
// Si tu app requiere login, proporciona una forma de probarla
struct LoginView: View {
    var body: some View {
        VStack(spacing: 16) {
            // Campos de login...
            
            Button("Iniciar Sesión") {
                login()
            }
            
            Button("Crear Cuenta") {
                register()
            }
            
            // Apple valora que el usuario pueda 
            // explorar sin registrarse
            Button("Continuar como invitado") {
                continueAsGuest()
            }
            .foregroundColor(.secondary)
        }
    }
}
```

#### 4. Uso de APIs privadas o permisos innecesarios

```swift
// ❌ No pidas permisos que no necesitas
// Si tu app no usa la cámara, NO incluyas esto en Info.plist:
// NSCameraUsageDescription

// ✅ Solo solicita permisos cuando el usuario los necesite
func requestCameraPermission() {
    // Solicitar solo cuando el usuario toca "Tomar Foto"
    AVCaptureDevice.requestAccess(for: .video) { granted in
        DispatchQueue.main.async {
            if granted {
                self.showCamera = true
            } else {
                self.showPermissionAlert = true
            }
        }
    }
}
```

#### 5. No implementar "Sign in with Apple"

Si tu app ofrece login con redes sociales (Google, Facebook), **es obligatorio** ofrecer también "Sign in with Apple":

```swift
import AuthenticationServices

struct LoginView: View {
    var body: some View {
        VStack(spacing: 12) {
            // Otros botones de login...
            
            SignInWithAppleButton(.signIn) { request in
                request.requestedScopes = [.fullName, .email]
            } onCompletion: { result in
                switch result {
                case .success(let authorization):
                    handleAppleSignIn(authorization)
                case .failure(let error):
                    print("Error en Sign in with Apple: \(error)")
                }
            }
            .signInWithAppleButtonStyle(.black)
            .frame(height: 50)
            .cornerRadius(10)
        }
    }
    
    private func handleAppleSignIn(_ authorization: ASAuthorization) {
        guard let credential = authorization.credential 
                as? ASAuthorizationAppleIDCredential else {
            return
        }
        
        let userID = credential.user
        let email = credential.email
        let fullName = credential.fullName
        
        // Enviar al backend para crear/vincular cuenta
        AuthService.shared.loginWithApple(
            userID: userID,
            email: email,
            fullName: fullName
        )
    }
}
```

---

## Paso 8: Post-publicación

¡Tu app fue aprobada! 🎉 Pero el trabajo no termina aquí.

### Monitoreo esencial

```swift
// Implementa un sistema básico de analytics y crash reporting
// AppDelegate.swift o App.swift

import FirebaseCrashlytics

@main
struct MiApp: App {
    init() {
        FirebaseApp.configure()
        
        // Identificar usuarios para debugging
        // (sin datos personales sensibles)
        Crashlytics.crashlytics().setCustomValue(
            Locale.current.region?.identifier ?? "unknown",
            forKey: "user_region"
        )
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### Responder reseñas

En App Store Connect puedes (y deberías) responder a las reseñas de los usuarios. Esto es especialmente importante en mercados latinoamericanos donde el **trato personal** genera fidelidad.

### Actualizar regularmente

Apple favorece las apps que se mantienen actualizadas. Planifica un ciclo de actualizaciones:

```
Semana 1-2: Monitorear crashes y feedback
Semana 3-4: Parche de bugs (v1.0.1)
Mes 2-3:    Nuevas funcionalidades (v1.1.0)
Cada 3-6 meses: Actualización mayor
```

---

## Configuración de precios para LATAM

Una ventaja importante es que Apple te permite configurar **precios diferenciados** por país. En App Store Connect:

1. Ve a **"Pricing and Availability"**.
2. Selecciona los territorios donde quieres distribuir.
3. Configura el precio base y Apple calculará automáticamente los equivalentes locales.

```
Precio base: $0.99 USD
├── México: $19.00 MXN
├── Colombia: $4,500 COP (aproximado)
├── Argentina: Precio regional de Apple
├── Chile: $900 CLP (aproximado)
├── Brasil: R$5.90 BRL (aproximado)
└── Perú: S/3.90 PEN (aproximado)
```

> **⚠️ Importante**: Apple maneja los impuestos y las conversiones de moneda. Tú recibes el pago neto después de la comisión de Apple (15% para desarrolladores que ganan menos de $1M