---
sidebar_position: 1
title: CryptoKit
---

# CryptoKit

## ¿Qué es CryptoKit?

CryptoKit es el framework nativo de Apple introducido en iOS 13, macOS 10.15 y watchOS 6 que proporciona una interfaz segura, moderna y de alto rendimiento para realizar operaciones criptográficas. Este framework permite a los desarrolladores ejecutar funciones de hash, autenticación de mensajes, cifrado simétrico y asimétrico, y gestión de claves sin necesidad de recurrir a bibliotecas de terceros ni a las APIs de bajo nivel de CommonCrypto o Security.framework.

CryptoKit fue diseñado con la filosofía de "seguro por defecto". A diferencia de sus predecesores, minimiza la posibilidad de errores de implementación al ofrecer APIs que manejan automáticamente aspectos críticos como la generación de nonces, el relleno (padding) y la gestión segura de memoria. Los tipos criptográficos implementan `ContiguousBytes` y liberan la memoria de manera segura cuando se desalojan, lo que reduce drásticamente la superficie de ataque.

Es la solución recomendada por Apple cuando necesitas proteger datos sensibles del usuario, verificar la integridad de información, generar firmas digitales, establecer claves compartidas mediante intercambio Diffie-Hellman, o cifrar comunicaciones entre dispositivos. Si tu aplicación maneja contraseñas, tokens, datos médicos, financieros o cualquier información confidencial, CryptoKit debe ser una pieza fundamental de tu arquitectura de seguridad.

## Casos de uso principales

- **Hashing de contraseñas y datos sensibles**: Generar resúmenes (digests) de contraseñas, archivos o datos arbitrarios utilizando SHA-256, SHA-384 o SHA-512 para verificar integridad sin almacenar la información original.

- **Cifrado simétrico de datos locales**: Proteger información almacenada en disco (bases de datos, archivos de configuración, tokens de sesión) utilizando AES-GCM o ChaChaPoly, garantizando confidencialidad y autenticidad simultáneamente.

- **Firmas digitales**: Firmar y verificar datos con curvas elípticas (P-256, P-384, P-521 y Curve25519) para asegurar la autenticidad e integridad de mensajes, transacciones o documentos.

- **Intercambio seguro de claves**: Implementar el protocolo Diffie-Hellman sobre curvas elípticas (ECDH) para establecer secretos compartidos entre dos partes sin transmitir la clave directamente.

- **Autenticación de mensajes (HMAC)**: Generar y verificar códigos de autenticación de mensajes basados en hash para garantizar que los datos no han sido alterados durante la transmisión.

- **Integración con el Secure Enclave**: Generar y utilizar claves que nunca abandonan el hardware seguro del dispositivo, proporcionando el nivel más alto de protección para operaciones de firma digital.

## Instalación y configuración

CryptoKit es un framework nativo de Apple, por lo que **no requiere instalación adicional** mediante gestores de dependencias como Swift Package Manager, CocoaPods ni Carthage. Viene incluido en el SDK de las plataformas Apple.

### Plataformas compatibles

| Plataforma | Versión mínima |
|---|---|
| iOS | 13.0+ |
| macOS | 10.15+ |
| watchOS | 6.0+ |
| tvOS | 13.0+ |
| Mac Catalyst | 13.0+ |
| visionOS | 1.0+ |

### Import necesario

```swift
import CryptoKit
```

### Permisos en Info.plist

CryptoKit **no requiere permisos especiales** en el archivo `Info.plist` para operaciones criptográficas estándar. Sin embargo, si planeas utilizar el **Secure Enclave**, necesitas:

1. Habilitar la capacidad **Keychain Sharing** en tu target.
2. Configurar un grupo de acceso al Keychain si compartes claves entre aplicaciones.

```xml
<!-- Solo si usas Keychain Sharing para Secure Enclave -->
<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)com.tuempresa.tuapp</string>
</array>
```

### Consideración para exportación

Si distribuyes tu aplicación fuera de Estados Unidos, recuerda que el uso de criptografía puede requerir declarar el cumplimiento de regulaciones de exportación en App Store Connect. Apple simplifica este proceso, pero debes verificar las preguntas sobre cifrado al enviar tu build.

## Conceptos clave

### 1. Funciones Hash (Digest)

Las funciones hash transforman datos de tamaño arbitrario en un resumen de tamaño fijo. CryptoKit soporta tres variantes de SHA-2: `SHA256`, `SHA384` y `SHA512`. Son funciones unidireccionales: no es posible recuperar los datos originales a partir del hash. Se utilizan para verificar integridad de datos, comparar archivos, y como base para otras operaciones criptográficas.

