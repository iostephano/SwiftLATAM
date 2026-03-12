---
sidebar_position: 1
title: KeychainServices
---

# KeychainServices

## ¿Qué es KeychainServices?

**Keychain Services** es el framework de Apple que proporciona un mecanismo de almacenamiento seguro y cifrado para guardar pequeñas piezas de información sensible en los dispositivos Apple. Funciona como una base de datos cifrada gestionada por el sistema operativo, donde las aplicaciones pueden almacenar contraseñas, tokens de autenticación, claves criptográficas, certificados y cualquier otro dato confidencial que no deba exponerse en texto plano. A diferencia de `UserDefaults` o archivos en disco, los datos almacenados en el Keychain están protegidos mediante cifrado a nivel de hardware y software, lo que los convierte en la opción más segura disponible en el ecosistema Apple.

El Keychain persiste incluso después de que el usuario desinstale la aplicación (en la mayoría de los casos), lo que permite recuperar credenciales cuando el usuario reinstala la app. Además, gracias a **iCloud Keychain**, los datos pueden sincronizarse de forma segura entre todos los dispositivos del usuario vinculados a su cuenta de Apple ID. Cada elemento almacenado en el Keychain puede configurarse con políticas de acceso granulares, incluyendo protección biométrica con Face ID o Touch ID.

Deberías utilizar Keychain Services siempre que necesites almacenar información sensible: credenciales de inicio de sesión, tokens OAuth, claves API, números de tarjetas, certificados digitales o cualquier secreto que tu aplicación necesite recordar de forma segura. Es el estándar de facto en el desarrollo iOS/macOS para el manejo de datos confidenciales y es ampliamente recomendado por Apple en sus guías de seguridad.

## Casos de uso principales

- **Almacenamiento de credenciales de usuario**: Guardar nombre de usuario y contraseña de forma segura después del primer inicio de sesión, evitando que el usuario deba autenticarse repetidamente.

- **Gestión de tokens de autenticación**: Almacenar tokens JWT, tokens de refresco (refresh tokens) y tokens de acceso de APIs OAuth 2.0, garantizando que no sean accesibles por otras aplicaciones ni visibles en texto plano.

- **Persistencia de claves criptográficas**: Guardar claves simétricas o asimétricas utilizadas para cifrar datos locales o comunicaciones, aprovechando la integración con el Secure Enclave del dispositivo.

- **Sincronización segura entre dispositivos**: Utilizar iCloud Keychain para que las credenciales almacenadas estén disponibles en todos los dispositivos del usuario (iPhone, iPad, Mac) sin comprometer la seguridad.

- **Protección de datos con biometría**: Configurar elementos del Keychain que solo sean accesibles tras una autenticación biométrica exitosa (Face ID / Touch ID), añadiendo una capa extra de seguridad.

- **Almacenamiento de certificados y credenciales de red**: Guardar certificados SSL/TLS del cliente y credenciales de redes Wi-Fi empresariales para autenticación automática en entornos corporativos.

## Instalación y configuración

Keychain Services forma parte del framework **Security**, que viene incluido de forma nativa en todos los sistemas operativos de Apple. No necesitas instalar ninguna dependencia externa ni usar gestores de paquetes.

### Import necesario

```swift
import Security
```

### Configuración del proyecto

No se requieren entradas especiales en `Info.plist` para el uso básico del Keychain. Sin embargo, hay configuraciones importantes según el escenario:

#### Keychain Sharing (compartir entre apps)

Si necesitas compartir datos del Keychain entre varias aplicaciones del mismo equipo de desarrollo:

1. Ve a tu target en Xcode → **Signing & Capabilities**
2. Pulsa **+ Capability** y añade **Keychain Sharing**
3. Define un **Keychain Access Group** (por ejemplo: `com.tuempresa.shared`)

#### iCloud Keychain

Para sincronización entre dispositivos mediante iCloud:

1. Añade la capability **iCloud** en tu target
2. Activa la opción **Key-value storage**
3. Utiliza el atributo `kSecAttrSynchronizable` al guardar elementos

#### Compatibilidad de plataformas

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 2.0+          |
| macOS      | 10.6+         |
| tvOS       | 9.0+          |
| watchOS    | 2.0+          |
| visionOS   | 1.0+          |

## Conceptos clave

### 1. Keychain Items (Elementos del Keychain)