### 2. Cifrado Autenticado (Authenticated Encryption)

CryptoKit ofrece dos algoritmos de cifrado autenticado con datos asociados (AEAD): **AES-GCM** (Advanced Encryption Standard - Galois/Counter Mode) y **ChaChaPoly** (ChaCha20-Poly1305). Ambos proporcionan confidencialidad y autenticidad en una sola operación. El resultado es un `SealedBox` que contiene el texto cifrado, el nonce (valor único que previene ataques de repetición) y el tag de autenticación.

### 3. Criptografía de Curva Elíptica (ECC)

CryptoKit implementa cuatro curvas elípticas para operaciones asimétricas: **P256** (secp256r1), **P384** (secp384r1), **P521** (secp521r1) y **Curve25519**. Cada curva ofrece tipos específicos para firma (`Signing`), intercambio de claves (`KeyAgreement`) y, en el caso de Curve25519, cifrado. Las claves privadas generan automáticamente su clave pública correspondiente.

### 4. HMAC (Hash-based Message Authentication Code)

HMAC combina una función hash con una clave secreta para producir un código de autenticación. A diferencia de un simple hash, un HMAC garantiza tanto la integridad como la autenticidad del mensaje, ya que solo quien posee la clave secreta puede generar o verificar el código. Es fundamental en la verificación de webhooks, APIs y comunicaciones cliente-servidor.

### 5. Secure Enclave

El Secure Enclave es un coprocesador hardware presente en dispositivos Apple modernos (iPhone con Touch ID/Face ID, Mac con chip T2/Apple Silicon). CryptoKit permite generar claves `P256` directamente en el Secure Enclave. Estas claves **nunca abandonan el hardware seguro**: las operaciones de firma se ejecutan dentro del enclave y solo se devuelve el resultado. Esto ofrece protección incluso si el sistema operativo está comprometido.

### 6. SymmetricKey

`SymmetricKey` es el tipo fundamental para operaciones de cifrado simétrico y HMAC. Puede generarse aleatoriamente con un tamaño específico (128, 192 o 256 bits) o derivarse a partir de datos existentes. CryptoKit gestiona su memoria de forma segura, limpiándola al desalocar, para prevenir que los datos de la clave persistan en la memoria del proceso.

## Ejemplo básico

```swift
import CryptoKit
import Foundation

// =============================================================
// EJEMPLO BÁSICO: Hashing y verificación de integridad de datos
// =============================================================

// 1. Crear un hash SHA-256 de una cadena de texto
let mensaje = "Hola, CryptoKit!"
let datosDelMensaje = Data(mensaje.utf8)

let hash = SHA256.hash(data: datosDelMensaje)

// El hash es un Digest que puede representarse como cadena hexadecimal
let hashString = hash.compactMap { String(format: "%02x", $0) }.joined()
print("SHA-256: \(hashString)")
// Ejemplo de salida: "a1b2c3d4e5f6..."

// 2. Verificar integridad comparando dos hashes
let mensajeOriginal = "Datos sensibles del usuario"
let mensajeRecibido = "Datos sensibles del usuario"

let hashOriginal = SHA256.hash(data: Data(mensajeOriginal.utf8))
let hashRecibido = SHA256.hash(data: Data(mensajeRecibido.utf8))

// Comparación segura contra ataques de timing
if hashOriginal == hashRecibido {
    print("✅ Los datos no han sido modificados")
} else {
    print("❌ Los datos han sido alterados")
}

// 3. Generar un HMAC para autenticar un mensaje
let claveSecreta = SymmetricKey(size: .bits256)
let hmac = HMAC<SHA256>.authenticationCode(
    for: datosDelMensaje,
    using: claveSecreta
)

print("HMAC: \(Data(hmac).base64EncodedString())")

// 4. Verificar el HMAC
let esValido = HMAC<SHA256>.isValidAuthenticationCode(
    hmac,
    authenticating: datosDelMensaje,
    using: claveSecreta
)

print("HMAC válido: \(esValido)") // true
```

## Ejemplo intermedio

```swift
import CryptoKit
import Foundation

// =========================================================
// EJEMPLO INTERMEDIO: Cifrado/descifrado de datos sensibles
// y firma digital con curvas elípticas
// =========================================================

// MARK: - Servicio de cifrado simétrico

/// Gestor de cifrado para proteger datos en reposo (almacenamiento local)
struct CifradoService {
    
    private let clave: SymmetricKey
    
    init(clave: SymmetricKey = SymmetricKey(size: .bits256)) {
        self.clave = clave
    }
    
    /// Cifra datos utilizando AES-GCM (cifrado autenticado)
    /// - Parameter datos: Los datos en claro a cifrar
    /// - Returns: Los datos cifrados como `AES.GCM.SealedBox` serializado
    func cifrar(_ datos: Data) throws -> Data {
        // AES-GCM genera automáticamente un nonce único por operación
        let sealedBox = try AES.GCM.seal(datos, using: clave)
        
        // combined incluye: nonce + texto cifrado + tag de autenticación
        guard let datosCombinados = sealedBox.combined else {
            throw CifradoError.errorAlCifrar
        }
        
        return datosCombinados
    }
    
    /// Descifra datos previamente cifrados con AES-GCM
    /// - Parameter datosCifrados: Los datos cifrados (nonce + ciphertext + tag)
    /// - Returns: Los datos originales en claro
    func descifrar(_ datosCifrados: Data) throws -> Data {
        // Reconstruir el SealedBox a partir de los datos combinados
        let sealedBox = try AES.GCM.SealedBox(combined: datosCifrados)
        
        // open() verifica el tag de autenticación antes de descifrar
        let datosDescifrados = try AES.GCM.open(sealedBox, using: clave)
        
        return datosDescifrados
    }
    
    enum CifradoError: Error, LocalizedError {
        case errorAlCifrar
        case errorAlDescifrar
        
        var errorDescription: String? {
            switch self {
            case .errorAlCifrar: return "No se pudieron cifrar los datos"
            case .errorAlDescifrar: return "No se pudieron descifrar los datos"
            }
        }
    }
}

// MARK: - Servicio de firma digital

/// Gestor de firmas digitales con P256
struct FirmaDigitalService {
    
    private let clavePrivada: P256.Signing.PrivateKey
    var clavePublica: P256.Signing.PublicKey {
        clavePrivada.publicKey
    }
    
    init() {
        // Generar un nuevo par de claves P256
        self.clavePrivada = P256.Signing.PrivateKey()
    }
    
    /// Firma datos con la clave privada
    func firmar(_ datos: Data) throws -> P256.Signing.ECDSASignature {
        return try clavePrivada.signature(for: datos)
    }
    
    /// Verifica una firma utilizando la clave pública del firmante
    static func verificar(
        firma: P256.Signing.ECDSASignature,
        datos: Data,
        clavePublica: P256.Signing.PublicKey
    ) -> Bool {
        return clavePublica.isValidSignature(firma, for: datos)
    }
}

// MARK: - Uso práctico

func demostrarCifradoYFirma() {
    // --- Cifrado simétrico ---
    let servicioCifrado = CifradoService()
    
    let informacionSensible = """
    {
        "usuario": "juan.perez@email.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "saldo": 15420.50
    }
    """.data(using: .utf8)!
    
    do {
        // Cifrar
        let datosCifrados = try servicioCifrado.cifrar(informacionSensible)
        print("📦 Datos cifrados (\(datosCifrados.count) bytes): " +
              "\(datosCifrados.prefix(20).base64EncodedString())...")
        
        // Descifrar
        let datosRecuperados = try servicioCifrado.descifrar(datosCifrados)
        let textoRecuperado = String(data: datosRecuperados, encoding: .utf8)!
        print("🔓 Datos descifrados: \(textoRecuperado)")
    } catch {
        print("❌ Error en cifrado: \(error.localizedDescription)")
    }
    
    // --- Firma digital ---
    let servicioFirma = FirmaDigitalService()
    
    let documento = "Contrato de prestación de servicios v2.1".data(using: .utf8)!
    
    do {
        // Firmar el documento
        let firma = try servicioFirma.firmar(documento)
        print("\n✍️ Firma generada: \(firma.derRepresentation.base64EncodedString())")
        
        // Verificar la firma (cualquiera con la clave pública puede hacer esto)
        let esValida = FirmaDigitalService.verificar(
            firma: firma,
            datos: documento,
            clavePublica: servicioFirma.clavePublica
        )
        print("✅ Firma válida: \(esValida)")
        
        // Intentar verificar con datos alterados
        let documentoAlterado = "Contrato de prestación de servicios v2.2".data(using: .utf8)!
        let esValidaAlterada = FirmaDigitalService.verificar(
            firma: firma,
            datos: documentoAlterado,
            clavePublica: servicioFirma.clavePublica
        )
        print("❌ Firma con datos alterados: \(esValida