Cada pieza de información almacenada en el Keychain es un **item**. Un item se compone de **datos cifrados** (el secreto en sí) y un conjunto de **atributos** que describen y permiten buscar ese elemento. Los atributos actúan como metadatos: la cuenta del usuario, el servicio asociado, etiquetas de descripción, etc.

### 2. Clases de Items (`kSecClass`)

Cada elemento del Keychain pertenece a una clase que define su naturaleza:

| Clase | Constante | Uso |
|-------|-----------|-----|
| Contraseña genérica | `kSecClassGenericPassword` | Contraseñas, tokens, cualquier dato secreto genérico |
| Contraseña de internet | `kSecClassInternetPassword` | Credenciales asociadas a un servidor/URL |
| Certificado | `kSecClassCertificate` | Certificados X.509 |
| Clave criptográfica | `kSecClassKey` | Claves públicas, privadas o simétricas |
| Identidad | `kSecClassIdentity` | Combinación de certificado + clave privada |

### 3. Operaciones CRUD

Keychain Services expone cuatro funciones C fundamentales para interactuar con el almacén:

- **`SecItemAdd`**: Añadir un nuevo elemento
- **`SecItemCopyMatching`**: Buscar y leer un elemento existente
- **`SecItemUpdate`**: Actualizar los datos o atributos de un elemento
- **`SecItemDelete`**: Eliminar un elemento

Todas retornan un `OSStatus` que indica si la operación fue exitosa o qué error ocurrió.

### 4. Queries (Diccionarios de consulta)

Todas las operaciones del Keychain se realizan mediante diccionarios `[String: Any]` (o más precisamente `CFDictionary`) que actúan como consultas. Estos diccionarios definen la clase del item, los atributos de búsqueda, los datos a almacenar y las opciones de retorno.

### 5. Access Control y políticas de accesibilidad

El atributo `kSecAttrAccessible` define **cuándo** los datos del Keychain son accesibles:

| Política | Descripción |
|----------|-------------|
| `kSecAttrAccessibleWhenUnlocked` | Solo cuando el dispositivo está desbloqueado |
| `kSecAttrAccessibleAfterFirstUnlock` | Tras el primer desbloqueo después de un reinicio |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Solo si hay código de acceso configurado, sin migración |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Desbloqueado, sin sincronización ni backup |

### 6. Keychain Access Groups

Permiten compartir elementos del Keychain entre múltiples aplicaciones del mismo equipo de desarrollo. Cada app tiene un grupo por defecto basado en su **App ID**, pero pueden definirse grupos compartidos adicionales.

## Ejemplo básico

```swift
import Security
import Foundation

// ==============================================
// EJEMPLO BÁSICO: Guardar y leer una contraseña
// ==============================================

/// Guarda una contraseña en el Keychain asociada a una cuenta y servicio
func guardarContrasena(_ contrasena: String, cuenta: String, servicio: String) -> Bool {
    // Convertimos la contraseña a Data (el Keychain trabaja con bytes)
    guard let datos = contrasena.data(using: .utf8) else { return false }
    
    // Construimos el diccionario (query) con los atributos del item
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,       // Tipo: contraseña genérica
        kSecAttrService as String: servicio,                  // Identificador del servicio
        kSecAttrAccount as String: cuenta,                    // Nombre de la cuenta/usuario
        kSecValueData as String: datos                        // Los datos secretos a guardar
    ]
    
    // Primero eliminamos cualquier item existente con los mismos atributos
    // para evitar errores de duplicado (errSecDuplicateItem)
    SecItemDelete(query as CFDictionary)
    
    // Intentamos añadir el nuevo item al Keychain
    let status = SecItemAdd(query as CFDictionary, nil)
    
    // errSecSuccess indica que la operación fue exitosa
    return status == errSecSuccess
}

/// Lee una contraseña del Keychain dada una cuenta y servicio
func leerContrasena(cuenta: String, servicio: String) -> String? {
    // Query de búsqueda
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: servicio,
        kSecAttrAccount as String: cuenta,
        kSecReturnData as String: true,           // Queremos que nos devuelva los datos
        kSecMatchLimit as String: kSecMatchLimitOne // Solo un resultado
    ]
    
    // Variable donde se almacenará el resultado
    var resultado: AnyObject?
    
    // Ejecutamos la búsqueda
    let status = SecItemCopyMatching(query as CFDictionary, &resultado)
    
    // Si fue exitosa, convertimos los datos de vuelta a String
    guard status == errSecSuccess,
          let datos = resultado as? Data,
          let contrasena = String(data: datos, encoding: .utf8) else {
        return nil
    }
    
    return contrasena
}

/// Elimina una contraseña del Keychain
func eliminarContrasena(cuenta: String, servicio: String) -> Bool {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: servicio,
        kSecAttrAccount as String: cuenta
    ]
    
    let status = SecItemDelete(query as CFDictionary)
    return status == errSecSuccess
}

// --- Uso ---
let exito = guardarContrasena("MiP@ssw0rd_Segura!", cuenta: "usuario@email.com", servicio: "com.miapp.login")
print("¿Guardado?: \(exito)") // true

if let contrasena = leerContrasena(cuenta: "usuario@email.com", servicio: "com.miapp.login") {
    print("Contraseña recuperada: \(contrasena)")
}
```

## Ejemplo intermedio

```swift
import Security
import Foundation

// =========================================================
// EJEMPLO INTERMEDIO: Wrapper genérico y tipado del Keychain
// =========================================================

/// Errores específicos del Keychain con descripciones legibles
enum KeychainError: LocalizedError {
    case duplicado
    case noEncontrado
    case errorDatos
    case errorDesconocido(OSStatus)
    
    var errorDescription: String? {
        switch self {
        case .duplicado:
            return "Ya existe un elemento con esos atributos en el Keychain."
        case .noEncontrado:
            return "No se encontró ningún elemento con esos atributos."
        case .errorDatos:
            return "Error al codificar o decodificar los datos."
        case .errorDesconocido(let status):
            return "Error del Keychain: \(status) - \(SecCopyErrorMessageString(status, nil) as String? ?? "Desconocido")"
        }
    }
}

/// Manager reutilizable para operaciones del Keychain
final class KeychainManager {
    
    /// Identificador del servicio (normalmente el Bundle ID de tu app)
    private let servicio: String
    
    /// Grupo de acceso para compartir entre apps (opcional)
    private let grupoAcceso: String?
    
    init(servicio: String = Bundle.main.bundleIdentifier ?? "com.default.keychain",
         grupoAcceso: String? = nil) {
        self.servicio = servicio
        self.grupoAcceso = grupoAcceso
    }
    
    // MARK: - Guardar
    
    /// Guarda cualquier objeto Codable en el Keychain
    func guardar<T: Codable>(_ item: T, cuenta: String) throws {
        // Codificamos el objeto a JSON
        let datos: Data
        do {
            datos = try JSONEncoder().encode(item)
        } catch {
            throw KeychainError.errorDatos
        }
        
        // Intentamos actualizar primero (por si ya existe)
        if try? leer(tipo: T.self, cuenta: cuenta) != nil {
            try actualizar(datos, cuenta: cuenta)
            return
        }
        
        // Si no existe, lo creamos
        var query = queryBase(cuenta: cuenta)
        query[kSecValueData as String] = datos
        query[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        
        let status = SecItemAdd(query as CFDictionary, nil)
        
        guard status == errSecSuccess else {
            if status == errSecDuplicateItem {
                throw KeychainError.duplicado
            }
            throw KeychainError.errorDesconocido(status)
        }
    }
    
    // MARK: - Leer
    
    /// Lee y decodifica un objeto Codable del Keychain
    func leer<T: Codable>(tipo: T.Type, cuenta: String) throws -> T {
        var query = queryBase(cuenta: cuenta)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        
        var resultado: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &resultado)
        
        guard status == errSecSuccess, let datos = resultado as? Data else {
            if status == errSecItemNotFound {
                throw KeychainError.noEncontrado
            }
            throw KeychainError.errorDesconocido(status)
        }
        
        do {
            return try JSONDecoder().decode(T.self, from: datos)
        } catch {
            throw KeychainError.errorDatos
        }
    }
    
    // MARK: - Actualizar
    
    /// Actualiza los datos de un item existente
    private func actualizar(_ datos: Data, cuenta: String) throws {
        let query = queryBase(cuenta: cuenta)
        let atributosActualizados: [String: Any] = [kSecValueData as String: datos]
        
        let status = SecItemUpdate(query as CFDictionary, atributosActualizados as CFDictionary)
        
        guard status == errSecSuccess else {
            throw KeychainError.errorDesconocido(status)
        }
    }
    
    // MARK: - Eliminar
    
    /// Elimina un item del Keychain
    @discardableResult
    func eliminar(cuenta: String) throws -> Bool {
        let query = queryBase(cuenta: cuenta)
        let status = SecItemDelete(query as CFDictionary)
        
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.errorDesconocido